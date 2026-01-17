from fastapi import FastAPI, WebSocket, HTTPException
import asyncio
from pathlib import Path
from recon_engine.intelligence_scans import SCANS_TO_RUN, SCAN_CHECKS
from recon_engine.live_parser import parse_line
from recon_engine.scan_exceptions import check_web_scanner_conditions
import json
import socket
import ipaddress
from datetime import datetime
import re
import subprocess
import shutil
import os

app = FastAPI()

PROCESS_REGISTRY = {}

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"

OPERATIONS_ARSENAL = {
    "ftp_anon_download": {
        "cmd": ["wget", "-r", "--no-passive-ftp", "--no-directories", "ftp://anonymous:anonymous@{TARGET}"],
        "name": "FTP Download"
    },
    "smb_enum_shares": {
        "cmd": ["enum4linux", "-a", "{TARGET}"],
        "name": "SMB Enumeration"
    },
    "waf_fingerprint": {
        "cmd": ["wafw00f", "http://{TARGET}"],
        "name": "WAF Fingerprint"
    },
    "wordpress_user_enum": {
        "cmd": ["wpscan", "--url", "http://{TARGET}", "--enumerate", "u", "--no-update", "--disable-tls-checks"],
        "name": "WP User Enum"
    },
    "zone_transfer": {
        "cmd": ["dig", "axfr", "@{TARGET}", "{TARGET}"],
        "name": "DNS Zone Transfer"
    },
    "ssh_brute_check": {
        "cmd": ["nmap", "-p", "22", "--script", "ssh-auth-methods", "{TARGET}"],
        "name": "SSH Auth Methods"
    }
}

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict, websocket: WebSocket):
        message = json.dumps(data)
        if websocket.client_state.name == "CONNECTED":
            try:
                await websocket.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

async def cleanup_processes_for_websocket(websocket: WebSocket):
    scan_ids_to_remove = []
    for scan_id, data in list(PROCESS_REGISTRY.items()):
        if data["websocket"] == websocket:
            process = data["process"]
            try:
                if process.returncode is None:
                    process.terminate()
                    await asyncio.sleep(0.1)
                    if process.returncode is None:
                        process.kill()
                scan_ids_to_remove.append(scan_id)
            except ProcessLookupError:
                scan_ids_to_remove.append(scan_id)

    for scan_id in scan_ids_to_remove:
        PROCESS_REGISTRY.pop(scan_id, None)

async def get_target_info(target: str):
    info = {
        "target_ip": "N/A",
        "hostname": "N/A",
        "location": "External",
        "os_type": "Unknown",
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    loop = asyncio.get_event_loop()
    try:
        results = await loop.getaddrinfo(target, None, family=socket.AF_INET)
        ip_address_str = results[0][4][0]
        info["target_ip"] = ip_address_str
        try:
            info["hostname"] = socket.gethostbyaddr(ip_address_str)[0]
        except socket.herror:
            info["hostname"] = target
        ip_address = ipaddress.ip_address(ip_address_str)
        if ip_address.is_private or ip_address.is_loopback:
            info["location"] = "Internal"
    except socket.gaierror:
        info["hostname"] = target
        info["target_ip"] = "Resolution failed"

    if info["target_ip"] not in ["N/A", "Resolution failed"]:
        try:
            process = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "1", info["target_ip"],
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=2.0)
            if process.returncode == 0:
                ping_output = stdout.decode(errors="ignore")
                ttl_match = re.search(r"ttl=(\d+)", ping_output, re.IGNORECASE)
                if ttl_match:
                    ttl = int(ttl_match.group(1))
                    if ttl <= 64: info["os_type"] = "Linux/Unix"
                    elif ttl <= 128: info["os_type"] = "Windows"
            else:
                info["os_type"] = "Ping failed"
        except (FileNotFoundError, asyncio.TimeoutError):
            info["os_type"] = "Ping failed"
    return info

