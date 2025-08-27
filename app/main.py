from fastapi import FastAPI
from . import models
from .database import engine
from .routes import users

app = FastAPI()

# Create tables
models.Base.metadata.create_all(bind=engine)

# Add user routes
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Backend running"}
