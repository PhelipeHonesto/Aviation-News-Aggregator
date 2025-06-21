# OsaCurator

This repository contains a full-stack application with:

- 🧠 A **FastAPI backend** that handles news ingestion and retrieval
- 🖥️ A **React frontend** (built with Vite) that displays the news and provides UI controls

---

## 🛠️ Backend Endpoints

- `GET /news` – returns the articles stored in `backend/news.json`
- `POST /ingest` – fetches fresh articles from the agents and appends them to `news.json`

---

## 🚀 Running the Project Locally

### 1. Install Python dependencies

```bash
pip install -r backend/requirements.txt

