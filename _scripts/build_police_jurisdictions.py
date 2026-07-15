#!/usr/bin/env python3
"""
Build data/geo/jerusalem-police-jurisdictions.geojson from the raw
extract produced by ogr2ogr against the data.gov.il police_boundaries
GDB.

Pipeline: extract (ogr2ogr, done separately) -> enrich (this script)
-> simplify (mapshaper, called from this script).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "_source" / "jerusalem-police-raw.geojson"
OUT = ROOT / "data" / "geo" / "jerusalem-police-jurisdictions.geojson"

# Hebrew station name -> Magen-facing display data.
# EN names are transliterations; Magen team can override.
STATIONS = {
    "תחנת בית שמש":  {"slug": "beit-shemesh",  "name_en": "Beit Shemesh",           "palette": "teal-lt"},
    "מרחב דוד":       {"slug": "merhav-david",  "name_en": "Merhav David (Old City & Centre)", "palette": "purple-lt"},
    "תחנת הראל":     {"slug": "harel",         "name_en": "Harel",                  "palette": "teal-dk"},
    "תחנת לב הבירה": {"slug": "lev-habira",    "name_en": "Lev HaBira (City Centre)","palette": "purple"},
    "תחנת מוריה":    {"slug": "moriah",        "name_en": "Moriah",                 "palette": "pink"},
    "תחנת מטה יהודה":{"slug": "mateh-yehuda",  "name_en": "Mateh Yehuda",           "palette": "teal"},
    "תחנת עוז":      {"slug": "oz",            "name_en": "Oz",                     "palette": "purple-dk"},
    "תחנת שלם":      {"slug": "shalem",        "name_en": "Shalem",                 "palette": "pink-dk"},
    "תחנת שפט":      {"slug": "shafat",        "name_en": "Shafat",                 "palette": "teal-lt"},
}


def enrich(raw_path: Path) -> dict:
    geo = json.loads(raw_path.read_text())
    kept = []
    for feat in geo["features"]:
        p = feat["properties"]
        he_full = (p.get("TahanaName") or "").strip()
        meta = STATIONS.get(he_full)
        if not meta:
            print(f"skip unknown station: {he_full!r}", file=sys.stderr)
            continue
        feat["properties"] = {
            "slug":       meta["slug"],
            "name_en":    meta["name_en"],
            "name_he":    he_full,
            "short_he":   (p.get("TahanaShortName") or "").strip(),
            "merhav_he":  (p.get("MerhavName") or "").strip(),
            "mahoz_he":   (p.get("MahozName") or "").strip(),
            "palette":    meta["palette"],
            "layer":      "police",
        }
        kept.append(feat)
    geo["features"] = kept
    return geo


def main() -> None:
    if not RAW.exists():
        sys.exit(f"missing {RAW}; run ogr2ogr extract first")
    enriched_tmp = RAW.parent / "jerusalem-police-enriched.geojson"
    enriched_tmp.write_text(json.dumps(enrich(RAW), ensure_ascii=False))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Visvalingam-weighted simplification via mapshaper; ~5% keeps
    # boundaries visually faithful at city zoom while cutting file size
    # dramatically. Also snaps vertices to close cross-boundary gaps.
    cmd = [
        "npx", "-y", "mapshaper",
        str(enriched_tmp),
        "-simplify", "visvalingam", "weighted", "5%", "keep-shapes",
        "-clean",
        "-o", "format=geojson", "precision=0.00001", str(OUT),
    ]
    subprocess.run(cmd, check=True)
    print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.1f} KB, {len(json.loads(OUT.read_text())['features'])} features)")


if __name__ == "__main__":
    main()
