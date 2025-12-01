# 👁️ EIDOLON
### The Local, Evolving AI Companion

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Backend](https://img.shields.io/badge/Backend-Ollama-black?style=for-the-badge)](https://ollama.com/)
[![Memory](https://img.shields.io/badge/Memory-ChromaDB-orange?style=for-the-badge)](https://www.trychroma.com/)
[![GUI](https://img.shields.io/badge/GUI-Flet-purple?style=for-the-badge)](https://flet.dev/)

> *"Eidolon (Ancient Greek: εἴδωλον) — an image, spirit, phantom, or idealized form."*

**Eidolon** is more than just a chatbot. It is an architecture for an **autonomous, local AI agent** that resides on your hardware, possessing long-term memory and a dynamic, evolving personality. It is engineered for total privacy, zero latency, and deep personalization.

---

## 🚀 Key Features

### 🧠 Sovereign Intelligence
Runs completely **offline** powered by **Llama 3**. No API keys, no cloud subscriptions, no data leakage. Your AI belongs solely to you.

### 💾 Infinite Context (Vector Memory)
Unlike standard LLMs, Eidolon does not forget.
- **RAG Architecture:** Utilizes **ChromaDB** for persistent memory storage.
- **Semantic Search:** The agent retrieves relevant facts from past conversations based on meaning, not just keywords.

### 🎭 Poly-Persona System
The architecture supports instant context switching between distinct profiles:
- **🟢 Friend Mode:** An empathetic companion that remembers your preferences and maintains an emotional bond.
- **🔴 Hacker Mode:** A dry, technical expert equipped with specialized tools (Shell, Python, Network analysis), stripped of emotional overhead.

### 🛠️ Tool Use (Agentic Capabilities)
Eidolon can do more than just talk. The Core is capable of executing local Python functions to perform real-world tasks: from checking system status to analyzing log files.

### 🖥️ Modern Native GUI
A sleek, dark-themed interface built with **Flet (Flutter)**. No browser required — a standalone desktop application experience.

---

## 🏗️ Architecture

The project follows the modular **"Orchestrator Pattern"**:

```mermaid
graph TD
    User <--> GUI[Flet Interface]
    GUI <--> Orchestrator[Python Core]
    Orchestrator <-->|Inference| Ollama[(Llama 3 Kernel)]
    Orchestrator <-->|RAG| Memory[(ChromaDB Vector Store)]
    Orchestrator <-->|Actions| Tools[System Tools]
    Orchestrator <-->|Config| Profiles[JSON Personas]
