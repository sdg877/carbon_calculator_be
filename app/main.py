# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from . import models
# from .database import engine
# from .routes import users, footprints

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# models.Base.metadata.create_all(bind=engine)

# app.include_router(users.router, tags=["users"])
# app.include_router(footprints.router, tags=["footprints"])


# @app.get("/")
# def root():
#     return {"message": "Backend running"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from . import models
from .database import engine
from .routes import users, footprints

app = FastAPI()

# Updated CORS to allow your Vercel site to talk to Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for now to stop errors
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

# NEW NEWS ROUTE
@app.get("/api/news")
def get_news():
    api_key = os.getenv("NEWS_API_KEY")
    url = (
        f"https://newsapi.org/v2/everything?q=%2B%22climate%20change%22%20OR%20"
        f"%2B%22carbon%20emissions%22%20OR%20%2B%22sustainability%22&"
        f"searchIn=title&language=en&sortBy=relevancy&pageSize=8&apiKey={api_key}"
    )
    response = requests.get(url)
    return response.json()