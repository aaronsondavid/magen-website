#!/usr/bin/env python3
"""Parse the gov.il police-stations dump into structured JSON, then merge
into data/_source/police-stations-fill-me-in.csv by fuzzy-matching Hebrew
station names against the units-CSV names.

Input : /tmp/police-scrape.txt (blob pasted from gov.il)
Output: data/_source/police-stations-fill-me-in.csv (updated in-place)
        data/districts/israel-police-services.json (final assembled)
"""
from __future__ import annotations
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRAPE = Path("/tmp/police-scrape.txt")
TEMPLATE = ROOT / "data/_source/police-stations-fill-me-in.csv"
GEO = ROOT / "data/geo/israel-police-jurisdictions-raw.geojson"
OUT_JSON = ROOT / "data/districts/israel-police-services.json"

# ---- Parser ------------------------------------------------------------------

RANKS = ["ניצב", "תנ\"צ", "נצ\"מ", "סנ\"צ", "רפ\"ק", "רב נגד", "רס\"ר", "רס\"ב", "פקד",
         "רב-רס\"ל", "רב פקד", "תנ\\\"צ", "רס\\\"ר", "מפקד", "מ\"מ", "רס\"ל"]

def _extract_commander(lines):
    """The commander line on gov.il looks like: 'שם משפחהרב-רסל שם משפחה' or 'שם משפחהסנצ שם משפחה'.
    The name is repeated: first with no rank prefix, then with rank prefix glued.
    Strategy: find a line before 'כתובת:' that contains a known rank marker, take the text after the rank."""
    for l in lines:
        if l.startswith(("כתובת:", "טלפון:", "פקס:", "אימייל:")): break
        # Look for any rank keyword; commander name is what follows
        for rank in RANKS:
            idx = l.find(rank)
            if idx >= 0:
                after = l[idx + len(rank):].strip()
                if after:
                    return f"{rank} {after}"
    return ""

def parse_blocks(text: str):
    """Split by the '-\n' delimiter and parse each block."""
    blocks = re.split(r'\n-\n', "\n" + text.strip() + "\n")
    parsed = []
    for b in blocks:
        b = b.strip()
        if not b: continue
        lines = [l.rstrip() for l in b.splitlines() if l.strip()]
        if len(lines) < 2: continue
        name = lines[0].strip()
        addr = phone = fax = email = ""
        for l in lines:
            if l.startswith("כתובת:"): addr = l[len("כתובת:"):].strip()
            elif l.startswith("טלפון:"): phone = l[len("טלפון:"):].strip()
            elif l.startswith("פקס:"):   fax   = l[len("פקס:"):].strip()
            elif l.startswith("אימייל:"): email = l[len("אימייל:"):].strip()
        commander = _extract_commander(lines)
        parsed.append({
            "name_he":   name,
            "address":   addr,
            "phone":     phone,
            "fax":       fax,
            "email":     email,
            "commander": commander,
        })
    return parsed

# ---- Matcher -----------------------------------------------------------------

def normalize_he(s: str) -> str:
    """Strip common prefixes + punctuation + region qualifiers to make matching easy.
    Also collapses all whitespace and hyphens so 'פתח תקווה', 'פתח-תקווה', 'פתחתקווה' all match.
    Handles common spelling variations (פאחם vs פחם, ואדי variants)."""
    s = s.strip()
    s = re.sub(r'^(תחנת|תחנה|מרחב|מחוז|נקודת|מש["׳]ק|מרכז שיטור|בסיס)\s+', '', s)
    s = re.sub(r'\s*\([^)]*\)', '', s)  # drop parentheticals
    # Trailing region qualifiers like "מרחב שומרון", "חוף", "מחוז חוף", region attached to station name
    s = re.sub(r'\s+(מרחב|מחוז)\s+\S+.*$', '', s)
    # Normalize dashes → nothing (unify hyphenated vs non-hyphenated forms)
    s = re.sub(r'[־–—-]', '', s)
    # Common Hebrew spelling variants
    s = s.replace('פאחם', 'פחם')   # אום אל-פחם / אום אל פאחם
    s = s.replace('נהרייה', 'נהריה')
    s = s.replace('טירת כרמל', 'טירת הכרמל')
    # Collapse whitespace, remove all spaces (fully normalized key)
    s = re.sub(r'\s+', '', s)
    return s

def load_template():
    with open(TEMPLATE, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def save_template(rows):
    with open(TEMPLATE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

# ---- Main --------------------------------------------------------------------

def main():
    scraped = parse_blocks(SCRAPE.read_text(encoding="utf-8"))
    print(f"parsed {len(scraped)} scraped blocks")

    rows = load_template()
    print(f"template has {len(rows)} station rows")

    # Build normalized-name → scraped-record map
    scraped_map = {}
    for s in scraped:
        key = normalize_he(s["name_he"])
        scraped_map.setdefault(key, []).append(s)

    matched = 0
    for row in rows:
        key = normalize_he(row["name_he"])
        candidates = scraped_map.get(key)
        if not candidates:
            # try alternative — scraped name might have a suffix like "(ירושלים)" or "מרחב שומרון"
            # try substring match
            for s_key, s_list in scraped_map.items():
                if s_key and (s_key in key or key in s_key):
                    candidates = s_list; break
        if candidates:
            s = candidates[0]
            row["phone"] = s["phone"]
            row["reception_hours"] = ""  # scrape didn't have hours per station
            if s["address"] and (not row["address"] or len(s["address"]) > len(row["address"])):
                row["address"] = s["address"]
            row["email"] = s["email"]
            row["fax"] = s["fax"]
            row["commander"] = s["commander"]
            matched += 1
    # Add columns if missing
    for col in ("email", "fax", "commander"):
        if col not in rows[0]:
            for r in rows: r.setdefault(col, "")

    save_template(rows)
    print(f"matched {matched}/{len(rows)} template rows → wrote {TEMPLATE.relative_to(ROOT)}")

    # Also assemble the final services JSON — stations keyed by slug so the
    # frontend can do currentServices.stations[slug] directly.
    services = {}
    for r in rows:
        entry = {
            "slug":       r["slug"],
            "name_he":    r["name_he"],
            "name_en":    r.get("name_en") or "",
            "mahoz_he":   r["mahoz_he"],
            "merhav_he":  r["merhav_he"],
            "address":    r["address"],
            "phone":      r.get("phone",""),
            "email":      r.get("email",""),
            "fax":        r.get("fax",""),
            "commander":  r.get("commander",""),
            "lng":        r["lng"],
            "lat":        r["lat"],
            "community_policing": r["community_policing"] == "yes",
        }
        services[r["slug"]] = entry

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "_meta": {
            "description": "Israel Police station directory (nationwide).",
            "source": "gov.il stations app (scraped) + data.gov.il police_receptions CSV + PoliceStationBoundaries GDB",
            "station_count": len(services),
            "with_phone": sum(1 for s in services.values() if s["phone"]),
            "with_email": sum(1 for s in services.values() if s["email"]),
        },
        "stations": services,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)} ({len(services)} stations)")

if __name__ == "__main__":
    main()
