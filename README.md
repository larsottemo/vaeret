# 🌤 Svolvær vær

Automatisk oppdatert værdata for **Svolvær** (Lofoten) via GitHub Actions + [Open-Meteo](https://open-meteo.com).

<!-- WEATHER-START -->
## 🌤 Vær i Svolvær

| Måling | Verdi |
|--------|-------|
| 🌧 **Nedbør siste to døgn** | 8.6 mm (2026-08-29 + 2026-08-30) |
| 💨 **Vindstyrke i går** | maks 19.4 m/s · snitt 10.9 m/s |
| 🌡 **Dagens temperatur** | 13.3 °C |
| 📉 **Lufttrykk for 4 dager siden** | 1024.9 hPa |
| 📈 **Lufttrykk i dag** | 1004.7 hPa |

*Sist oppdatert: 2026-08-31 10:57 (Europe/Oslo)*  
*Data: [Open-Meteo](https://open-meteo.com) · Koordinater: 68.2342, 14.5683*
<!-- WEATHER-END -->





































---

## Hvordan det fungerer

1. GitHub Actions kjører `weather.py` automatisk hver 3. time (eller manuelt).
2. Scriptet henter data fra Open-Meteo (gratis, ingen API-nøkkel).
3. README.md og `weather.json` oppdateres og commits tilbake til repoet.

## Hva som vises

| Felt | Beskrivelse |
|------|-------------|
| Nedbør siste to døgn | Sum av nedbør de to siste hele døgnene (mm) |
| Vindstyrke i går | Maksimum og gjennomsnittlig vindhastighet (m/s) |
| Dagens temperatur | Nåværende temperatur (°C) |
| Lufttrykk for 4 dager siden | Lufttrykk på tilsvarende tidspunkt for 4 dager siden (hPa) |
| Lufttrykk i dag | Nåværende lufttrykk (hPa) |

## Manuell kjøring

Gå til **Actions** → **Oppdater værdata for Svolvær** → **Run workflow**.

## Lokal testing

```bash
python weather.py
```

## Lisens

Data fra Open-Meteo (CC BY 4.0). Kode fri å bruke.
