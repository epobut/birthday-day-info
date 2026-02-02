import datetime as dt
from typing import Tuple

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Birthday Day Info API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Базовий набір міст (можемо розширити)
CITY_COORDS = {
    "Kyiv": (50.4501, 30.5234),
    "Lviv": (49.8397, 24.0297),
    "Kharkiv": (49.9935, 36.2304),
    "Odesa": (46.4825, 30.7233),
    "Dnipro": (48.4647, 35.0462),
}
DEFAULT_CITY = "Kyiv"


def get_coords(city: str) -> Tuple[float, float]:
    key = (city or "").strip()
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    return CITY_COORDS[DEFAULT_CITY]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/day-info")
async def day_info(
    date: str = Query(..., description="YYYY-MM-DD"),
    city: str = Query(DEFAULT_CITY),
):
    # Парсимо дату
    try:
        d = dt.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Невірний формат дати, потрібен YYYY-MM-DD")

    lat, lon = get_coords(city)

    # --- Погода: Open-Meteo historical API ---
    weather_url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={d.isoformat()}&end_date={d.isoformat()}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
    )

    # --- Восход/закат: SunriseSunset.io ---
    sun_url = f"https://api.sunrisesunset.io/json?lat={lat}&lng={lon}&date={d.isoformat()}"

    # --- Історичні події: Wikimedia "On this day" (англійською) ---
    month, day = d.month, d.day
    wiki_url = (
        "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all"
        f"/{month:02d}/{day:02d}"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        w_resp, sun_resp, wiki_resp = await client.get(weather_url), await client.get(
            sun_url
        ), await client.get(wiki_url)

    # --- Погода ---
    weather = {
        "t_min": None,
        "t_max": None,
        "precipitation": None,
        "anomaly_comment": "Немає даних про погоду для цього дня.",
    }
    if w_resp.status_code == 200:
        w = w_resp.json()
        daily = w.get("daily") or {}
        tmax = (daily.get("temperature_2m_max") or [None])[0]
        tmin = (daily.get("temperature_2m_min") or [None])[0]
        precip = (daily.get("precipitation_sum") or [None])[0]
        if tmax is not None or tmin is not None:
            weather["t_min"] = tmin
            weather["t_max"] = tmax
            weather["precipitation"] = precip
            weather["anomaly_comment"] = "Історичні дані погоди для цього дня завантажено."

    # --- Сонце / тривалість дня ---
    astro = {
        "sunrise": None,
        "sunset": None,
        "day_length": None,
        "moon_phase": None,
        "events": [],
    }
    if sun_resp.status_code == 200:
        s = sun_resp.json().get("results") or {}
        astro["sunrise"] = s.get("sunrise")
        astro["sunset"] = s.get("sunset")
        astro["day_length"] = s.get("day_length")

    # --- Події у світі ---
    world_events = []
    if wiki_resp.status_code == 200:
        body = wiki_resp.json()
        for section_key in ("events", "births", "deaths"):
            for item in body.get(section_key, [])[:3]:
                text = item.get("text") or (
                    item.get("pages", [{}])[0].get("normalizedtitle")
                )
                year = item.get("year")
                if text:
                    world_events.append(f"{year}: {text}" if year else text)

    fun_score = None
    if weather["t_max"] is not None or world_events:
        fun_score = min(10, 3 + len(world_events) // 2)

    return {
        "date": d.isoformat(),
        "location": city,
        "weather": weather,
        "astro": astro,
        "world_events": world_events,
        "fun_score": fun_score,
    }
