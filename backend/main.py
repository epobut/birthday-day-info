import datetime as dt

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


@app.get("/health")
def health():
    return {"status": "ok"}


KYIV_LAT = 50.4501
KYIV_LON = 30.5234


@app.get("/day-info")
async def day_info(
    date: str = Query(..., description="YYYY-MM-DD"),
    city: str = Query("Kyiv"),
):
    try:
        d = dt.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Невірний формат дати, потрібен YYYY-MM-DD")

    # Для MVP ігноруємо city і завжди беремо Київ
    lat, lon = KYIV_LAT, KYIV_LON

    # --- Погода: Open-Meteo historical API ---
    # https://open-meteo.com
    weather_url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={d.isoformat()}&end_date={d.isoformat()}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
    )

    # --- Восход/закат: SunriseSunset.io ---
    # https://sunrisesunset.io/api/
    sun_url = (
        f"https://api.sunrisesunset.io/json?lat={lat}&lng={lon}&date={d.isoformat()}"
    )

    # --- Исторические события: Wikimedia "On this day" ---
    # https://api.wikimedia.org/wiki/API_reference/Feed/On_this_day
    month = d.month
    day = d.day
    wiki_url = (
        "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all"
        f"/{month:02d}/{day:02d}"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        w_resp, sun_resp, wiki_resp = await client.get(weather_url), await client.get(
            sun_url
        ), await client.get(wiki_url)

    # Погода
    weather = None
    if w_resp.status_code == 200:
        w = w_resp.json()
        daily = w.get("daily") or {}
        tmax = (daily.get("temperature_2m_max") or [None])[0]
        tmin = (daily.get("temperature_2m_min") or [None])[0]
        precip = (daily.get("precipitation_sum") or [None])[0]
        if tmax is not None or tmin is not None:
            anomaly_comment = "Поки без аномалій — просто історичні дані для цього дня."
            weather = {
                "t_min": tmin,
                "t_max": tmax,
                "precipitation": precip,
                "anomaly_comment": anomaly_comment,
            }

    # Солнце
    astro = None
    if sun_resp.status_code == 200:
        s = sun_resp.json().get("results") or {}
        astro = {
            "sunrise": s.get("sunrise"),
            "sunset": s.get("sunset"),
            "day_length": s.get("day_length"),
            "moon_phase": s.get("moonrise") or "невідомо",
            "events": [],
        }

    # Исторические события
    world_events = []
    if wiki_resp.status_code == 200:
        body = wiki_resp.json()
        # Берём немного событий, рождений и смертей
        for section_key in ("events", "births", "deaths"):
            for item in body.get(section_key, [])[:3]:
                text = item.get("text") or item.get("pages", [{}])[0].get("normalizedtitle")
                year = item.get("year")
                if text:
                    if year:
                        world_events.append(f"{year}: {text}")
                    else:
                        world_events.append(text)

    fun_score = None
    if weather or astro or world_events:
        # простой «индекс незвичності» — чем больше данных, тем выше
        fun_score = min(10, 3 + len(world_events) // 2)

    return {
        "date": d.isoformat(),
        "location": city,
        "weather": weather,
        "astro": astro,
        "world_events": world_events,
        "fun_score": fun_score,
    }
