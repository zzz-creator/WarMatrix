from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="WarMatrix Simulation Backend")

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Wargame simulator backend running"}