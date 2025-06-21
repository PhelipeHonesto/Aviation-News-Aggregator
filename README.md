# osacurator

This repository contains a small FastAPI backend and a React frontend built with Vite. The backend provides two endpoints:

- `/news` – returns articles stored in `news.json`.
- `/ingest` – fetches fresh articles from the agents and stores them in `news.json`.

## Running the backend

1. Install Python dependencies from `backend/requirements.txt`.
2. Start the app with `python backend/main.py` or run with Uvicorn.

## Running the frontend

Change to the `frontend` directory and install dependencies with `npm install`. Start the development server using `npm run dev`.

