SELECTORS = {
    "accept_cookies": "button:has-text('Akceptuj')",
    "service_card_by_name": lambda name: f"[role='button']:has-text('{name}')",
    "barber_card_by_name": lambda name: f"[role='button']:has-text('{name}')",
    "calendar_open": "[data-testid='date-picker'], [aria-label='Wybierz datę']",
    "calendar_day": lambda iso: f"[data-date='{iso}'], button[aria-label*='{iso}']",
    "time_slot_buttons": "[role='button'][data-testid*='slot'], button:has-text(':')",
    "next_day": "[aria-label='Następny dzień'], [data-testid='next-day']"
}
