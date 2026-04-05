# Architecture

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Data pipeline | Python 3 + PyArrow + Pandas | PyArrow reads parquet natively; pandas makes aggregation easy. Runs once at build time. |
| Frontend | Vanilla HTML/CSS/JS + Canvas API | Zero build step, zero dependencies, deploys to any static host. Canvas gives pixel-level control for map rendering. |
| Hosting | Any static host (Vercel, Netlify, GitHub Pages) | The app is 100% client-side. No server needed at runtime. |

**Why not React/Next.js?** The tool has one page with one interactive canvas. A framework would add build complexity without meaningful benefit. Vanilla JS keeps the stack simple and the deploy instant.

**Why not Streamlit/Dash?** Those require a Python server at runtime. A static site is cheaper to host, loads faster, and has no scaling concerns.

## Data Flow

```
parquet files (1,243 files, ~10MB)
    │
    ▼
process_data.py (Python, runs once)
    │  - reads all parquet files with PyArrow
    │  - decodes binary event column
    │  - converts world coords → minimap pixel coords
    │  - normalizes timestamps to 0-1 range per match
    │  - groups events by match_id
    │
    ▼
public/data/matches.json (124KB index)
public/data/match_{id}.json (796 files, ~6MB total)
    │
    ▼
index.html (browser)
    │  - fetches matches.json on load
    │  - fetches individual match JSON on selection
    │  - renders on HTML5 Canvas
```

## Coordinate Mapping

This was the trickiest part. The data has 3D world coordinates `(x, y, z)` but the minimap is a 2D 1024x1024 image.

**Step 1: World → UV (0-1 range)**
```
u = (x - origin_x) / scale
v = (z - origin_z) / scale
```
Each map has its own `origin` and `scale` (provided in the README):
- AmbroseValley: scale=900, origin=(-370, -473)
- GrandRift: scale=581, origin=(-290, -290)
- Lockdown: scale=1000, origin=(-500, -500)

**Step 2: UV → Pixel**
```
pixel_x = u * 1024
pixel_y = (1 - v) * 1024    // Y-flip: image origin is top-left, world Z increases upward
```

The `y` column (elevation) is ignored for 2D mapping — only `x` and `z` are used.

This conversion is done once during data processing, so the browser receives pre-computed pixel coordinates.

## Assumptions

| Area | Assumption | Reasoning |
|------|-----------|-----------|
| Timestamps | Treated as ordinal match-progress values (normalized 0-1), not wall-clock time | Raw `ts` values are game-server ticks spaced ~5ms apart. The total range per match is ~500-800ms regardless of actual match length. Normalizing to 0-1 preserves ordering for playback. |
| Bot detection | `user_id` is a UUID → human; short numeric ID → bot | Matches the README specification. Verified by checking that UUID users generate `Position` events and numeric users generate `BotPosition`. |
| Event bytes | Decoded as UTF-8 strings | All 8 event types decoded cleanly with no encoding errors across all 1,243 files. |
| Feb 14 data | Partial day, included as-is | README notes this; 37 matches vs 284 on Feb 10. No special handling needed. |

## Tradeoffs

| Decision | Alternative Considered | Why I Chose This |
|----------|----------------------|------------------|
| Pre-compute all coords in Python | Compute in browser on-the-fly | Saves CPU in the browser; match JSON files load instantly. 6MB total is acceptable for a static site. |
| One JSON file per match | Single large JSON with all data | Lazy loading — only fetch data when a match is selected. Keeps initial load fast (124KB index). |
| Canvas API for rendering | SVG or WebGL (deck.gl) | Canvas is simple, fast for this data volume (~1000 events/match), and requires no dependencies. |
| Static site, no backend | Server with DuckDB for live queries | Adds hosting complexity for minimal gain. All 796 matches fit comfortably in pre-processed JSON. |
| Normalized 0-1 timestamps | Attempt to reconstruct real-time durations | The raw timestamps don't map to real-world seconds in an obvious way. Normalized values preserve the correct ordering and work well for playback. |
