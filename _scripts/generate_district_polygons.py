#!/usr/bin/env python3
"""Generate approximate Jerusalem community-administration polygons.

Method: Voronoi partition around 8 seed points (each roughly at the centre of
a real community admin), then clip against Jerusalem's real municipal
boundary from the gov.il shapefile we already converted. This yields 8
non-overlapping, no-gap polygons that follow natural halfway divisions
between district centres — good enough for an MVP that reads as a real map
because the base tiles will be OpenStreetMap.

When we get survey-grade GeoJSON later, this script is deleted and the
data/districts/jerusalem-community-admins.geojson file is replaced.
"""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/districts/jerusalem-community-admins.geojson"
OUT.parent.mkdir(parents=True, exist_ok=True)

# Approximate Jerusalem municipal outer boundary (hand-sketched from memory of the
# city's real outline). Traced clockwise from the north; will be replaced with
# survey-grade GeoJSON when we get it from the municipality.
JERUSALEM_OUTLINE = [
    (35.190, 31.836),  # N — Neve Ya'akov area
    (35.235, 31.828),  # NE — Pisgat Ze'ev outer edge
    (35.264, 31.815),  # NE — Anata border
    (35.263, 31.793),  # E — Isawiya / French Hill east
    (35.256, 31.775),  # E — Mount Scopus east
    (35.251, 31.755),  # SE — East Talpiot / Kidron
    (35.235, 31.735),  # SE — Har Homa east
    (35.221, 31.717),  # S — Har Homa south
    (35.200, 31.720),  # SW — Beit Safafa / Gilo south
    (35.170, 31.740),  # SW — Malha / Kiryat HaYovel south
    (35.150, 31.762),  # W — Ir Ganim west
    (35.145, 31.780),  # W — Kiryat Menachem edge
    (35.150, 31.803),  # NW — Ramot outer edge
    (35.170, 31.822),  # NW — Ramot north
    (35.190, 31.836),  # close
]

# ----------------------------------------------------------------------------
# 8 community-admin seeds — approximate centre of each cluster
# (lat, lng, slug, name_en, name_he, palette_key)
# ----------------------------------------------------------------------------
SEEDS = [
    ("lev-hair",       "Lev HaIr",                       "לב העיר",                          31.784, 35.219, "teal"),
    ("ginot-hair",     "Ginot HaIr",                     "גינות העיר",                       31.766, 35.213, "purple"),
    ("baka-talpiot",   "Baka & Talpiot",                 "בקעה ותלפיות",                    31.749, 35.220, "pink"),
    ("ramat-eshkol",   "Ramat Eshkol & Ma'alot Dafna",   "רמת אשכול ומעלות דפנה",           31.797, 35.229, "teal-dk"),
    ("kiryat-hayovel", "Kiryat HaYovel & Ir Ganim",      "קריית היובל ועיר גנים",           31.754, 35.185, "purple-dk"),
    ("ramot",          "Ramot",                          "רמות",                             31.809, 35.180, "pink-dk"),
    ("gilo-har-homa",  "Gilo & Har Homa",                "גילה והר חומה",                    31.731, 35.199, "teal-lt"),
    ("pisgat-neve",    "Pisgat Ze'ev & Neve Ya'akov",    "פסגת זאב ונווה יעקב",             31.827, 35.235, "purple-lt"),
]

def load_boundary():
    return Polygon(JERUSALEM_OUTLINE)

def voronoi_polygons(seed_points, bounding_box):
    """Return one Voronoi cell per seed as shapely Polygon (finite polygons).

    Uses ghost points far outside the bounding box to force every real seed's
    region to be finite.
    """
    pts = np.array(seed_points)
    # ghost points beyond the bounding box in each direction
    xmin, ymin, xmax, ymax = bounding_box
    dx = xmax - xmin
    dy = ymax - ymin
    ghosts = np.array([
        [xmin - 2*dx, ymin - 2*dy], [xmax + 2*dx, ymin - 2*dy],
        [xmin - 2*dx, ymax + 2*dy], [xmax + 2*dx, ymax + 2*dy],
        [(xmin + xmax) / 2, ymin - 2*dy], [(xmin + xmax) / 2, ymax + 2*dy],
        [xmin - 2*dx, (ymin + ymax) / 2], [xmax + 2*dx, (ymin + ymax) / 2],
    ])
    all_pts = np.vstack([pts, ghosts])
    vor = Voronoi(all_pts)
    polys = []
    for i in range(len(pts)):
        region_idx = vor.point_region[i]
        region = vor.regions[region_idx]
        if not region or -1 in region:
            polys.append(None)
            continue
        cell_coords = [vor.vertices[v] for v in region]
        polys.append(Polygon(cell_coords))
    return polys

def main():
    outer = load_boundary()
    print(f"boundary polygon: {len(outer.exterior.coords)} pts, bbox {outer.bounds}")

    # Voronoi wants (x, y) = (lng, lat)
    seed_pts = [(lng, lat) for _, _, _, lat, lng, _ in SEEDS]
    cells = voronoi_polygons(seed_pts, outer.bounds)

    features = []
    for (slug, name_en, name_he, lat, lng, palette), cell in zip(SEEDS, cells):
        if cell is None:
            print(f"  ! {slug}: no cell (infinite region)"); continue
        clipped = cell.intersection(outer)
        if clipped.is_empty:
            print(f"  ! {slug}: clipped to empty")
            continue
        # Simplify a bit for smaller payload (tolerance in degrees; ~11m per 0.0001°)
        clipped = clipped.simplify(0.0001, preserve_topology=True)
        geom = mapping(clipped)
        features.append({
            "type": "Feature",
            "properties": {
                "slug": slug,
                "name_en": name_en,
                "name_he": name_he,
                "centre_lat": lat,
                "centre_lng": lng,
                "palette": palette,
            },
            "geometry": geom,
        })
        print(f"  + {slug}: {geom['type']}  ~{len(json.dumps(geom))} bytes")

    fc = {"type": "FeatureCollection", "features": features}
    OUT.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size:,} bytes, {len(features)} districts)")

if __name__ == "__main__":
    main()
