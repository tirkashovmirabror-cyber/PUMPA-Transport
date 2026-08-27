from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app=FastAPI(title="PUMPA Kids Transport")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

class Location(BaseModel):
    latitude: float
    longitude: float

class RouteStatus(BaseModel):
    status: str

location={"latitude":None,"longitude":None}
route={"status":"waiting"}

@app.get("/")
def home(): return {"app":"PUMPA Kids Transport","status":"online"}

@app.post("/driver/location")
def set_location(x:Location):
    location.update(x.model_dump()); return {"success":True,"location":location}

@app.get("/driver/location")
def get_location(): return location

@app.post("/driver/route")
def set_route(x:RouteStatus):
    route["status"]=x.status; return {"success":True,"status":route["status"]}

@app.get("/driver/route")
def get_route(): return route
