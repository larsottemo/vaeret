# 🌤 Svolvær vær

Automatisk oppdatert værdata for **Svolvær** (Lofoten) via GitHub Actions + [Open-Meteo](https://open-meteo.com).

<!-- WEATHER-START -->
## 🌤 Vær i Svolvær

| Måling | Verdi |
|--------|-------|
| 🌧 **Nedbør siste to døgn** | 0.6 mm (2026-08-25 + 2026-08-26) |
| 💨 **Vindstyrke i går** | maks 11.5 m/s · snitt 5.2 m/s |
| 🌡 **Dagens temperatur** | 15.2 °C |
| 📉 **Lufttrykk for 4 dager siden** | 1016.1 hPa |
| 📈 **Lufttrykk i dag** | 1024.4 hPa |

*Sist oppdatert: 2026-08-27 15:11 (Europe/Oslo)*  
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
