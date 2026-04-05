#!/usr/bin/env python3
"""
Process LILA BLACK parquet telemetry data into JSON for the web visualization tool.
Outputs:
  - public/data/matches.json  (match metadata index)
  - public/data/match_{id}.json (per-match player journey data)
"""

import pyarrow.parquet as pq
import pandas as pd
import os, json, sys, re
from collections import defaultdict

BASE = os.path.join(os.path.dirname(__file__), "..", "player_data")
OUT = os.path.join(os.path.dirname(__file__), "public", "data")

DAYS = ["February_10", "February_11", "February_12", "February_13", "February_14"]
DAY_LABELS = {
    "February_10": "2026-02-10",
    "February_11": "2026-02-11",
    "February_12": "2026-02-12",
    "February_13": "2026-02-13",
    "February_14": "2026-02-14",
}

MAP_CONFIG = {
    "AmbroseValley": {"scale": 900, "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581, "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

def is_bot(user_id):
    """Bots have short numeric user_ids, humans have UUIDs."""
    return not bool(re.match(r'^[0-9a-f]{8}-', user_id))

def world_to_pixel(x, z, map_id):
    cfg = MAP_CONFIG[map_id]
    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]
    px = u * 1024
    py = (1 - v) * 1024
    return round(px, 1), round(py, 1)

def ts_to_raw_ms(ts):
    """Convert timestamp to raw ms integer (the game server's internal time)."""
    if pd.isna(ts):
        return 0
    return int(ts.timestamp() * 1000)

def process_all():
    # Collect all data grouped by match
    match_data = defaultdict(lambda: {"players": defaultdict(list), "map_id": None, "date": None})

    file_count = 0
    error_count = 0

    for day in DAYS:
        folder = os.path.join(BASE, day)
        if not os.path.isdir(folder):
            continue
        files = os.listdir(folder)
        for fname in files:
            filepath = os.path.join(folder, fname)
            try:
                df = pq.read_table(filepath).to_pandas()
            except Exception as e:
                error_count += 1
                continue

            if df.empty:
                continue

            df['event'] = df['event'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)

            user_id = str(df['user_id'].iloc[0])
            match_id = str(df['match_id'].iloc[0])
            map_id = str(df['map_id'].iloc[0])

            # Clean match_id (remove .nakama-0 suffix for display)
            match_id_clean = match_id.replace('.nakama-0', '')

            match_data[match_id_clean]["map_id"] = map_id
            match_data[match_id_clean]["date"] = DAY_LABELS[day]

            bot = is_bot(user_id)

            # Convert events to compact format
            events = []
            for _, row in df.iterrows():
                px, py = world_to_pixel(row['x'], row['z'], map_id)
                ts_val = ts_to_raw_ms(row['ts'])
                events.append({
                    "px": px,
                    "py": py,
                    "t": ts_val,
                    "e": row['event'],
                })

            # Sort by timestamp
            events.sort(key=lambda e: e['t'])

            match_data[match_id_clean]["players"][user_id] = {
                "bot": bot,
                "events": events,
            }

            file_count += 1
            if file_count % 200 == 0:
                print(f"  Processed {file_count} files...")

    print(f"Processed {file_count} files ({error_count} errors)")
    print(f"Found {len(match_data)} unique matches")

    # Build match index
    match_index = []
    for mid, mdata in match_data.items():
        humans = sum(1 for p in mdata["players"].values() if not p["bot"])
        bots = sum(1 for p in mdata["players"].values() if p["bot"])
        total_events = sum(len(p["events"]) for p in mdata["players"].values())

        # Count event types
        event_counts = defaultdict(int)
        for p in mdata["players"].values():
            for ev in p["events"]:
                event_counts[ev["e"]] += 1

        match_index.append({
            "id": mid,
            "map": mdata["map_id"],
            "date": mdata["date"],
            "humans": humans,
            "bots": bots,
            "totalEvents": total_events,
            "kills": event_counts.get("Kill", 0) + event_counts.get("BotKill", 0),
            "deaths": event_counts.get("Killed", 0) + event_counts.get("BotKilled", 0) + event_counts.get("KilledByStorm", 0),
            "loots": event_counts.get("Loot", 0),
        })

    match_index.sort(key=lambda m: (m["date"], m["map"], m["id"]))

    # Write match index
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "matches.json"), "w") as f:
        json.dump(match_index, f, separators=(',', ':'))
    print(f"Wrote matches.json ({len(match_index)} matches)")

    # Write per-match data files
    for mid, mdata in match_data.items():
        # Normalize timestamps: raw ms values are game-server ticks (~5ms apart).
        # We normalize to 0..N where each tick ~= 5ms, then scale so the match
        # plays back over a reasonable duration.
        all_times = []
        for p in mdata["players"].values():
            for ev in p["events"]:
                all_times.append(ev["t"])

        if all_times:
            min_t = min(all_times)
            max_t = max(all_times)
            raw_range_ms = max_t - min_t

            # Normalize to seconds. The raw range is typically 200-800ms of server ticks.
            # Each tick is ~5ms. We treat the total tick range as the match duration.
            # Scale: raw_range_ms of ticks → proportional seconds.
            # A typical match has ~150 ticks spanning ~750ms of server time.
            # We map this to a reasonable playback duration (proportional to event count).
            # Simple approach: normalize to 0..1 range, then the JS side can
            # use total number of unique timestamps to estimate duration.
            if raw_range_ms > 0:
                for p in mdata["players"].values():
                    for ev in p["events"]:
                        ev["t"] = round((ev["t"] - min_t) / raw_range_ms, 4)
            else:
                for p in mdata["players"].values():
                    for ev in p["events"]:
                        ev["t"] = 0
        else:
            raw_range_ms = 0

        # Count unique tick values to estimate match length
        unique_ticks = len(set(all_times))

        match_out = {
            "id": mid,
            "map": mdata["map_id"],
            "date": mdata["date"],
            "duration": 1.0,
            "ticks": unique_ticks,
            "rawRangeMs": raw_range_ms,
            "players": {}
        }

        for uid, pdata in mdata["players"].items():
            match_out["players"][uid] = pdata

        safe_id = mid[:36]  # truncate for filename safety
        with open(os.path.join(OUT, f"match_{safe_id}.json"), "w") as f:
            json.dump(match_out, f, separators=(',', ':'))

    print(f"Wrote {len(match_data)} match data files")

    # Print summary stats
    maps = defaultdict(int)
    dates = defaultdict(int)
    for m in match_index:
        maps[m["map"]] += 1
        dates[m["date"]] += 1

    print("\nMatches per map:")
    for k, v in sorted(maps.items()):
        print(f"  {k}: {v}")
    print("\nMatches per date:")
    for k, v in sorted(dates.items()):
        print(f"  {k}: {v}")

if __name__ == "__main__":
    process_all()