async def quick_port_check(target: str, port: int):
    try:
        conn = asyncio.open_connection(target, port)
        _, writer = await asyncio.wait_for(conn, timeout=1.5)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def run_process_stream(cmd: list, process_id: str, websocket: WebSocket, channel_id: str):
    try:
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=BASE_DIR)
    except FileNotFoundError:
        await manager.broadcast({"type": "op_output", "slug": channel_id, "line": f"Error: Command {cmd[0]} not found."}, websocket)
        return

    PROCESS_REGISTRY[process_id] = {"process": process, "websocket": websocket}
    
    target = "unknown"
    for arg in cmd:
        if arg != "wget" and arg != "nmap" and "." in arg:
             target = arg.replace("http://", "").replace("https://", "").split("/")[0].split("@")[-1]
             break
    
    log_file_path = LOGS_DIR / target / f"{channel_id}.log"
    if not log_file_path.parent.exists(): log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Standard open with line buffering (1) instead of aiofiles
    with open(log_file_path, "a", buffering=1) as log_file:
        async def stream(stream_pipe):
            async for line in stream_pipe:
                decoded = line.decode(errors='ignore').strip()
                if decoded:
                    log_file.write(decoded + "\n")
                    await manager.broadcast({"type": "op_output", "slug": channel_id, "line": decoded}, websocket)
        
        await asyncio.gather(stream(process.stdout), stream(process.stderr))
    
    await process.wait()
    PROCESS_REGISTRY.pop(process_id, None)
    await manager.broadcast({"type": "op_status", "slug": channel_id, "status": "completed"}, websocket)

async def run_scan_instance(cmd: list, scan_id: str, sub_scan_id: str, scan_name_slug: str, scan_display_name: str, websocket: WebSocket, port_state_map: dict):
    process_id = sub_scan_id
    try:
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=BASE_DIR)
    except FileNotFoundError:
        details = f"Command '{cmd[0]}' not found."
        await manager.broadcast({"type": "output", "scan_id": scan_id, "sub_scan_id": sub_scan_id, "scan_name": scan_name_slug, "line": f"--- ERROR: {details} ---"}, websocket)
        return

    target = scan_id.split("_")[0] 
    log_file_path = LOGS_DIR / target / f"{sub_scan_id}.log"
    
    PROCESS_REGISTRY[process_id] = {"process": process, "websocket": websocket}
    
    try:
        if not log_file_path.parent.exists():
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Standard open with line buffering (1)
        with open(log_file_path, "w", buffering=1) as log_file:
            async def stream(stream_pipe):
                if stream_pipe:
                    async for line in stream_pipe:
                        decoded_line = line.decode(errors='ignore').strip()
                        if not decoded_line: continue
                        
                        log_file.write(decoded_line + "\n")
                        
                        await manager.broadcast({"type": "output", "scan_id": scan_name_slug, "sub_scan_id": sub_scan_id, "line": decoded_line}, websocket)
                        findings = parse_line(scan_name_slug, decoded_line, port_state_map)
                        if findings:
                            for f in findings: await manager.broadcast(f, websocket)
            await asyncio.gather(stream(process.stdout), stream(process.stderr))
            await process.wait()
    finally:
        PROCESS_REGISTRY.pop(process_id, None)

