from fastapi import FastAPI
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


@app.get("/day-info")
def day_info(date: str, city: str = "Kyiv"):
    # TODO: замінити мок на реальні дані з API/БД
    return {
        "date": date,
        "location": city,
        "weather": {
            "t_min": -3.4,
            "t_max": 29.1,
            "anomaly_comment": "Цей день був приблизно на 3 °C тепліший за кліматичну норму.",
        },
        "astro": {
            "moon_phase": "повня",
            "events": [
                "Часткове місячне затемнення було видно над Східною Європою."
            ],
        },
        "world_events": [
            "У цей день народилася відома людина.",
            "Сталося цікаве відкриття у світі науки.",
        ],
        "fun_score": 7.8,
    }
