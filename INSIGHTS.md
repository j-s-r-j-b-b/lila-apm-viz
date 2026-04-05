# Insights

Three things I learned about LILA BLACK using the visualization tool.

---

## 1. Lockdown Has 3x the Storm Death Rate of Ambrose Valley

**What caught my eye:** When toggling between maps, Lockdown consistently showed more purple storm-death triangles relative to its match count. Filtering by map confirmed it.

**The data:**

| Metric | Ambrose Valley | Lockdown |
|--------|---------------|----------|
| Matches | 566 | 171 |
| Storm deaths | 17 | 17 |
| Storm deaths/match | 0.03 | **0.10** |
| Loot/journey | 17.8 | 12.1 |

Lockdown has **3.3x** the storm death rate per match despite being described as a "smaller/close-quarters map." Players are also looting less per journey on Lockdown (12.1 items vs 17.8 on Ambrose Valley).

**Why a level designer should care:** The storm is killing players disproportionately on Lockdown. This could mean:
- The storm speed/timing is too aggressive for the map's size
- Extract points are too far from high-traffic zones
- Players get funneled into dead ends with no escape path

**Actionable items:**
- Review storm pacing on Lockdown — consider slowing it or adjusting the direction
- Check if extract points are reachable from all quadrants when the storm is active
- **Metric to track:** Storm deaths/match on Lockdown (target: bring to parity with Ambrose Valley at ~0.03)

---

## 2. Player Retention Drops Sharply — Only 16% Return the Next Day

**What caught my eye:** Filtering by date shows a dramatic decline: 98 unique humans on Feb 10 → 12 on Feb 14. But what's worse is the *retention* between consecutive days.

**The data:**

| Period | Players Day 1 | Retained Day 2 | Retention |
|--------|--------------|----------------|-----------|
| Feb 10 → 11 | 98 | 16 | **16%** |
| Feb 11 → 12 | 81 | 10 | **12%** |
| Feb 12 → 13 | 59 | 11 | **19%** |
| Feb 13 → 14 | 47 | 5 | **11%** |

Day-1 retention is consistently around 12-19%. This is significantly below industry benchmarks for shooters (typically 30-40% D1 retention).

**Why a level designer should care:** If players aren't coming back, it's worth asking whether the map experience contributes. The data shows most journeys involve heavy looting (avg 17.6 items/journey) but very few human-vs-human engagements (only 3 PvP kills in the entire dataset — the rest are PvE bot kills). The gameplay loop may feel repetitive: enter → loot → kill bots → leave.

**Actionable items:**
- Investigate whether map layouts are creating enough organic PvP encounters (currently nearly zero)
- Consider POI design that funnels players into contested areas
- Add high-value loot zones that create risk/reward tension
- **Metrics to track:** D1 retention, PvP kill rate per match (currently 0.004 PvP kills/match)

---

## 3. The Southeast Quadrant of Ambrose Valley Is a Kill Hotspot

**What caught my eye:** Using the Kill Zones heatmap on multiple Ambrose Valley matches, a clear cluster emerges in the center-right and southeast portions of the map. The traffic heatmap confirms players move through there heavily.

**The data:**

Kill distribution across Ambrose Valley quadrants (dividing the map at its center):

| Quadrant | Kills | % of Total |
|----------|-------|-----------|
| Southwest | 435 | 19% |
| **Southeast** | **799** | **35%** |
| Northwest | 347 | 15% |
| Northeast | 706 | 31% |

The eastern half of Ambrose Valley accounts for **66%** of all kills. The southeast alone has **2.3x** more kills than the southwest.

**Why a level designer should care:** This kill asymmetry suggests:
- The eastern side has higher-density POIs or better loot, pulling more players (and bots) there
- The storm direction may be consistently pushing players east
- The western half may be underutilized — "dead zones" that don't contribute to gameplay

**Actionable items:**
- Audit POI placement on the western half of Ambrose Valley — add incentives to distribute traffic
- Check if the storm consistently pushes eastward, creating a predictable flow
- Consider adding an extract point or high-value loot to the southwest to balance engagement
- **Metric to track:** Kill distribution evenness across quadrants (target: no quadrant below 20% or above 30%)
