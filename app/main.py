from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import time
from dotenv import load_dotenv
from . import models
from .database import engine
from .routes import users, footprints

load_dotenv()

app = FastAPI()

news_cache = {"data": None, "expiry": 0}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://carbon-calculator-fe-pi.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router, tags=["users"])
app.include_router(footprints.router, tags=["footprints"])


@app.get("/")
def root():
    return {"message": "Backend running"}


@app.get("/api/news")
def get_news():
    current_time = time.time()

    if news_cache["data"] and current_time < news_cache["expiry"]:
        return news_cache["data"]

    api_key = os.getenv("NEWS_API_KEY")

    exclude = "dailymail.co.uk,foxnews.com,tmz.com,thesun.co.uk"

    url = (
        f"https://newsapi.org/v2/everything?q=%2B%22climate%20change%22%20OR%20"
        f"%2B%22carbon%20emissions%22%20OR%20%2B%22sustainability%22&"
        f"searchIn=title&language=en&sortBy=relevancy&excludeDomains={exclude}&"
        f"pageSize=8&apiKey={api_key}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        news_cache["data"] = data
        news_cache["expiry"] = current_time + 3600
        return data
    except Exception:

        return {"articles": []}
