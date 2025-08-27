from fastapi import FastAPI
from . import models
from .database import engine
from .routes import users, footprints

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(footprints.router)

@app.get("/")
def root():
    return {"message": "Backend running"}
