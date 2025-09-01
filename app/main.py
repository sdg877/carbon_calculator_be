from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routes import users, footprints, suggestions

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(footprints.router, prefix="/footprints", tags=["footprints"])
app.include_router(suggestions.router, prefix="/offsets", tags=["offsets"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, GET, OPTIONS etc.
    allow_headers=["*"],  # allow Content-Type, Authorization, etc.
)

@app.get("/")
def root():
    return {"message": "Backend running"}
