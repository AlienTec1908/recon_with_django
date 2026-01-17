
# 👽 AlienTec – Autonomous Recon Orchestration Framework

<p align="center">
  <img src="AlienTec_Django_Recon1.png" alt="AlienTec Live Recon Cover" width="50%" style="height: 20rem;">
</p>

**🛰️ Autonomous Recon Framework for Offensive Security**  
Hands-off scanning · Live findings · Senior-grade workflows

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Phase%201%20Live%20/%20Phase%202--3%20Dev-orange.svg)
![GitHub Stars](https://img.shields.io/github/stars/AlienTec1908/recon_with_django?style=social)

---

## 📌 Project Scope & Phases

This repository contains **Phase 1 (Live Recon Showcase)** of the AlienTec Recon Framework.

- ✅ **Phase 1:** Active Recon + Live Visualization  
- 🚧 **Phase 2:** Subroutines (~45 modules) — in development  
- 🚧 **Phase 3:** Reporting & Correlation Engine — planned  

Phase 1 is intentionally released as a **reduced showcase** to demonstrate architecture, orchestration, and real-time systems.

---

## ✨ Features

- **Autonomous Scanning:** Full recon pipeline with a single click  
- **Live Finding System:** Results appear in real time  
- **Central Orchestrator:** All modules controlled via one authority  
- **Real-time Dashboard:** HUD, progress, severity tracking  
- **Scalable Architecture:** Designed for Phase 2 & Phase 3 expansion  

---

## 🛠️ Tech Stack

- **Backend / Orchestrator:** Python, FastAPI  
- **Frontend:** Django, HTML, CSS, JavaScript  
- **Scan Tools (Phase 1):** Nmap  
- **Async Runtime:** Uvicorn, Asyncio  

---

## 🧩 Requirements 

| Area | Source | Components | Notes |
|-----|--------|------------|-------|
| 🖥️ System Tools | `install.sh` | `nmap`, `nikto`, `feroxbuster`, `curl` | Installed via system package manager |
| 📚 Wordlists | `install.sh` | `seclists` | Expected at `/usr/share/seclists` |
| 🐍 Python | `requirements.txt` | Python dependencies | Installed via `pip` (venv) |

- 🐧 Linux (recommended: Kali Linux)  
- 🐍 Python 3.11+  
- 📦 pip  
- 🌐 Network access for scanning  

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/AlienTec1908/recon_with_django.git
cd recon_with_django
````

(Optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Installation & Setup (Phase 1)

### 1. Automatic Installation (Recommended)

The repository provides an `install.sh` script that performs:

* **System checks:** root privileges & dependencies
* **Python setup:** virtual environment & requirements
* **Database:** Django migrations & static files
* **SecLists:**

  * Checks `/usr/share/seclists`
  * Installs via `apt` or clones from GitHub if missing

Run:

```bash
chmod +x install.sh
sudo ./install.sh
```

**Note:**
External tools (`nmap`, `feroxbuster`, `nikto`) are checked automatically.
Missing tools must be installed manually:

```bash
sudo apt install nmap feroxbuster nikto
```

---

### 2. Configuring Wordlists (Manual)

Wordlist paths are currently **hardcoded**.

Default path:

```text
/usr/share/seclists/
```

To use custom wordlists, edit:

```bash
nano recon_engine/scans.py
```

Locate the `SCANS_TO_RUN` variable and update the `-w` flag for Feroxbuster.

**Before (default):**

```python
{
    "id": "ferox_common",
    "name": "Feroxbuster - Common Directories",
    "command": [
        "feroxbuster",
        "-u", "{URL}",
        "-w", "/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-big.txt",
        "-k", "--json", "--silent",
        "--output", "logs/{TARGET}/ferox_common.json"
    ]
},
```

**After (custom):**

```python
{
    "id": "ferox_common",
    "name": "Feroxbuster - Custom List",
    "command": [
        "feroxbuster",
        "-u", "{URL}",
        "-w", "/home/user/my_wordlists/custom_dic.txt",
        "-k", "--json", "--silent",
        "--output", "logs/{TARGET}/ferox_common.json"
    ]
},
```

---

## 🗂️ Project Structure

```text
recon_with_django/
├── manage.py                     # Django entry point
├── engine_api.py                 # Orchestrator & API (FastAPI)
├── requirements.txt
├── recon_engine/                 # Core orchestration logic
├── recon_livesensor_project/     # Live sensor & UI bridge
├── scanner/                      # Phase 1 scan modules
├── back.index.html               # Frontend entry
└── readme.md
```

---

## 🧠 Architecture Overview (Phase 1)

* Each system is **fully isolated**
* No module directly controls another
* **Orchestrator is the only authority**
* Communication via **shared JSON state**

> **Modules do not know each other — the Orchestrator knows all.**

---

## 🚀 Running the Framework (Phase 1)

### 1. Django (UI & State)

```bash
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Responsibilities:

* UI rendering
* State visualization
* Project structure

---

### 2. Orchestrator & Scan Engine (Mandatory)

```bash
uvicorn engine_api:app --reload --port 8001
```

Starts:

* Phase-1 Orchestrator
* Scan dispatcher
* Live parser pipeline
* Progress & severity engine

---

## 🌐 Access Points

* **Frontend UI:**

  ```
  http://127.0.0.1:8000
  ```

* **Orchestrator / API:**

  ```
  http://127.0.0.1:8001
  ```

---

## 🖥️ Web GUI — How to Use (Phase 1)

### Start Services

Both services must be running:

```bash
python manage.py runserver 127.0.0.1:8000
uvicorn engine_api:app --reload --port 8001
```

Open:

```text
http://127.0.0.1:8000
```

---

### GUI Walkthrough & Screenshots

**Phase 1:**

<p align="center">
  <img src="alientec4.jpg" width="50%">
</p>

**Phase 2 Preview:**

<p align="center">
  <img src="alientec3.jpg" width="50%">
</p>

---

### Starting a Scan

1. Enter target (IP or domain)
2. Click **Start Scan**
3. No further interaction required

Example:

```text
192.168.1.10
scanme.nmap.org
```

---

### What Happens Internally

* UI sends target to Orchestrator
* Orchestrator launches Nmap
* Live findings update instantly
* HUD, OPS panel, progress update continuously

---

### Emergency Stop

* Press **Stop Scan**
* All running tasks are terminated cleanly

---

## ▶️ Operational Flow (Phase 1)

1. User enters target
2. User clicks **Start Scan**
3. Orchestrator takes control

Orchestrator actions:

* Launches `nmap_fullport`
* Parses results into live JSON
* Evaluates discovered services
* Feeds HUD & Live-Finding system
* Updates progress & severity

---

## ⚙️ Orchestration Rules

* Nmap is the **primary data source**
* HTTP scans wait for service discovery
* UDP / IPv6 may run asynchronously
* UI polls shared JSON state
* UI never starts scans directly

---

## ⚙️ Design Principles

* Modular
* Replaceable
* State-driven
* Testable
* Scalable

---

## 🗺️ Roadmap

* ✔ Phase 1 — Live Recon Showcase
* 🚧 Phase 2 — Subroutines & Advanced Scans
* 🗓 Phase 3 — Reporting & Correlation

---

## 🤝 Contributing

* Open an Issue for discussion
* Pull Requests welcome

---

## 📄 License

MIT License — see `LICENSE`

---

## ⚠️ Disclaimer

For **authorized security testing only**.

* Unauthorized scanning is illegal
* No responsibility for misuse
* Always obtain explicit permission

 
