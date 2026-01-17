from django.shortcuts import render
from recon_engine.intelligence_scans import SCANS_TO_RUN

def index(request):
    hostname = request.get_host().split(':')[0]
    websocket_url = f"ws://{hostname}:8001/ws"
    total_scans = len(SCANS_TO_RUN)
    context = {
        'total_scans': total_scans,
        'websocket_url': websocket_url
    }
    return render(request, 'scanner/index.html', context)

def operations(request):
    context = {}
    return render(request, 'scanner/operations.html', context)