async def run_single_scan(scan: dict, target: str, websocket: WebSocket, port_state_map: dict, nmap_done_event: asyncio.Event):
    scan_id_group = f"{target}_{scan['id']}"
    scan_name = scan['name']
    scan_name_slug = scan['id']
    await manager.broadcast({"type": "status", "scan_id": scan_id_group, "scan_name": scan_name_slug, "scan_display_name": scan_name, "line": f"--- Starting {scan_name} ---"}, websocket)
    
    if scan_name in SCAN_CHECKS:
        started_fast_ports = set()
        
        # Async Fast Check
        fast_tasks = []
        
        if await quick_port_check(target, 80):
            sub_id = f"{scan_name_slug}_http_80"
            started_fast_ports.add(80)
            await manager.broadcast({"type": "prepare_sub_scan", "scan_name": scan_name_slug, "sub_scan_id": sub_id, "sub_scan_name": "80 (Fast)"}, websocket)
            cmd = [p.replace("{URL}", f"http://{target}").replace("{TARGET}", target) for p in scan["command"]]
            fast_tasks.append(asyncio.create_task(run_scan_instance(cmd, scan_id_group, sub_id, scan_name_slug, scan_name, websocket, port_state_map)))

        if await quick_port_check(target, 443):
            sub_id = f"{scan_name_slug}_https_443"
            started_fast_ports.add(443)
            await manager.broadcast({"type": "prepare_sub_scan", "scan_name": scan_name_slug, "sub_scan_id": sub_id, "sub_scan_name": "443 (Fast)"}, websocket)
            cmd = [p.replace("{URL}", f"https://{target}").replace("{TARGET}", target) for p in scan["command"]]
            fast_tasks.append(asyncio.create_task(run_scan_instance(cmd, scan_id_group, sub_id, scan_name_slug, scan_name, websocket, port_state_map)))
        
        await nmap_done_event.wait()
        
        web_targets = check_web_scanner_conditions(port_state_map)
        deep_tasks = []
        
        for proto, port in web_targets:
            if port in started_fast_ports:
                continue
                
            url = f"{proto}://{target}" if (proto == "http" and port == 80) or (proto == "https" and port == 443) else f"{proto}://{target}:{port}"
            sub_scan_id = f"{scan_name_slug}_{proto}_{port}"
            sub_scan_name = f"{port}"
            
            await manager.broadcast({"type": "prepare_sub_scan", "scan_name": scan_name_slug, "sub_scan_id": sub_scan_id, "sub_scan_name": sub_scan_name}, websocket)
            cmd = [p.replace("{URL}", url).replace("{TARGET}", target) for p in scan["command"]]
            deep_tasks.append(asyncio.create_task(run_scan_instance(cmd, scan_id_group, sub_scan_id, scan_name_slug, scan_name, websocket, port_state_map)))
            
        all_tasks = fast_tasks + deep_tasks
        if all_tasks:
            await asyncio.gather(*all_tasks)
        elif not started_fast_ports:
            sub_scan_id = f"{scan_name_slug}_skipped"
            await manager.broadcast({"type": "prepare_sub_scan", "scan_name": scan_name_slug, "sub_scan_id": sub_scan_id, "sub_scan_name": "Skipped"}, websocket)
            await manager.broadcast({"type": "output", "scan_name": scan_name_slug, "sub_scan_id": sub_scan_id, "line": "No open web ports found."}, websocket)

    else:
        sub_scan_id = scan_name_slug
        await manager.broadcast({"type": "prepare_sub_scan", "scan_name": scan_name_slug, "sub_scan_id": sub_scan_id, "sub_scan_name": "Default"}, websocket)
        cmd = [p.replace("{TARGET}", target) for p in scan["command"]]
        await run_scan_instance(cmd, scan_id_group, sub_scan_id, scan_name_slug, scan_name, websocket, port_state_map)
    
    await manager.broadcast({"type": "status", "scan_id": scan_id_group, "scan_name": scan_name_slug, "line": "--- Completed ---"}, websocket)
    if "Nmap Full Scan" in scan_name:
        nmap_done_event.set()

async def run_all_scans(target: str, websocket: WebSocket):
    target_log_dir = LOGS_DIR / target
    target_log_dir.mkdir(parents=True, exist_ok=True)
    target_info = await get_target_info(target)
    await manager.broadcast({"type": "target_info", "data": target_info}, websocket)
    port_state_map = {}
    nmap_done_event = asyncio.Event()

    scan_tasks = [asyncio.create_task(run_single_scan(scan, target, websocket, port_state_map, nmap_done_event)) for scan in SCANS_TO_RUN]
    
    await asyncio.gather(*scan_tasks)
    await manager.broadcast({"type": "intelligence_phase_complete"}, websocket)

async def execute_operation(slug: str, target: str, websocket: WebSocket):
    if slug not in OPERATIONS_ARSENAL:
        await manager.broadcast({"type": "op_output", "slug": slug, "line": "Error: Unknown Operation"}, websocket)
        return

    op_def = OPERATIONS_ARSENAL[slug]
    cmd = [p.replace("{TARGET}", target) for p in op_def["cmd"]]
    process_id = f"op_{slug}_{target}"
    
    await manager.broadcast({"type": "op_status", "slug": slug, "status": "running"}, websocket)
    await manager.broadcast({"type": "op_output", "slug": slug, "line": f"--- Executing: {' '.join(cmd)} ---"}, websocket)
    
    asyncio.create_task(run_process_stream(cmd, process_id, websocket, slug))

@app.post("/api/scans/stop_all")
async def stop_all_scans():
    for proc_id, data in list(PROCESS_REGISTRY.items()):
        process = data["process"]
        try:
            if process.returncode is None: process.terminate()
        except ProcessLookupError: pass
    await asyncio.sleep(0.2)
    for proc_id, data in list(PROCESS_REGISTRY.items()):
        process = data["process"]
        try:
            if process.returncode is None: process.kill()
        except ProcessLookupError: pass
    PROCESS_REGISTRY.clear()
    return {"status": "success", "message": "All scans terminated."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                command = message.get("command")
                target = message.get("target")

                if command == "start_scan" and target:
                    await cleanup_processes_for_websocket(websocket)
                    asyncio.create_task(run_all_scans(target, websocket))
                
                elif command == "start_operation" and target:
                    slug = message.get("slug")
                    if slug:
                        asyncio.create_task(execute_operation(slug, target, websocket))

            except Exception as e:
                print(f"WS Error: {e}")
                break
    finally:
        await cleanup_processes_for_websocket(websocket)
        manager.disconnect(websocket)
