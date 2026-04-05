# LILA BLACK — Player Journey Visualizer

A web-based tool for Level Designers to explore player behavior across LILA BLACK maps. Visualizes movement paths, combat events, loot pickups, and storm deaths from 5 days of production telemetry.

**Live demo:** *[deployed URL goes here]*

## Features

- **Player journey paths** on accurate minimaps (Ambrose Valley, Grand Rift, Lockdown)
- **Human vs bot distinction** — humans get colored paths, bots get dashed grey
- **Event markers** — kills (red circles), deaths (orange X), loot (green diamonds), storm deaths (purple triangles)
- **Filtering** by map, date, and match ID search
- **Timeline/playback** — watch a match unfold over time with play/pause and speed controls
- **Heatmap overlays** — kill zones, death zones, and player traffic density
- **Match info panel** — player counts, event totals at a glance
- **Player toggles** — show/hide individual players, filter by humans-only or bots-only

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Data pipeline | Python 3, PyArrow, Pandas |
| Frontend | Vanilla HTML/CSS/JS, Canvas API |
| Hosting | Any static file server |

## Setup

### Prerequisites

- Python 3.8+ with `pyarrow` and `pandas`
- The `player_data/` folder (from the provided zip) placed alongside this project

### Install dependencies

```bash
pip install pyarrow pandas
```

### Process data

```bash
python3 process_data.py
```

This reads all parquet files from `../player_data/`, converts coordinates, normalizes timestamps, and outputs JSON files into `public/data/`.

### Run locally

```bash
cd public
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

### Deploy

The `public/` folder is a self-contained static site. Deploy it to any static host:

**Vercel:**
```bash
cd public && npx vercel --prod
```

**Netlify:**
```bash
netlify deploy --dir=public --prod
```

**GitHub Pages:**
Push the `public/` folder contents to a `gh-pages` branch.

## Project Structure

```
lila-apm-viz/
├── public/
│   ├── index.html          # The entire app (HTML + CSS + JS)
│   ├── minimaps/           # Map images (1024x1024)
│   │   ├── AmbroseValley_Minimap.png
│   │   ├── GrandRift_Minimap.png
│   │   └── Lockdown_Minimap.jpg
│   └── data/
│       ├── matches.json    # Match index (796 matches)
│       └── match_*.json    # Per-match player data
├── process_data.py         # Parquet → JSON pipeline
├── ARCHITECTURE.md         # Architecture decisions & coordinate mapping
├── INSIGHTS.md             # Three data insights with evidence
└── README.md               # This file
```

## Environment Variables

None required. The app is fully static with no external dependencies.
