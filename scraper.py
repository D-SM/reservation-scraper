from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from reservation-selectors import SELECTORS as S

TZ = ZoneInfo("Europe/Warsaw")

def _parse_times(texts, day_iso):
    slots = []
    for t in texts:
        t = t.strip()
        if ":" in t:
            slots.append({"date": day_iso, "time": t})
    return slots

def _filter_by_from(slots, time_from):
    if not time_from:
        return slots
    hh, mm = map(int, time_from.split(":"))
    threshold = time(hh, mm)
    return [s for s in slots if tuple(map(int, s["time"].split(":"))) >= (threshold.hour, threshold.minute)]

def scrape_slots(profile_url, service=None, barber=None, pref="asap",
                 date=None, time_from=None, max_days_ahead=7, per_day_limit=8):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True),
        args=["--no-sandbox", "--disable-dev-shm-usage"],
        ctx = b.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.goto(profile_url, wait_until="domcontentloaded")
        try:
            page.locator(S["accept_cookies"]).first.click(timeout=3000)
        except PWTimeout:
            pass

        if service:
            page.locator(S["service_card_by_name"](service)).first.click(timeout=10000)

        if barber and barber.lower() not in ("any", "dowolny"):
            page.locator(S["barber_card_by_name"](barber)).first.click(timeout=8000)

        try:
            page.locator(S["calendar_open"]).first.click(timeout=5000)
        except PWTimeout:
            pass

        today = datetime.now(TZ).date()

        def get_day_slots(day_date):
            day_iso = day_date.isoformat()
            try:
                page.locator(S["calendar_day"](day_iso)).first.click(timeout=3000)
            except PWTimeout:
                for _ in range(10):
                    try:
                        page.locator(S["next_day"]).first.click(timeout=1000)
                        page.locator(S["calendar_day"](day_iso)).first.click(timeout=1000)
                        break
                    except PWTimeout:
                        continue
            texts = page.locator(S["time_slot_buttons"]).all_inner_texts()
            slots = _parse_times(texts, day_iso)[:per_day_limit]
            for s in slots:
                s["barber"] = barber if barber else "dowolny"
            return slots

        results = []
        if pref == "exact" and date:
            results = get_day_slots(datetime.fromisoformat(date).date())
            results = _filter_by_from(results, time_from)
        elif pref in ("today_any","today_pm","today_evening"):
            slots = get_day_slots(today)
            if pref == "today_pm":
                slots = _filter_by_from(slots, "12:00")
            elif pref == "today_evening":
                slots = _filter_by_from(slots, "18:00")
            results = slots
        elif pref in ("asap","any"):
            for i in range(max_days_ahead+1):
                slots = get_day_slots(today + timedelta(days=i))
                if slots:
                    results = slots
                    break

        ctx.close(); b.close()
        return results[:3]
