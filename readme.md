# AlienTec Live Recon Engine

Ein modulares, live-fähiges Reconnaissance-System mit Web-UI, das parallele Security-Scans ausführt, deren Output live darstellt und einzelne Scanner gezielt steuern kann.

## Architektur

-   **Frontend & UI:** Django
-   **Backend & Scan-Engine:** FastAPI

## Voraussetzungen

Stelle sicher, dass die folgenden Kommandozeilen-Tools auf deinem System installiert sind (vorzugsweise auf einer Kali-Linux-Umgebung):

-   `nmap`
-   `feroxbuster`
-   `nikto`
-   `curl`

**Wichtig:** Das Tool erwartet, dass sich die `seclists` unter `/usr/share/seclists/` befinden.

## Installation & Start

1.  **Repository klonen:**
    ```bash
    git clone <DEINE_GITHUB_URL_HIER>
    cd recon_with_django
    ```

2.  **Virtuelle Umgebung erstellen und aktivieren:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Datenbank migrieren:**
    ```bash
    python manage.py migrate
    ```

## Nutzung

Das System benötigt zwei laufende Server.

1.  **Terminal 1: Starte die FastAPI Scan-Engine:**
    ```bash
    uvicorn engine_api:app --host 0.0.0.0 --port 8001
    ```

2.  **Terminal 2: Starte den Django UI-Server:**
    ```bash
    python manage.py runserver
    ```

3.  **Öffne deinen Browser** und gehe zu `http://127.0.0.1:8000/`.
