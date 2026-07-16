#!/usr/bin/env python3
"""Add dedicated per-station columns to the District Directory Monday board
and populate them from israel-police-services.json.

Columns added: Address, Phone, Fax, Email, Station commander.
Existing police-station items (slug starts 'station.') are updated so each
field lives in its own column instead of the Description blob.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import requests

BOARD = 5100388371
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"
ROOT = Path(__file__).resolve().parent.parent
POLICE_JSON = ROOT / "data/districts/israel-police-services.json"

NEW_COLS = [
    ("Address",           "text"),
    ("Phone",             "phone"),
    ("Fax",               "text"),   # phone type is strict; keep fax as text since ~10% are missing
    ("Email",             "email"),
    ("Station commander", "text"),
    ("Merhav",            "text"),
    ("Community policing","status"),
    ("Google Maps",       "link"),
]

def gql(query, variables=None, retries=4):
    for a in range(retries):
        try:
            r = requests.post(API, headers={"Authorization": TOKEN, "Content-Type":"application/json"},
                              json={"query": query, "variables": variables or {}}, timeout=45)
            j = r.json()
            if "errors" in j: raise RuntimeError(json.dumps(j["errors"]))
            return j
        except Exception as e:
            if a == retries-1: raise
            time.sleep(2**a)

def ensure_columns():
    r = gql('query($b:ID!){ boards(ids:[$b]){ columns{ id title type } } }', {"b": BOARD})
    have = {c["title"]: c["id"] for c in r["data"]["boards"][0]["columns"]}
    for title, ctype in NEW_COLS:
        if title in have: print(f"  = {title}"); continue
        time.sleep(0.4)
        if ctype == "status" and title == "Community policing":
            defaults = {"labels": {"1": "yes"}}
            q = '''mutation($b:ID!,$t:String!,$ct:ColumnType!,$d:JSON!){ create_column(board_id:$b, title:$t, column_type:$ct, defaults:$d){ id } }'''
            r = gql(q, {"b": BOARD, "t": title, "ct": ctype, "d": json.dumps(defaults)})
        else:
            q = '''mutation($b:ID!,$t:String!,$ct:ColumnType!){ create_column(board_id:$b, title:$t, column_type:$ct){ id } }'''
            r = gql(q, {"b": BOARD, "t": title, "ct": ctype})
        have[title] = r["data"]["create_column"]["id"]
        print(f"  + {title} → {have[title]}")
    return have

def phone_val(v):
    """Monday's phone column accepts digits-only (no hyphens, no plus, no spaces)."""
    import re
    if not v: return None
    digits = re.sub(r'\D', '', str(v))
    if len(digits) < 6: return None  # not a real phone
    return {"phone": digits, "countryShortName": "IL"}
def email_val(v): return {"email": v, "text": v} if v else None
def link_val(u, t=None): return {"url": u, "text": t or u} if u else None
def status_val(l): return {"label": l} if l else None

def update_stations(cols):
    data = json.loads(POLICE_JSON.read_text())
    # stations is now a dict keyed by slug
    stations_by_slug = {f"station.{slug}": s for slug, s in data["stations"].items()}

    # Fetch board items with slug column value
    slug_col = None
    for c_title in ("Slug (external id)", "Slug"):
        if c_title in cols: slug_col = cols[c_title]; break
    # need to fetch slug column id — refetch full column set
    r = gql('query($b:ID!){ boards(ids:[$b]){ columns{ id title } } }', {"b": BOARD})
    all_cols = {c["title"]: c["id"] for c in r["data"]["boards"][0]["columns"]}
    slug_col = all_cols["Slug (external id)"]
    desc_col = all_cols.get("Description")

    # Page through items
    items = []
    cursor = None
    while True:
        q = ('query($b:ID!,$c:String!){ boards(ids:[$b]){ items_page(limit:200, cursor:$c){ cursor items{ id name column_values(ids:["' + slug_col + '"]){ text } } } } }'
             if cursor else
             'query($b:ID!){ boards(ids:[$b]){ items_page(limit:200){ cursor items{ id name column_values(ids:["' + slug_col + '"]){ text } } } } }')
        r = gql(q, {"b": BOARD, "c": cursor} if cursor else {"b": BOARD})
        page = r["data"]["boards"][0]["items_page"]
        items.extend(page["items"])
        cursor = page.get("cursor")
        if not cursor: break
    print(f"  board has {len(items)} items")

    updated = 0
    q_upd = 'mutation($b:ID!,$i:ID!,$v:JSON!){ change_multiple_column_values(board_id:$b, item_id:$i, column_values:$v){ id } }'
    for it in items:
        slug = it["column_values"][0]["text"] if it["column_values"] else ""
        if not slug or not slug.startswith("station."): continue
        s = stations_by_slug.get(slug)
        if not s: continue
        cv = {}
        if s.get("address"):  cv[cols["Address"]] = s["address"]
        ph = phone_val(s.get("phone"));  em = email_val(s.get("email"))
        if ph: cv[cols["Phone"]] = ph
        if em: cv[cols["Email"]] = em
        if s.get("fax"):      cv[cols["Fax"]] = s["fax"]
        if s.get("commander"):cv[cols["Station commander"]] = s["commander"]
        if s.get("merhav_he"):cv[cols["Merhav"]] = s["merhav_he"]
        if s.get("community_policing"): cv[cols["Community policing"]] = status_val("yes")
        # Nice Google Maps link from lat/lng
        if s.get("lat") and s.get("lng"):
            cv[cols["Google Maps"]] = link_val(f"https://maps.google.com/?q={s['lat']},{s['lng']}",
                                               "Open in Google Maps")
        # Replace bloated Description with just the Hebrew name (cleaner now that fields are proper)
        if desc_col: cv[desc_col] = ""
        try:
            gql(q_upd, {"b": BOARD, "i": it["id"], "v": json.dumps(cv)})
            updated += 1
        except Exception as e:
            print(f"  ✗ {it['name']}: {str(e)[:120]}")
        if updated % 20 == 0 and updated: print(f"    … updated {updated}")
        time.sleep(0.35)
    print(f"  ✓ updated {updated} station items")

def main():
    print("== Adding new columns ==")
    cols = ensure_columns()
    print("\n== Updating station items ==")
    update_stations(cols)
    print("\nDone.")

if __name__ == "__main__":
    main()
