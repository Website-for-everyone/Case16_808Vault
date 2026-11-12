import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="808 Vault Sound Lab API", version="1.0.0")

# Base directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Models
class BookingRequest(BaseModel):
    client_name: str = Field(..., min_length=2)
    client_contact: str = Field(..., min_length=5)
    studio_room: str
    booking_date: str
    booking_time: str
    notes: Optional[str] = ""

class LicenseOrderRequest(BaseModel):
    client_name: str = Field(..., min_length=2)
    client_contact: str = Field(..., min_length=5)
    track_id: str
    license_type: str
    artist_pseudonym: Optional[str] = "Independent Artist"

# In-memory storage
TRACKS_DATABASE = [
    {
        "id": "trk-01",
        "title": "Sub Zero 808",
        "producer": "Idrisov Sound Lab",
        "bpm": 140,
        "key": "D Minor",
        "tags": ["Trap", "Dark", "Hard 808"],
        "price_lease": 2500,
        "price_trackout": 7000,
        "price_exclusive": 28000,
        "description": "Heavy distorted 808 slides, razor-sharp hats, and atmospheric cinematic synth.",
        "waveform_peaks": [12, 45, 80, 95, 60, 40, 75, 100, 85, 30, 65, 90, 70, 50, 80, 60, 30, 90, 75, 40]
    },
    {
        "id": "trk-02",
        "title": "Cyber Drift Phonk",
        "producer": "Idrisov Sound Lab",
        "bpm": 160,
        "key": "F# Minor",
        "tags": ["Phonk", "Drift", "Cowbell"],
        "price_lease": 3000,
        "price_trackout": 8500,
        "price_exclusive": 35000,
        "description": "Aggressive analog Memphis tape cowbells with punchy kick transients.",
        "waveform_peaks": [20, 60, 90, 100, 80, 55, 70, 95, 90, 45, 80, 85, 65, 75, 90, 55, 45, 95, 80, 60]
    },
    {
        "id": "trk-03",
        "title": "Phantom Drill",
        "producer": "Idrisov Sound Lab",
        "bpm": 142,
        "key": "C Minor",
        "tags": ["UK Drill", "Sliding 808", "Orchestral"],
        "price_lease": 2200,
        "price_trackout": 6500,
        "price_exclusive": 25000,
        "description": "Complex counter-snare patterns, haunting choir chords, and sub-bass glides.",
        "waveform_peaks": [15, 35, 70, 85, 65, 50, 80, 90, 75, 40, 70, 85, 60, 45, 75, 55, 35, 85, 70, 45]
    },
    {
        "id": "trk-04",
        "title": "Neon Syndicate",
        "producer": "Idrisov Sound Lab",
        "bpm": 128,
        "key": "A Minor",
        "tags": ["Cyberpunk", "Synthwave", "Midtempo"],
        "price_lease": 2800,
        "price_trackout": 7500,
        "price_exclusive": 30000,
        "description": "Industrial saw basslines, gated snares, and dystopian analog pads.",
        "waveform_peaks": [25, 50, 75, 85, 70, 60, 85, 90, 80, 50, 75, 80, 65, 55, 80, 65, 40, 90, 75, 50]
    }
]

LICENSES_DATABASE = [
    {
        "type": "MP3 Lease",
        "price": 1500,
        "format": "High-Quality 320kbps MP3",
        "distribution_limit": "5,000 Streams",
        "commercial_use": False,
        "stems_included": False,
        "rights": "Non-exclusive lease"
    },
    {
        "type": "WAV Lease",
        "price": 3000,
        "format": "24-bit 44.1kHz Lossless WAV",
        "distribution_limit": "50,000 Streams",
        "commercial_use": True,
        "stems_included": False,
        "rights": "Non-exclusive commercial lease"
    },
    {
        "type": "Trackout Stems",
        "price": 8500,
        "format": "24-bit Separated Audio Stems (WAV)",
        "distribution_limit": "500,000 Streams",
        "commercial_use": True,
        "stems_included": True,
        "rights": "Full mixing freedom & commercial lease"
    },
    {
        "type": "Exclusive Rights",
        "price": 35000,
        "format": "WAV + MP3 + Multi-track Stems + Contract",
        "distribution_limit": "Unlimited Streams / Broadcasts",
        "commercial_use": True,
        "stems_included": True,
        "rights": "Full ownership buyout (Removed from market)"
    }
]

BOOKINGS_LOG = []
ORDERS_LOG = []

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "808_vault_api", "version": "1.0.0"}

@app.get("/api/tracks")
def get_tracks():
    return {"status": "success", "tracks": TRACKS_DATABASE}

@app.get("/api/licenses")
def get_licenses():
    return {"status": "success", "licenses": LICENSES_DATABASE}

@app.post("/api/book-session")
def book_session(req: BookingRequest):
    booking_id = f"BK-{len(BOOKINGS_LOG) + 101}"
    record = {
        "booking_id": booking_id,
        "client_name": req.client_name,
        "client_contact": req.client_contact,
        "studio_room": req.studio_room,
        "booking_date": req.booking_date,
        "booking_time": req.booking_time,
        "notes": req.notes,
        "status": "confirmed"
    }
    BOOKINGS_LOG.append(record)
    return {
        "status": "success",
        "message": f"Студийная сессия успешно забронирована (#{booking_id})",
        "booking": record
    }

@app.post("/api/order-license")
def order_license(req: LicenseOrderRequest):
    track = next((t for t in TRACKS_DATABASE if t["id"] == req.track_id), None)
    if not track:
        raise HTTPException(status_code=404, detail="Трек не найден")
    
    order_id = f"ORD-808-{len(ORDERS_LOG) + 501}"
    record = {
        "order_id": order_id,
        "client_name": req.client_name,
        "client_contact": req.client_contact,
        "track_id": req.track_id,
        "track_title": track["title"],
        "license_type": req.license_type,
        "artist_pseudonym": req.artist_pseudonym,
        "status": "payment_pending"
    }
    ORDERS_LOG.append(record)
    return {
        "status": "success",
        "message": f"Заказ на лицензию успешно сформирован (#{order_id})",
        "order": record
    }

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>808 Vault DAW Studio</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.app:app", host="0.0.0.0", port=3016, reload=True)
