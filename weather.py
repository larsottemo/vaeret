#!/usr/bin/env python3
"""
Henter værdata for Svolvær via Open-Meteo og oppdaterer README.md + weather.json.
Kjører automatisk via GitHub Actions.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
import urllib.request
import urllib.parse

# --- Konfigurasjon ---
LAT = 68.2342
LON = 14.5683
TIMEZONE = "Europe/Oslo"
LOCATION_NAME = "Svolvær"

def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "svolvaer-weather-github-action"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def get_weather() -> dict:
    """Henter data for de siste 5+ dagene + nåværende."""
    params = {
        "latitude": LAT,
        "longitude": LON,
        "timezone": TIMEZONE,
        "past_days": 5,
        "forecast_days": 1,
        "current": "temperature_2m,pressure_msl,wind_speed_10m,weather_code",
        "hourly": "precipitation,wind_speed_10m,temperature_2m,pressure_msl",
        "daily": "precipitation_sum,wind_speed_10m_max,temperature_2m_max,temperature_2m_min,pressure_msl_mean",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params, doseq=True)
    return fetch_json(url)


def find_index(times: list[str], target: datetime) -> int | None:
    """Finn nærmeste time-indeks for en datetime."""
    target_str = target.strftime("%Y-%m-%dT%H:00")
    for i, t in enumerate(times):
        if t.startswith(target_str[:13]):  # YYYY-MM-DDTHH
            return i
    # Fallback: nærmeste
    target_ts = target.timestamp()
    best_i, best_diff = None, float("inf")
    for i, t in enumerate(times):
        try:
            dt = datetime.fromisoformat(t)
            diff = abs(dt.timestamp() - target_ts)
            if diff < best_diff:
                best_diff, best_i = diff, i
        except Exception:
            continue
    return best_i


def safe_get(arr, idx, default=None):
    if idx is None or arr is None or idx < 0 or idx >= len(arr):
        return default
    val = arr[idx]
    return default if val is None else val


def compute_stats(data: dict) -> dict:
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)

    current = data.get("current", {})
    hourly = data.get("hourly", {})
    daily = data.get("daily", {})

    times = hourly.get("time", [])
    precip = hourly.get("precipitation", [])
    wind = hourly.get("wind_speed_10m", [])
    temp = hourly.get("temperature_2m", [])
    pressure = hourly.get("pressure_msl", [])

    # --- Dagens temperatur (nå) ---
    temp_now = current.get("temperature_2m")

    # --- Lufttrykk i dag (nå) ---
    pressure_now = current.get("pressure_msl")

    # --- Vindstyrke i går (maks + snitt) ---
    yesterday = (now - timedelta(days=1)).date()
    wind_yesterday = []
    for i, t in enumerate(times):
        try:
            dt = datetime.fromisoformat(t).astimezone(tz)
            if dt.date() == yesterday:
                v = safe_get(wind, i)
                if v is not None:
                    wind_yesterday.append(v)
        except Exception:
            pass
    wind_max_yest = max(wind_yesterday) if wind_yesterday else None
    wind_mean_yest = (sum(wind_yesterday) / len(wind_yesterday)) if wind_yesterday else None

    # --- Nedbør siste to døgn (sum av de to siste hele døgnene) ---
    # Bruker daily hvis tilgjengelig, ellers summerer hourly
    precip_2d = None
    if daily and "precipitation_sum" in daily and "time" in daily:
        # daily.time er datoer, siste er ofte i dag (ufullstendig)
        daily_times = daily["time"]
        daily_precip = daily["precipitation_sum"]
        # Finn de to siste komplette dagene (ikke i dag)
        sums = []
        for i, d in enumerate(daily_times):
            if d < now.strftime("%Y-%m-%d"):
                val = safe_get(daily_precip, i)
                if val is not None:
                    sums.append((d, val))
        if len(sums) >= 2:
            # de to siste
            precip_2d = sums[-1][1] + sums[-2][1]
            precip_2d_dates = f"{sums[-2][0]} + {sums[-1][0]}"
        elif len(sums) == 1:
            precip_2d = sums[0][1]
            precip_2d_dates = sums[0][0]
        else:
            precip_2d_dates = None
    else:
        precip_2d_dates = None

    # Fallback: summer siste 48 timer
    if precip_2d is None:
        cutoff = now - timedelta(hours=48)
        total = 0.0
        count = 0
        for i, t in enumerate(times):
            try:
                dt = datetime.fromisoformat(t).astimezone(tz)
                if dt >= cutoff:
                    v = safe_get(precip, i, 0.0)
                    total += v
                    count += 1
            except Exception:
                pass
        precip_2d = round(total, 1) if count else None
        precip_2d_dates = "siste 48 timer"

    # --- Lufttrykk for 4 dager siden (nærmeste time) ---
    four_days_ago = now - timedelta(days=4)
    idx_4d = find_index(times, four_days_ago)
    pressure_4d = safe_get(pressure, idx_4d)

    # Alternativ: daglig mean hvis hourly mangler
    if pressure_4d is None and daily and "pressure_msl_mean" in daily:
        target_date = four_days_ago.strftime("%Y-%m-%d")
        for i, d in enumerate(daily.get("time", [])):
            if d == target_date:
                pressure_4d = safe_get(daily["pressure_msl_mean"], i)
                break

    return {
        "location": LOCATION_NAME,
        "latitude": LAT,
        "longitude": LON,
        "updated": now.isoformat(timespec="seconds"),
        "updated_local": now.strftime("%Y-%m-%d %H:%M"),
        "precipitation_last_2_days_mm": round(precip_2d, 1) if precip_2d is not None else None,
        "precipitation_period": precip_2d_dates,
        "wind_yesterday_max_ms": round(wind_max_yest, 1) if wind_max_yest is not None else None,
        "wind_yesterday_mean_ms": round(wind_mean_yest, 1) if wind_mean_yest is not None else None,
        "temperature_now_c": round(temp_now, 1) if temp_now is not None else None,
        "pressure_4_days_ago_hpa": round(pressure_4d, 1) if pressure_4d is not None else None,
        "pressure_now_hpa": round(pressure_now, 1) if pressure_now is not None else None,
        "wind_now_ms": round(current.get("wind_speed_10m"), 1) if current.get("wind_speed_10m") is not None else None,
    }


def format_markdown(stats: dict) -> str:
    def fmt(v, unit=""):
        if v is None:
            return "–"
        return f"{v}{unit}"

    period = stats.get("precipitation_period") or "siste to døgn"

    return f"""<!-- WEATHER-START -->
