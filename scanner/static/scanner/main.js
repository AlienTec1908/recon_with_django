document.addEventListener('DOMContentLoaded', () => {
    const startScanButton = document.getElementById('start-scan-button');
    const targetInput = document.getElementById('target-input');
    const stopAllButton = document.getElementById('stop-all-button');
    let currentSessionId = document.body.dataset.sessionId || null;
    const websocketHost = document.body.dataset.websocketHost;
    let currentWs = null;

    if (startScanButton) {
        startScanButton.addEventListener('click', startScan);
    }
    if (targetInput) {
        targetInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') { e.preventDefault(); startScan(); } });
    }
    if (stopAllButton) {
        stopAllButton.addEventListener('click', stopAllScans);
    }

    if (currentSessionId) {
        restoreState(currentSessionId);
        connectWebSocket(currentSessionId);
    } else {
        resetUI();
    }

    async function startScan() {
        if (currentWs && currentWs.readyState === WebSocket.OPEN) return;
        const target = targetInput.value;
        if (!target) { alert("Please enter a target."); return; }

        resetUI();
        localStorage.removeItem('current_session_id');

        const response = await fetch("/api/start_scan/", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': '{{ csrf_token }}' },
            body: JSON.stringify({ target: target })
        });
        const data = await response.json();

        if (data.session_id) {
            currentSessionId = data.session_id;
            localStorage.setItem('current_session_id', currentSessionId);
            window.history.replaceState(null, '', `/scan/${currentSessionId}/`);
            connectWebSocket(currentSessionId);
        }
    }

    function connectWebSocket(sessionId) {
        if (currentWs && currentWs.readyState === WebSocket.OPEN) return;
        currentWs = new WebSocket(`ws://${websocketHost}/ws/scan/${sessionId}/`);
        currentWs.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // Handle WebSocket messages here
        };
        currentWs.onclose = () => {
            console.log("WebSocket closed.");
        };
    }

    async function restoreState(sessionId) {
        const response = await fetch(`/api/get_scan_data/${sessionId}/`);
        if (!response.ok) { resetUI(); return; }
        const state = await response.json();
        // Populate UI from state
    }

    function resetUI() {
        // Your full resetUI logic here
    }
    
    async function stopAllScans() {
        // Your full stopAllScans logic here
    }
});
