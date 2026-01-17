# 👽 AlienTec – Autonomous Recon Orchestration Framework

---

<p align="center">
  <img src="AlienTec_Django_Recon1.png" alt="AlienTec Live Recon Cover" width="50%" style="height: 20rem;">
</p>

<p align="center">
  <b>Autonomous Recon Framework for Offensive Security</b><br>
  Hands-off scanning · Live findings · Senior-grade workflows
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Status-Phase%201%20Live%20/%20Phase%202--3%20Dev-orange.svg" alt="Status">
  <img src="https://img.shields.io/github/stars/AlienTec1908/recon_with_django?style=social" alt="GitHub Stars">
</p>

---

## 🔥 AlienTec – Phase 1 (Showcase Release)

**AlienTec** is an autonomous recon framework for offensive security, built from real-world pentesting workflows.  
This repository contains **only Phase 1**, released as a **reduced showcase version** to demonstrate architecture, orchestration, and UI flow.

This is **not** the full product.

---

## 🧠 Purpose of Phase 1

Phase 1 represents the **foundation of the entire framework**:

- Target initialization (IP / scope)
- Automated recon pipeline
- Live parsing of scan outputs
- Real-time web UI updates
- Central orchestration logic

👉 Focus: **Reconnaissance, not exploitation**

---

## ⚙️ Core Architecture (Phase 1)

- **Orchestrator**
  - Central control unit
  - Starts, monitors, and sequences all scans
  - Reacts to live findings (e.g. HTTP service discovered)

- **IP Start Scan**
  - Triggers the initial scan chain
  - Produces ports, services, and base intelligence

- **Live Parser**
  - Continuously parses scan outputs
  - Writes structured JSON findings
  - Acts as a signal source for follow-up scans

- **Tab System (UI)**
  - Dynamically builds scan tabs
  - Displays only context-relevant scans
  - No useless or dead modules

- **HUD / OPS Panel**
  - Running tasks
  - Progress tracking
  - Severity overview

---

## 🚧 Project Status

### ✅ Phase 1 – **Live (this repository)**
- Fully integrated recon pipeline
- Orchestrator-driven scan logic
- Live UI with findings and tabs
- **Showcase / reduced version**

### 🛠️ Phase 2 – **In Development**
- ~45 subroutines / modules
- Deep service & web analysis
- Context-aware scan chaining
- **Not included**

### 📄 Phase 3 – **Planned**
- Reporting engine
- Structured findings
- Pentest-ready client reports
- **Not included**

---

## ⚠️ Important Notice

This repository is **not a full release** of AlienTec.

- No complete scan set
- No reporting engine
- No Phase 2 logic
- Purpose: **architecture, orchestration, and design showcase**

The reduced scope is intentional.

---

## 🧩 Design Philosophy

AlienTec follows strict principles:

- Senior-grade workflows
- No blind or noisy scanning
- Context over brute force
- Orchestration over script chaos
- Built from real pentest experience

---

## 📜 License

MIT License – see `LICENSE`.

---

## ⭐ Support

If you like the project:
- ⭐ Star the repository
- Follow ongoing development
- Phase 2 & 3 will follow once the architecture is finalized

---

**AlienTec**  
_Built from real battles, not from theory._
