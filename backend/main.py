from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("NEWSDATA_API_KEY")

print("API KEY:", API_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/news")
def get_news():
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country=us&category=technology"
    response = requests.get(url)
    return response.json()
