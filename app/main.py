from fastapi import FastAPI
from . import models
from .database import engine
from .routes import users, footprints, suggestions

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(footprints.router, prefix="/footprints", tags=["footprints"])
app.include_router(suggestions.router, prefix="/offsets", tags=["offsets"])

@app.get("/")
def root():
    return {"message": "Backend running"}
