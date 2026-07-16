#!/usr/bin/env python3
"""Simplify + enrich the nationwide police-jurisdiction GeoJSON so the
frontend can consume it directly.

Input : data/geo/israel-police-jurisdictions-raw.geojson (16 MB from GDB extract)
Output: data/geo/israel-police-jurisdictions.geojson (target ~1 MB, enriched props)
Also  : data/districts/israel-police-services.json (station-service lookup with slug)
"""
from __future__ import annotations
import json, re
from pathlib import Path
from shapely.geometry import shape, mapping

ROOT = Path(__file__).resolve().parent.parent
IN_GEO = ROOT / "data/geo/israel-police-jurisdictions-raw.geojson"
OUT_GEO = ROOT / "data/geo/israel-police-jurisdictions.geojson"
SVC = ROOT / "data/districts/israel-police-services.json"

# mahoz → palette key (matches our brand palette)
MAHOZ_PALETTE = {
    "ירושלים":  "purple",
    "תל אביב":  "pink",
    "ת\"א":     "pink",
    "מרכז":     "teal-dk",
    "חוף":      "purple-dk",
    "צפון":     "teal-lt",
    "דרום":     "purple-lt",
    "ש\"י":     "pink-dk",
}

# minimal Hebrew → latin slug (rough — Magen team can override in JSON)
HE_TO_LATIN = {
    "א":"a","ב":"b","ג":"g","ד":"d","ה":"h","ו":"v","ז":"z","ח":"ch","ט":"t","י":"y",
    "כ":"k","ך":"k","ל":"l","מ":"m","ם":"m","נ":"n","ן":"n","ס":"s","ע":"","פ":"p","ף":"f",
    "צ":"ts","ץ":"ts","ק":"k","ר":"r","ש":"sh","ת":"t","'":"","״":"","׳":"",
    " ":"-","-":"-",
}
def slugify(s):
    s = re.sub(r'^(תחנת|מרחב)\s*', '', s or '').strip()
    out = "".join(HE_TO_LATIN.get(c, c) for c in s).lower()
    return re.sub(r'-+', '-', out).strip('-') or "unknown"

def main():
    raw = json.loads(IN_GEO.read_text())
    services = json.loads(SVC.read_text())
    svc_by_name_he = {s["name_he"]: s for s in services["stations"]}

    features_out = []
    matched = 0; unmatched = []
    for feat in raw["features"]:
        p = feat["properties"]
        name_he = (p.get("TahanaName") or "").strip()
        # Try to match against services JSON by exact name_he
        svc = svc_by_name_he.get(name_he)
        if svc:
            matched += 1
            slug = svc["slug"]
            name_en = svc.get("name_en") or ""
        else:
            unmatched.append(name_he)
            slug = slugify(name_he) + "-nomatch"
            name_en = ""
        mahoz = (p.get("MahozName") or "").strip()
        merhav = (p.get("MerhavName") or "").strip()

        # simplify geometry (tolerance in degrees, ~0.0008 ≈ 90m)
        geom = shape(feat["geometry"])
        simplified = geom.simplify(0.0008, preserve_topology=True)
        # Round coordinates to 5 decimals to shrink JSON further
        gj = mapping(simplified)
        def round_coords(x):
            if isinstance(x, (list, tuple)):
                if x and isinstance(x[0], (int, float)):
                    return [round(x[0], 5), round(x[1], 5)]
                return [round_coords(y) for y in x]
            return x
        gj["coordinates"] = round_coords(gj["coordinates"])

        features_out.append({
            "type": "Feature",
            "properties": {
                "slug":       slug,
                "name_he":    name_he,
                "short_he":   (p.get("TahanaShortName") or "").strip(),
                "name_en":    name_en,
                "mahoz_he":   mahoz,
                "merhav_he":  merhav,
                "palette":    MAHOZ_PALETTE.get(mahoz, "teal"),
                "layer":      "police",
            },
            "geometry": gj,
        })

    fc = {"type":"FeatureCollection","features": features_out}
    OUT_GEO.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
    size = OUT_GEO.stat().st_size
    print(f"wrote {OUT_GEO.name}: {len(features_out)} features, {size:,} bytes ({size/1024:.0f} KB)")
    print(f"matched {matched}/{len(raw['features'])} against services JSON")
    if unmatched:
        print(f"unmatched names: {unmatched[:10]}")

if __name__ == "__main__":
    main()
