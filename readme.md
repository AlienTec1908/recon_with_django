# 👽 AlienTec – Autonomous Recon Orchestration Framework

---

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

## 🖥️ Web GUI — How to Use (Phase 1)

### 🌐 Start the Web Interface

Make sure **both services are running**:

```bash
# Django (Frontend)
python manage.py runserver 127.0.0.1:8000

# Orchestrator / Scan Engine
uvicorn engine_api:app --reload --port 8001
```

---

### 🌍 Open the GUI in Your Browser

Open your browser and navigate to:

```
http://127.0.0.1:8000
```

This loads the **AlienTec Live Recon Interface (Phase 1)**.

---
## 🖥️ GUI Walkthrough & Screenshot

📸 **Screenshot – Meltdown Web Interface**

1. Phase 1
<p align="center">
  <img src="alientec4.jpg" alt="AlienTec Live Recon Cover" width="50%" style="height: 20rem;">
</p>


2. Phase 2 

<p align="center">
  <img src="alientec3.jpg" alt="AlienTec Live Recon Cover" width="50%" style="height: 20rem;">
</p>

---
### 🎯 Starting a Scan

1. Locate the **Target Input Field** in the OPS Panel (left side)

2. Enter a **target IP address or domain name**

   Examples:

   ```
   192.168.1.10
   scanme.nmap.org
   ```

3. Click **Start Scan**

---

### ⚙️ What Happens After Clicking “Start Scan”

* The GUI sends the target to the **Phase‑1 Orchestrator**
* The orchestrator launches:

  * Nmap Full Port Scan
  * UDP / IPv6 scans (if enabled)
* Live Findings, HUD Panel, OPS Panel and Progress Bar update **in real time**
* Discovered services appear immediately in the **Live‑Finding System**
* Severity counters and task states update dynamically

No manual interaction is required after pressing **Start Scan**.

---

### 🛑 Stop Scan (Emergency)

* Press **Stop Scan** in the OPS Panel
* The orchestrator terminates all running tasks cleanly

---

## 📍 Where to Place This Section in the README

👉 **Insert this section directly AFTER:**

```
## 🚀 Running the Framework (Phase 1)
```

and **BEFORE:**

```
## ▶️ How Phase 1 Works (Operational Flow)
```

So the flow for the reader is:

1. Install
2. Start services
3. **Use the GUI**
4. Understand orchestration

---

# ⚙️ Installation & Operation — Phase 1

## 📌 Scope of This Repository

This repository currently contains **Phase 1 (Live Recon Showcase)** of the **AlienTec Django Recon Framework**.

* ✅ Phase 1: **Active Recon + Live Visualization**
* 🚧 Phase 2: **Subroutines (≈45 modules)** — *in development*
* 🚧 Phase 3: **Reporting & Correlation Engine** — *planned*

Phase 1 is intentionally released as a **reduced, showcase version** to demonstrate architecture, orchestration, and live systems.

---

## 🧩 Requirements

* 🐧 **Linux** (recommended: Kali Linux)
* 🐍 **Python 3.11+**
* 📦 `pip`
* 🌐 Network access (for scanning targets)

---

## 📦 Installation

```bash
git clone https://github.com/AlienTec1908/recon_with_django.git
cd recon_with_django
```

(Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🗂️ Relevant Project Structure

```text
recon_with_django/
├── manage.py                     # Django entry point
├── engine_api.py                 # Orchestrator & API layer (FastAPI)
├── requirements.txt
├── recon_engine/                 # Core orchestration logic
├── recon_livesensor_project/     # Live sensor & UI bridge
├── scanner/                      # Phase 1 scan modules
├── back.index.html               # Frontend entry point
└── readme.md
```

---

## 🧠 Architecture Overview (Phase 1)

Phase 1 follows a **strict modular orchestration model**:

* Every system is an **isolated module**
* No module directly controls another module
* **All coordination happens via the Phase‑1 Orchestrator**
* Communication is handled through **JSON state & output files**

Core principle:

> **Modules do not know each other — the Orchestrator knows all.**

---

## 🚀 Running the Framework (Phase 1)

### 1️⃣ Django Core (UI / Structure)

```bash
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Django is used for:

* UI integration
* State representation
* Project structure

---

### 2️⃣ Orchestrator & Scan Engine (Mandatory)

The actual scan logic is executed via **FastAPI + Uvicorn**:

```bash
uvicorn engine_api:app --reload --port 8001
```

This starts:

* 🧠 Phase‑1 Orchestrator
* 📡 Live parser pipeline
* ⚙️ Scan dispatch engine
* 📊 State & progress tracking

---

## 🌐 Access Points

* **Orchestrator / API**

  ```
  http://127.0.0.1:8001
  ```

* **Frontend (UI)**

  ```
  http://127.0.0.1:8000
  ```

---

## ▶️ How Phase 1 Works (Operational Flow)

1. User enters a target IP in the UI
2. User clicks **Start Scan**
3. The **Phase‑1 Orchestrator** takes full control

The orchestrator then:

* 🔍 launches `nmap_fullport`
* 📡 parses findings into live JSON state
* 🧠 evaluates discovered services
* 🗂️ feeds Live‑Finding & HUD systems
* 📊 updates progress & severity engines

⚠️ **Scans are never started directly by the UI.**
All execution logic lives inside the orchestrator.

---

## 🧠 Orchestration Rules (Phase 1)

* `nmap_fullport` is the **primary data source**
* HTTP‑based scans wait for Nmap service discovery
* UDP & IPv6 scans may run asynchronously
* Live‑Finding, HUD, OPS Panel poll shared JSON state
* Progress & severity are calculated continuously

---

## ⚙️ Design Principles

* 🧩 **Modular** — each system is standalone
* 🔁 **Replaceable** — modules can be swapped without refactoring others
* 📄 **State‑driven** — JSON is the single source of truth
* 🧪 **Testable** — every module can run independently
* 🚀 **Scalable** — Phase 2 & 3 plug into the same model

---

## ⚠️ Disclaimer

This project is provided **for educational and authorized security testing only**.

* Unauthorized scanning is illegal
* The author assumes **no responsibility for misuse**
* Always obtain **explicit permission** before scanning any target

---

 
