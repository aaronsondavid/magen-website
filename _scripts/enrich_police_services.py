#!/usr/bin/env python3
"""
Enrich data/districts/jerusalem-police-services.json with real
addresses + coordinates + sub-reception points, pulled from the
data.gov.il police_receptions CKAN datastore. Fields we get:
UnitName, MerhavName, SiteType, Address, Long_X_, Lat_Y.

The bulk CSV/GDB downloads at e.data.gov.il are blocked by a JS bot
challenge, but the CKAN datastore_search API is open — we use it.
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "districts" / "jerusalem-police-services.json"
CACHE = ROOT / "data" / "_source" / "police_receptions_jerusalem.json"

RESOURCE_ID = "848b57bf-362f-4eda-993a-3c74b1feef44"

# TahanaName (Hebrew) from the boundaries GDB -> station slug used
# throughout the site. Must match _scripts/build_police_jurisdictions.py.
STATION_SLUG_BY_HE = {
    "תחנת בית שמש":   "beit-shemesh",
    "מרחב דוד":        "merhav-david",
    "תחנת הראל":      "harel",
    "תחנת לב הבירה":  "lev-habira",
    "תחנת מוריה":     "moriah",
    "תחנת מטה יהודה": "mateh-yehuda",
    "תחנת עוז":       "oz",
    "תחנת שלם":       "shalem",
    "תחנת שפט":       "shafat",
}

# Sub-reception "נקודות" get grouped under their Merhav's stations; we
# route them to the closest station by coordinates.
MERHAV_STATIONS = {
    "מרחב ציון": ["beit-shemesh","harel","lev-habira","moriah","mateh-yehuda"],
    "מרחב קדם":  ["oz","shalem","shafat"],
    "מרחב דוד":  ["merhav-david"],
}


def fetch_records() -> list:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    q = urllib.parse.quote("ירושלים")
    url = f"https://data.gov.il/api/3/action/datastore_search?resource_id={RESOURCE_ID}&limit=250&q={q}"
    data = json.loads(urllib.request.urlopen(url).read())
    recs = data["result"]["records"]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(recs, ensure_ascii=False, indent=2))
    return recs


def haversine_km(a, b) -> float:
    from math import radians, sin, cos, asin, sqrt
    lat1, lon1 = radians(a[0]), radians(a[1])
    lat2, lon2 = radians(b[0]), radians(b[1])
    d = 2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2))
    return d * 6371


def build() -> dict:
    recs = fetch_records()

    # First pass: pick out the primary station address for each slug.
    stations = {}
    for r in recs:
        if r.get("SiteType") != "תחנה" and r.get("UnitName") not in STATION_SLUG_BY_HE:
            continue
        name = r["UnitName"]
        slug = STATION_SLUG_BY_HE.get(name)
        if not slug:
            continue
        stations[slug] = {
            "address": r.get("Address"),
            "lat":     r.get("Lat_Y"),
            "lng":     r.get("Long_X_"),
            "phone":   None,
            "hours":   None,
            "magen_coordinator": None,
            "notes":   None,
            "sub_points": [],
        }

    # Merhav-level HQ (Merhav David is our only station-slug at this level).
    for r in recs:
        if r.get("SiteType") == "מרחב" and r.get("UnitName") in STATION_SLUG_BY_HE:
            slug = STATION_SLUG_BY_HE[r["UnitName"]]
            stations.setdefault(slug, {})
            stations[slug].update({
                "address": r.get("Address"),
                "lat":     r.get("Lat_Y"),
                "lng":     r.get("Long_X_"),
                "phone":   None, "hours": None, "magen_coordinator": None,
                "notes":   "Covers the Old City, downtown Jerusalem, and central-city addresses. Serves as the Jerusalem sub-district investigative HQ.",
                "sub_points": stations.get(slug, {}).get("sub_points", []),
            })

    # Second pass: attach sub-reception points to their nearest station
    # inside the same Merhav.
    for r in recs:
        if r.get("SiteType") != "נקודה":
            continue
        merhav = r.get("MerhavName")
        candidates = MERHAV_STATIONS.get(merhav, [])
        lat, lng = r.get("Lat_Y"), r.get("Long_X_")
        if not (lat and lng and candidates):
            continue
        # Route to the nearest station-slug in this merhav.
        nearest = min(
            (s for s in candidates if s in stations and stations[s].get("lat")),
            key=lambda s: haversine_km((lat, lng), (stations[s]["lat"], stations[s]["lng"])),
            default=None,
        )
        if not nearest:
            continue
        stations[nearest]["sub_points"].append({
            "name":    r["UnitName"],
            "address": r.get("Address"),
            "lat":     lat,
            "lng":     lng,
        })

    return {
        "layer": "police",
        "meta": {
            "source_boundaries": "data.gov.il / israel-police / police_boundaries (PoliceStationBoundaries)",
            "source_addresses":  "data.gov.il / israel-police / police_receptions (publicpoliceunits) via CKAN datastore_search",
            "phone_hours_status": "Not published in data.gov.il open data — will be curated manually or scraped from police.gov.il station pages.",
            "updated": "2026-07-15",
        },
        "stations": stations,
    }


def main() -> None:
    data = build()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT}")
    for slug, s in data["stations"].items():
        subs = len(s.get("sub_points") or [])
        print(f"  {slug:15s}  addr={s.get('address') and s['address'][:60] or '—'}  ({subs} sub-points)")


if __name__ == "__main__":
    main()
