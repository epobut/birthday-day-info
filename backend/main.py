from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Birthday Day Info API")

origins = [
    "*",  # на старте можно так, потом сузим под домен фронта
]

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
    # TODO: заменить мок на реальные данные из API/БД
    return {
        "date": date,
        "location": city,
        "weather": {
            "t_min": -3.4,
            "t_max": 29.1,
            "anomaly_comment": "День был теплее нормы примерно на 3 °C.",
        },
        "astro": {
            "moon_phase": "полнолуние",
            "events": [
                "Частичное лунное затмение было видно над Восточной Европой."
            ],
        },
        "world_events": [
            "В этот день родился какой-то известный человек.",
            "Произошло интересное событие в мире науки.",
        ],
        "fun_score": 7.8,
    }
