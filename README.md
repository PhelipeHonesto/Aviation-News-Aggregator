# 🌞 OsaCurator

**Orange Sunshine Aviation's** intelligent news curation platform designed to democratize aviation education by delivering high-quality, curated aviation news and stories.

Built with the **OSA Brand Guidelines 2025** - featuring our signature vibrant orange, clean typography, and aviation-inspired design system.

## Features

- **Automated News Ingestion:** Gathers articles from multiple sources including:
  - Newsdata.io API for aviation news
  - SkyWest News press releases
  - GroundNews aviation content
  - Institutional sources (FAA, ICAO, IATA)
- **Curation Workflow:** A simple multi-step process to select, edit, and export articles with status tracking
- **Export Functionality:** Export curated articles as markdown files for easy sharing and publishing
- **OSA Brand Design:** Built with Orange Sunshine Aviation's 2025 brand guidelines
- **Modern UI:** Clean, responsive dashboard with Swiss design principles and aviation aesthetics
- **Real-time Updates:** WebSocket support for live updates and notifications
- **Analytics Dashboard:** Track article counts, status breakdowns, and source performance
- **Mobile-First Design:** Optimized for mobile devices with intuitive swipe gestures
- **Export Functionality:** Download curated articles as markdown files for easy sharing
- **SQLite Storage:** Articles are persisted using SQLModel with SQLite and proper indexing

## Project Structure

```
osacurator/
├── backend/         # FastAPI backend
│   ├── agents/      # Modules for ingesting news
│   ├── .env         # API keys and secrets (must be created)
│   ├── main.py      # Main FastAPI application
│   ├── database.py  # SQLModel models and database helpers (SQLite)
│   └── requirements.txt
│
└── frontend/        # React/Vite frontend
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── services/
    ├── index.html
    └── package.json
```

## Getting Started

Follow these instructions to set up and run the project on your local machine.

### 1. Backend Setup

First, configure the Python backend and install its dependencies.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create the environment file:**
    The application uses a `.env` file to store API keys. Create a file named `.env` in the `backend` directory and add the following content. **Remember to replace the placeholder values with your actual keys.**

    ```
    NEWSDATA_API_KEY="your_newsdata.io_api_key"
    ```

3.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 2. Frontend Setup

Next, install the Node.js dependencies for the React frontend.

1.  **Navigate to the frontend directory:**
    ```bash
    cd ../frontend 
    ```
    *(If you are in the `backend` directory)*

2.  **Install npm dependencies:**
    ```bash
    npm install
    ```

3.  **Build the frontend for production:**
    ```bash
    npm run build
    ```

### 3. Running the Application

You will need two separate terminal windows to run both the backend and frontend servers.
Alternatively, you can start both at once using the `start_dev.sh` script in the project root:

```bash
./start_dev.sh
```

1.  **Run the Backend Server:**
    *   Open a terminal window.
    *   Navigate to the `backend` directory.
    *   Activate the virtual environment: `source venv/bin/activate`
    *   Start the FastAPI server: `uvicorn main:app --reload`
      *(If running from the project root, use `uvicorn backend.main:app --reload`)*
    *   The backend will be running at `http://localhost:8000`.

2.  **Run the Frontend Server:**
    *   Open a **new** terminal window.
    *   Navigate to the `frontend` directory.
    *   Start the Vite development server: `npm run dev`
    *   The frontend will be running at `http://localhost:5173` (or the next available port).

You can now open your web browser to the frontend URL to use the application.


### Quick Development Script

To start both the backend and frontend at once, run the helper script from the project root:

```bash
c
```

The script launches the FastAPI backend and Vite frontend concurrently. Press `Ctrl+C` to stop both servers.

### Pre-commit Hooks

This repository uses `pre-commit` to run linters and formatters automatically.
If you encounter errors when running the hooks, try upgrading `pre-commit` and
`identify`:

```bash
pip install -U pre-commit identify
```

You can bypass the hooks temporarily with `git commit --no-verify`.

## License

This project is licensed under the [MIT License](LICENSE).
