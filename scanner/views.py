import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ScanSession, Finding, AvailableOperation
from recon_engine.intelligence_scans import SCANS_TO_RUN

# Pfad zum Logs Ordner bestimmen (relativ zu diesem Script)
# scanner/views.py -> ../recon_engine/logs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

def index(request):
    hostname = request.get_host().split(':')[0]
    websocket_url = f"ws://{hostname}:8001/ws"
    total_scans = len(SCANS_TO_RUN)
    
    context = {
        'total_scans': total_scans,
        'websocket_url': websocket_url,
        'session_id': request.GET.get('session_id')
    }
    return render(request, 'scanner/index.html', context)

def operations(request):
    context = {
        'session_id': request.GET.get('session_id')
    }
    return render(request, 'scanner/operations.html', context)

@csrf_exempt
def api_start_scan(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            target = data.get('target')
            info = data.get('target_info', {})
            
            session = ScanSession.objects.create(
                target=target,
                hostname=info.get('hostname'),
                ip_address=info.get('target_ip'),
                os_type=info.get('os_type'),
                location=info.get('location')
            )
            return JsonResponse({'session_id': str(session.id)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_save_finding(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            finding_data = data.get('finding')
            
            if not session_id or not finding_data:
                return JsonResponse({'error': 'Missing data'}, status=400)

            session = ScanSession.objects.get(id=session_id)
            Finding.objects.get_or_create(
                session=session,
                category=finding_data.get('category'),
                value=finding_data.get('value'),
                defaults={'severity': finding_data.get('severity', 'Info')}
            )
            return JsonResponse({'status': 'ok'})
        except ScanSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_update_progress(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            completed_steps = data.get('completed_steps')
            
            session = ScanSession.objects.get(id=session_id)
            session.completed_steps = completed_steps
            session.save()
            return JsonResponse({'status': 'updated'})
        except ScanSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_end_scan(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            session = ScanSession.objects.get(id=session_id)
            session.is_complete = True
            session.save()
            generate_operations(session)
            return JsonResponse({'status': 'ok'})
        except ScanSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        except Exception as e:
             return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def api_get_scan_state(request, session_id):
    try:
        session = ScanSession.objects.get(id=session_id)
        findings = list(session.findings.values('category', 'value', 'severity'))
        return JsonResponse({
            'target_info': {
                'hostname': session.hostname,
                'target_ip': session.ip_address,
                'os_type': session.os_type,
                'location': session.location,
                'start_time': session.start_time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'findings': findings,
            'is_complete': session.is_complete,
            'completed_steps': session.completed_steps,
            'target': session.target
        })
    except ScanSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

def api_get_scan_logs(request, session_id):
    try:
        session = ScanSession.objects.get(id=session_id)
        target_log_dir = os.path.join(LOGS_DIR, session.target)
        logs = {}
        
        if os.path.exists(target_log_dir):
            for filename in os.listdir(target_log_dir):
                if filename.endswith(".log"):
                    # key ist der filename ohne extension (z.b. 'nmap_full', 'ferox_common_http_80')
                    key = filename[:-4]
                    try:
                        with open(os.path.join(target_log_dir, filename), 'r', encoding='utf-8', errors='ignore') as f:
                            logs[key] = f.read()
                    except Exception:
                        pass
        return JsonResponse(logs)
    except ScanSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

def api_get_operations(request, session_id):
    try:
        session = ScanSession.objects.get(id=session_id)
        ops = list(session.operations.values('name', 'slug', 'description', 'category'))
        return JsonResponse({'operations': ops})
    except ScanSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

def generate_operations(session):
    findings = session.findings.all()
    ports = []
    services = []
    vulns = []
    
    for f in findings:
        if f.category == 'open_ports':
            ports.append(f.value.split('/')[0])
        elif f.category == 'services':
            services.append(f.value.lower())
        elif f.category == 'vulns':
            vulns.append(f.value.lower())
    
    rules = [
        {
            'slug': 'ftp_anon_download',
            'name': 'FTP Download',
            'desc': 'Attempt to download all files from anonymous FTP.',
            'check': lambda: '21' in ports and 'ftp' in services
        },
        {
            'slug': 'smb_enum_shares',
            'name': 'SMB Enumeration',
            'desc': 'Deep enumeration of SMB shares and permissions.',
            'check': lambda: ('445' in ports or '139' in ports)
        },
        {
            'slug': 'waf_fingerprint',
            'name': 'WAF Fingerprint',
            'desc': 'Advanced WAF detection and bypass testing.',
            'check': lambda: ('80' in ports or '443' in ports)
        },
        {
            'slug': 'wordpress_user_enum',
            'name': 'WP User Enum',
            'desc': 'Bruteforce WordPress user IDs.',
            'check': lambda: any('wp-' in v for v in vulns) or any('wordpress' in s for s in services)
        },
        {
            'slug': 'zone_transfer',
            'name': 'DNS Zone Transfer',
            'desc': 'Attempt AXFR against the nameserver.',
            'check': lambda: '53' in ports
        },
        {
            'slug': 'ssh_brute_check',
            'name': 'SSH Auth Methods',
            'desc': 'Check supported authentication methods.',
            'check': lambda: '22' in ports
        }
    ]

    for rule in rules:
        if rule['check']():
            AvailableOperation.objects.get_or_create(
                session=session,
                slug=rule['slug'],
                defaults={
                    'name': rule['name'],
                    'description': rule['desc'],
                    'category': 'Network' if rule['slug'] in ['ftp_anon_download', 'ssh_brute_check', 'zone_transfer'] else 'Web'
                }
            )
