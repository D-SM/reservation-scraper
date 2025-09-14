from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scraper import scrape_slots

app = FastAPI()

class Req(BaseModel):
    profile_url: str
    service: str | None = None
    barber: str | None = None
    pref: str = "asap"          # asap | today_any | any | today_pm | today_evening | exact
    date: str | None = None     # YYYY-MM-DD
    time_from: str | None = None

@app.get("/")
def root():
    return {"ok": True}

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/slots")
def slots(r: Req):
    try:
        data = scrape_slots(
            profile_url=r.profile_url,
            service=r.service,
            barber=r.barber,
            pref=r.pref,
            date=r.date,
            time_from=r.time_from
        )
        return {"slots": data}
    except Exception as e:
        # kluczowe: nie ubijamy procesu – zwracamy 502 dla Voiceflow
        raise HTTPException(status_code=502, detail=f"scrape_error: {e}")
