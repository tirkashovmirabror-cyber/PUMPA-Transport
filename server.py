from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVER_HTML = os.path.join(BASE_DIR, "driver.html")


@app.get("/")
def home():
    return FileResponse(DRIVER_HTML)


@app.get("/driver.html")
def driver():
    return FileResponse(DRIVER_HTML)


@app.get("/health")
def health():
    return {
        "status": "online",
        "app": "PUMPA Kids Transport"
    }
