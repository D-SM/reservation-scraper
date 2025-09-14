from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from scraper import scrape_slots

app = FastAPI()

# 🔹 CORS – żeby można było testować z dowolnej przeglądarki / fetch
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 🔹 model requestu dla POST
class Req(BaseModel):
    profile_url: str
    service: Optional[str] = None
    barber: Optional[str] = None
    pref: str = "asap"          # asap | today_any | any | today_pm | today_evening | exact
    date: Optional[str] = None  # YYYY-MM-DD albo np. "poniedziałek" jeśli w scraperze obsłużysz
    time_from: Optional[str] = None


@app.get("/")
def root():
    return {"ok": True}


@app.get("/healthz")
def health():
    return {"status": "ok"}


# 🔹 POST – standardowe wywołanie z Voiceflow
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
        raise HTTPException(status_code=502, detail=f"scrape_error: {e}")


# 🔹 GET – łatwe testowanie w przeglądarce (slots_qs?profile_url=...&barber=Igor&pref=exact&date=2025-09-15)
@app.get("/slots_qs")
def slots_qs(
    profile_url: str = Query(...),
    service: Optional[str] = None,
    barber: Optional[str] = None,
    pref: str = "asap",
    date: Optional[str] = None,
    time_from: Optional[str] = None
):
    try:
        data = scrape_slots(
            profile_url=profile_url,
            service=service,
            barber=barber,
            pref=pref,
            date=date,
            time_from=time_from
        )
        return {"slots": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"scrape_error: {e}")


# 🔹 Prosta strona testowa – klik i masz wynik
@app.get("/test", response_class=HTMLResponse)
def test_page():
    return """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Scraper test</title></head>
<body style="font-family:system-ui;max-width:700px;margin:40px auto;">
  <h1>Test /slots</h1>
  <label>profile_url <input id="u" size="80" value="https://booksy.com/pl-pl/twoj-profil"></label><br><br>
  <label>barber <input id="b" value=""></label>
  <label style="margin-left:1rem;">pref 
    <select id="p">
      <option>asap</option>
      <option>today_any</option>
      <option>any</option>
      <option>today_pm</option>
      <option>today_evening</option>
      <option>exact</option>
    </select>
  </label>
  <label style="margin-left:1rem;">date <input id="d" placeholder="YYYY-MM-DD"></label>
  <label style="margin-left:1rem;">time_from <input id="t" placeholder="HH:MM"></label>
  <button id="go" style="margin-left:1rem;">Wyślij</button>
  <pre id="out" style="background:#f6f8fa;padding:16px;white-space:pre-wrap;"></pre>
<script>
document.getElementById('go').
