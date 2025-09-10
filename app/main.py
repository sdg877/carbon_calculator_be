from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from app.routes import users, footprints, suggestions

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router, tags=["users"])
app.include_router(footprints.router, tags=["footprints"])
app.include_router(suggestions.router, prefix="/offsets", tags=["offsets"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Backend running"}