## 🌤 Vær i {stats['location']}

| Måling | Verdi |
|--------|-------|
| 🌧 **Nedbør siste to døgn** | {fmt(stats['precipitation_last_2_days_mm'], ' mm')} ({period}) |
| 💨 **Vindstyrke i går** | maks {fmt(stats['wind_yesterday_max_ms'], ' m/s')} · snitt {fmt(stats['wind_yesterday_mean_ms'], ' m/s')} |
| 🌡 **Dagens temperatur** | {fmt(stats['temperature_now_c'], ' °C')} |
| 📉 **Lufttrykk for 4 dager siden** | {fmt(stats['pressure_4_days_ago_hpa'], ' hPa')} |
| 📈 **Lufttrykk i dag** | {fmt(stats['pressure_now_hpa'], ' hPa')} |

*Sist oppdatert: {stats['updated_local']} (Europe/Oslo)*  
*Data: [Open-Meteo](https://open-meteo.com) · Koordinater: {stats['latitude']}, {stats['longitude']}*
<!-- WEATHER-END -->
"""


def update_readme(markdown_block: str):
    path = "README.md"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = "# Svolvær vær\n\n"

    start = "<!-- WEATHER-START -->"
    end = "<!-- WEATHER-END -->"

    if start in content and end in content:
        before = content.split(start)[0]
        after = content.split(end)[-1]
        new_content = before + markdown_block + after
    else:
        # Legg til på slutten
        new_content = content.rstrip() + "\n\n" + markdown_block + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    print("Henter værdata for Svolvær...")
    data = get_weather()
    stats = compute_stats(data)

    # Skriv JSON
    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print("Skrev weather.json")

    # Oppdater README
    md = format_markdown(stats)
    update_readme(md)
    print("Oppdaterte README.md")

    # Vis resultat
    print("\n" + md)


if __name__ == "__main__":
    main()
