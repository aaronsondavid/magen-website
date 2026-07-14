#!/usr/bin/env python3
"""Wipe the Supporters & Partners board and repopulate from the live magen-israel.org
partners strip. Downloads each logo and uploads to the item's Logo file column."""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
import requests

BOARD_ID = 5099963394
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"
FILE_API = "https://api.monday.com/v2/file"
CACHE = Path("/tmp/partner-logos"); CACHE.mkdir(exist_ok=True)

# Column ids (from earlier query of board 5099963394)
COL_TYPE    = "text_mm52q0mz"
COL_LOGO    = "file_mm52spsc"
COL_WEBSITE = "link_mm52n796"
COL_SHOW    = "text_mm52a9mp"
COL_NOTES   = "long_text_mm52k6t1"
COL_STATUS  = "color_mm52jth8"

# Partners scraped from magen-israel.org (in order shown on the site)
PARTNERS = [
    {"name": "Maple Holistics",                            "website": "https://mapleholistics.com/",                             "type": "Corporate sponsor",     "logo_url": "https://magen-israel.org/wp-content/uploads/2022/03/MH_LogoRed.png"},
    {"name": "Jewish Women's Foundation of Boca Raton",    "website": "https://jewishboca.org/jewish-womens-foundation/",        "type": "Foundation",            "logo_url": "https://magen-israel.org/wp-content/uploads/2023/08/JWF-002-logo-300x168.jpg"},
    {"name": "CLT (Charity Loving Trust — verify name)",   "website": "",                                                        "type": "Foundation",            "logo_url": "https://magen-israel.org/wp-content/uploads/2022/03/FINAL-CLT-LOGO-1024x1024.png"},
    {"name": "My Tzedakah",                                "website": "https://www.mytzedakah.com/",                             "type": "Giving platform",       "logo_url": "https://magen-israel.org/wp-content/uploads/2022/08/logo_new-300x143.png"},
    {"name": "Good People Fund",                           "website": "https://goodpeoplefund.org/",                             "type": "Foundation",            "logo_url": "https://magen-israel.org/wp-content/uploads/2022/03/GPF_Logo_Stacked.png"},
    {"name": "Check Point",                                "website": "https://www.checkpoint.com/",                             "type": "Corporate sponsor",     "logo_url": "https://magen-israel.org/wp-content/uploads/2022/08/Logo_stacked_color_Small-300x134.png"},
    {"name": "Israel Ministry of Welfare & Social Security","website": "https://www.gov.il/he/departments/molsa",                "type": "Government",            "logo_url": "https://magen-israel.org/wp-content/uploads/2022/03/לוגו-כחול-משרד-הרווחה-וביטחון-החברתי-03-1024x264.png"},
    {"name": "Jewish Women's Foundation of Chicago",       "website": "https://jwfchicago.org/",                                 "type": "Foundation",            "logo_url": "https://magen-israel.org/wp-content/uploads/2025/02/Chicago-300x288.jpeg"},
    {"name": "Jewish Women's Foundation of NJ",            "website": "https://jwfnj.org/",                                      "type": "Foundation",            "logo_url": "https://magen-israel.org/wp-content/uploads/2025/02/aArtboard-1-300x101.png"},
    {"name": "NATAN Fund",                                 "website": "https://natan.org/",                                      "type": "Giving circle",         "logo_url": "https://magen-israel.org/wp-content/uploads/2025/07/Natan-Logo-transparent-243x300.png"},
]

def gql(query, variables=None, retries=3):
    for a in range(retries):
        r = requests.post(API, headers={"Authorization": TOKEN, "Content-Type":"application/json"},
                          json={"query": query, "variables": variables or {}}, timeout=30)
        if r.status_code == 200:
            j = r.json()
            if "errors" in j:
                raise RuntimeError(f"GraphQL error: {j['errors']}")
            return j
        if a == retries-1: r.raise_for_status()
        time.sleep(2**a)

def download_logo(url: str) -> Path:
    fname = url.rsplit("/", 1)[-1]
    # sanitize any %-encoded or non-ascii chars for local disk
    safe = "".join(c if c.isascii() and c not in '<>:"|?*' else "_" for c in fname)
    p = CACHE / safe
    if p.exists() and p.stat().st_size > 0:
        return p
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    p.write_bytes(r.content)
    return p

def upload_file(item_id: str, path: Path):
    query = ('mutation($file: File!, $item: ID!, $col: String!) {'
             '  add_file_to_column(item_id: $item, column_id: $col, file: $file) { id } }')
    map_ = {"image": ["variables.file"]}
    variables = {"file": None, "item": int(item_id), "col": COL_LOGO}
    files = {
        "query":     (None, query),
        "variables": (None, json.dumps(variables)),
        "map":       (None, json.dumps(map_)),
        "image":     (path.name, path.open("rb"), "application/octet-stream"),
    }
    r = requests.post(FILE_API, headers={"Authorization": TOKEN}, files=files, timeout=60)
    r.raise_for_status()
    j = r.json()
    if "errors" in j:
        raise RuntimeError(f"upload error: {j['errors']}")
    return j

def delete_all_existing():
    r = gql('query{ boards(ids: %d){ items_page(limit:200){ items{ id name } } } }' % BOARD_ID)
    items = r["data"]["boards"][0]["items_page"]["items"]
    print(f"Existing items: {len(items)}")
    for it in items:
        gql('mutation($id:ID!){ delete_item(item_id:$id){ id } }', {"id": it["id"]})
        print(f"  ✗ deleted {it['name']}")
        time.sleep(0.4)

def create_partners():
    q = '''mutation($b:ID!, $name:String!, $cv:JSON!) {
      create_item(board_id:$b, item_name:$name, column_values:$cv) { id }
    }'''
    for p in PARTNERS:
        cv = {
            COL_TYPE: p["type"],
            COL_WEBSITE: {"url": p["website"], "text": p["name"]} if p["website"] else "",
            COL_SHOW: "Yes (donor strip)",
            COL_STATUS: {"label": "Approved"} if False else {"label": "Live"},
        }
        # Skip empty strings — Monday rejects empty link objects
        if not p["website"]: cv.pop(COL_WEBSITE)
        try:
            r = gql(q, {"b": BOARD_ID, "name": p["name"], "cv": json.dumps(cv)})
        except RuntimeError as e:
            # try without status if the label doesn't exist
            if "label" in str(e).lower() or "status" in str(e).lower():
                cv.pop(COL_STATUS, None)
                r = gql(q, {"b": BOARD_ID, "name": p["name"], "cv": json.dumps(cv)})
            else:
                raise
        item_id = r["data"]["create_item"]["id"]
        print(f"  + {p['name']:55} id={item_id}")
        time.sleep(0.5)
        # download & upload logo
        try:
            path = download_logo(p["logo_url"])
            upload_file(item_id, path)
            print(f"      logo uploaded ({path.name})")
        except Exception as e:
            print(f"      ✗ logo failed: {e}")
        time.sleep(0.5)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "delete-only":
        delete_all_existing()
    elif cmd == "create-only":
        create_partners()
    else:
        delete_all_existing()
        print()
        create_partners()
