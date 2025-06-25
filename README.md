# OsaCurator

OsaCurator is a full-stack news curation web application designed to gather articles from various sources, allow for AI-powered editing, and publish them to a designated Slack channel.

## Features

- **Automated News Ingestion:** Gathers articles from web pages (SkyWest News) and external APIs (Newsdata.io).
- **Curation Workflow:** A multi-step process to select, edit, and post articles.
- **AI-Powered Editing:** Integrates with OpenAI's GPT-4o to rewrite and refine article content.
- **Slack Integration:** Posts curated articles directly to a Slack channel using webhooks.
- **Modern UI:** A clean, responsive dashboard built with React and TypeScript.

## Project Structure

```
osacurator/
├── backend/         # FastAPI backend
│   ├── agents/      # Modules for ingesting news
│   ├── .env         # API keys and secrets (must be created)
│   ├── main.py      # Main FastAPI application
│   ├── database.py  # Handles reading/writing to news.json
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
    OPENAI_API_KEY="your_openai_api_key"
    SLACK_WEBHOOK_URL="your_slack_webhook_url"
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
./dev.sh
```

The script launches the FastAPI backend and Vite frontend concurrently. Press `Ctrl+C` to stop both servers.
