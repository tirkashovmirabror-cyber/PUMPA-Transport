from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path


# =========================================================
# PUMPA KIDS TRANSPORT SERVER
# =========================================================

app = FastAPI(title="PUMPA Kids Transport")


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# DRIVER HOLATI
# =========================================================

driver = {
    "online": False,
    "on_route": False,
    "latitude": None,
    "longitude": None,
    "last_update": None,
}


# =========================================================
# OTA-ONA JOYLASHUVI
# =========================================================

parent = {
    "latitude": None,
    "longitude": None,
}


# =========================================================
# XABARLAR
# =========================================================

notifications = []


# =========================================================
# GPS MODELI
# =========================================================

class Location(BaseModel):
    latitude: float
    longitude: float


# =========================================================
# MASOFANI HISOBLASH
# =========================================================

def distance_meters(lat1, lon1, lat2, lon2):

    R = 6371000

    p1 = radians(lat1)
    p2 = radians(lat2)

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(p1)
        * cos(p2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c


# =========================================================
# DRIVER.HTML
# =========================================================

@app.get("/driver.html")
def driver_page():

    file_path = Path(__file__).parent / "driver.html"

    return FileResponse(file_path)


# =========================================================
# DRIVER SAHIFASINI /driver ORQALI HAM OCHISH
# =========================================================

@app.get("/driver")
def driver_page_short():

    file_path = Path(__file__).parent / "driver.html"

    return FileResponse(file_path)


# =========================================================
# SERVER HOLATI
# =========================================================

@app.get("/")
def home():

    return {
        "app": "PUMPA Kids Transport",
        "status": "online",
        "message": "PUMPA Transport server ishlayapti"
    }


# =========================================================
# HAYDOVCHI YO‘LGA CHIQDI
# =========================================================

@app.post("/api/driver/start")
def driver_start():

    driver["online"] = True
    driver["on_route"] = True

    notifications.append({
        "type": "route_started",
        "message": "🚐 Bog‘cha avtomobili yo‘lga chiqdi. Tayyorlaning!",
        "time": datetime.now().isoformat()
    })

    return {
        "success": True,
        "message": "🚐 Yo‘lga chiqildi"
    }


# =========================================================
# HAYDOVCHI YO‘LINI TUGATDI
# =========================================================

@app.post("/api/driver/finish")
def driver_finish():

    driver["on_route"] = False

    notifications.append({
        "type": "route_finished",
        "message": "🏁 Bog‘cha avtomobili yo‘nalishni tugatdi.",
        "time": datetime.now().isoformat()
    })

    return {
        "success": True,
        "message": "🏁 Yo‘l yakunlandi"
    }


# =========================================================
# HAYDOVCHI GPS JOYLASHUVI
# =========================================================

@app.post("/api/driver/location")
def driver_location(data: Location):

    driver["latitude"] = data.latitude
    driver["longitude"] = data.longitude
    driver["last_update"] = datetime.now().isoformat()

    return {
        "success": True,
        "latitude": data.latitude,
        "longitude": data.longitude
    }


# =========================================================
# HAYDOVCHI GPSINI KO‘RISH
# =========================================================

@app.get("/api/driver/location")
def get_driver_location():

    return {
        "success": True,
        "driver": driver
    }


# =========================================================
# OTA-ONA GPS
# =========================================================

@app.post("/api/parent/location")
def parent_location(data: Location):

    parent["latitude"] = data.latitude
    parent["longitude"] = data.longitude

    return {
        "success": True,
        "message": "📍 Ota-ona joylashuvi saqlandi"
    }


# =========================================================
# OTA-ONA HOLATI
# =========================================================

@app.get("/api/parent/status")
def parent_status():

    # Haydovchi hali yo‘lga chiqmagan
    if not driver["on_route"]:

        return {
            "success": True,
            "status": "waiting",
            "driver_online": driver["online"],
            "on_route": False,
            "distance": None,
            "message": "🚐 Bog‘cha avtomobili hali yo‘lga chiqmagan."
        }


    # Haydovchining GPSi yo‘q
    if driver["latitude"] is None:

        return {
            "success": True,
            "status": "gps_waiting",
            "driver_online": True,
            "on_route": True,
            "distance": None,
            "message": "📡 Haydovchi GPSi aniqlanmoqda..."
        }


    # Ota-onaning GPSi yo‘q
    if parent["latitude"] is None:

        return {
            "success": True,
            "status": "parent_gps_waiting",
            "driver_online": True,
            "on_route": True,
            "distance": None,
            "message": "📍 Joylashuvingizni aniqlash kerak."
        }


    # Masofani hisoblash
    distance = distance_meters(
        parent["latitude"],
        parent["longitude"],
        driver["latitude"],
        driver["longitude"]
    )

    distance = round(distance)


    # =====================================================
    # 50 METR
    # =====================================================

    if distance <= 50:

        status = "arrived"

        message = (
            "🚐 BOG‘CHA AVTOMOBILI KELDI! "
            "Farzandingizni olib chiqishingiz mumkin."
        )


    # =====================================================
    # 500 METR
    # =====================================================

    elif distance <= 500:

        status = "near"

        message = (
            f"🔔 Bog‘cha avtomobili {distance} metr qoldi! "
            "Tushishga shoshiling."
        )


    # =====================================================
    # 500 METRDAN UZOQ
    # =====================================================

    else:

        status = "on_route"

        if distance >= 1000:

            km = round(distance / 1000, 1)

            message = (
                f"🚐 Avtomobil {km} km uzoqlikda."
            )

        else:

            message = (
                f"🚐 Avtomobil {distance} metr uzoqlikda."
            )


    return {
        "success": True,
        "status": status,
        "driver_online": True,
        "on_route": True,
        "distance": distance,
        "message": message,
        "driver_latitude": driver["latitude"],
        "driver_longitude": driver["longitude"]
    }


# =========================================================
# XABARLAR
# =========================================================

@app.get("/api/notifications")
def get_notifications():

    return {
        "success": True,
        "notifications": notifications[-20:]
    }


# =========================================================
# UMUMIY HOLAT
# =========================================================

@app.get("/api/status")
def status():

    return {
        "server": "online",
        "driver": driver,
        "parent": parent
    }
