import re
import json
import os
from urllib.parse import unquote
from recon_engine.severity_rules import get_severity

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0?]*[ -/]*[@-~])')

def clean(line: str) -> str:
    """Entfernt ANSI-Farbcodes und Whitespace."""
    return ANSI_ESCAPE.sub("", line).strip()

def create_finding(category, value):
    """Erstellt ein standardisiertes Finding-Objekt inklusive Severity-Check."""
    severity = get_severity(category, value)
    return {
        "type": "finding",
        "category": category,
        "value": value,
        "severity": severity
    }

def parse_line(tool_name, line, port_state_map):
    findings = []
    clean_line = clean(line)
    if not clean_line:
        return findings

    l = clean_line.lower()
    scan_id = tool_name.lower()

    # --- NMAP PARSER ---
    if "nmap" in scan_id:
        m = re.search(r'^(\d+)/(tcp|udp)\s+(open|filtered|closed)\s+(\S+)', l)
        if m:
            port = int(m.group(1))
            proto = m.group(2)
            state = m.group(3)
            service = m.group(4).strip('?')

            port_state_map[port] = {"status": state, "service": service}

            if state == "open":
                findings.append(create_finding("open_ports", f"{port}/{proto}"))
                findings.append(create_finding("services", service))
                if "http" in service:
                    findings.append(create_finding("web", service))
            if state == "filtered":
                findings.append(create_finding("filtered_ports", f"{port}/{proto}"))

    # --- CURL PARSER ---
    if "curl" in scan_id:
        if l.startswith("set-cookie:"):
            findings.append(create_finding("cookies", "cookie-found"))
        if l.startswith("server:"):
            server = clean_line.split(":", 1)[1].strip()
            findings.append(create_finding("web", server))
        if l.startswith("allow:"):
            for m in clean_line.split(":", 1)[1].split(","):
                if m.strip():
                    findings.append(create_finding("methods", m.strip().upper()))

    # --- NIKTO PARSER ---
    if "nikto" in scan_id:
        # This part might need adjustment if Nikto's JSON output is parsed differently
        if "x-frame-options header is not present" in l:
            findings.append(create_finding("vulns", "missing-x-frame-options"))
        if "x-content-type-options header is not set" in l:
            findings.append(create_finding("vulns", "missing-x-content-type-options"))
        if "directory indexing found" in l:
            findings.append(create_finding("vulns", "directory-indexing"))
        if "allowed http methods" in l:
            for m in clean_line.split(":", 1)[1].split(","):
                if m.strip():
                    findings.append(create_finding("methods", m.strip().upper()))

    # --- FEROXBUSTER PARSER (YOUR INTELLIGENT VERSION) ---
    if "ferox" in scan_id:
        if not clean_line.startswith("{"):
            return findings

        try:
            data = json.loads(clean_line)
        except json.JSONDecodeError:
            return findings

        if data.get("type") != "response":
            return findings

        status = data.get("status")
        if status not in {200, 301, 302, 403}:
            return findings

        url = data.get("url")
        if not url:
            return findings
            
        path = "/" + "/".join(part for part in unquote(url).split("/")[3:] if part)
        if not path or path == "/":
            return findings

        path_no_query = path.split('?')[0]
        _, ext = os.path.splitext(path_no_query)
        ext = ext.lower()
        
        backup_exts = {'.bak', '.old', '.zip', '.tar', '.gz', '.sql', '.db', '.7z', '.rar'}
        asset_exts = {'.jpg', '.jpeg', '.png', '.gif', '.ico', '.css', '.svg', '.woff', '.woff2', '.ttf', '.mp4', '.mpeg', '.avi'}
        script_exts = {'.js'}
        sensitive_exts = {'.txt', '.log', '.env', '.conf', '.config', '.ini', '.pdf'}

        if ext in backup_exts or "backup" in path.lower():
            findings.append(create_finding("backups", path_no_query))
        elif ext in asset_exts:
            findings.append(create_finding("assets", path_no_query))
        elif ext in script_exts:
            findings.append(create_finding("scripts", path_no_query))
        elif ext in sensitive_exts:
            findings.append(create_finding("sensitive_files", path_no_query))

        if ext:
            findings.append(create_finding("extensions", ext))
        else:
            findings.append(create_finding("endpoints", path_no_query))

    return findings
