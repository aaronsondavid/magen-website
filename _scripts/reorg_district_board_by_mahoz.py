#!/usr/bin/env python3
"""Restructure the 'District Directory' Monday board (id 5100388371) into
groups by mahoz, and load all 85 Israeli police stations from
data/districts/israel-police-services.json.

Existing 8 Jerusalem community-admin items are moved into a dedicated
'Jerusalem community admins' group so nothing is lost. The 7 police
mahozot each get their own group.
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

# Groups we want (by mahoz), plus one for the existing community admins
MAHOZ_ORDER = [
    "Jerusalem community admins",
    "מחוז ירושלים",
    "מחוז תל אביב",
    "מחוז מרכז",
    "מחוז חוף",
    "מחוז צפון",
    "מחוז דרום",
    "מחוז ש\"י",
]
# Palette per mahoz (extend on top of the 8 brand tints we already use)
MAHOZ_PALETTE = {
    "Jerusalem community admins": "teal",
    "מחוז ירושלים":               "purple",
    "מחוז תל אביב":                "pink",
    "מחוז מרכז":                  "teal-dk",
    "מחוז חוף":                   "purple-dk",
    "מחוז צפון":                  "teal-lt",
    "מחוז דרום":                  "purple-lt",
    "מחוז ש\"י":                   "pink-dk",
}

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
            print(f"  … retry {a+1} ({e})", file=sys.stderr)
            time.sleep(2**a)

def get_cols_and_groups():
    r = gql('query($b:ID!){ boards(ids:[$b]){ columns{ id title type } groups{ id title } items_page(limit:100){ items{ id name group{ id title } column_values(ids:["_none_"]){ id text } } } } }', {"b": BOARD})
    b = r["data"]["boards"][0]
    cols = {c["title"]: c["id"] for c in b["columns"]}
    groups = {g["title"]: g["id"] for g in b["groups"]}
    items = b["items_page"]["items"]
    return cols, groups, items

def ensure_groups(existing_groups):
    """Rename first default group, delete other defaults, create the rest in order."""
    group_ids = {}
    default_group = None
    # Preserve any group that already matches
    for title in MAHOZ_ORDER:
        if title in existing_groups:
            group_ids[title] = existing_groups[title]

    # Existing group not in our target order → likely the current 'Jerusalem' catch-all — rename it
    surplus = [(t, gid) for t, gid in existing_groups.items() if t not in group_ids.values()]
    # actually correct that check
    surplus = [(t, gid) for t, gid in existing_groups.items() if gid not in group_ids.values() and t not in MAHOZ_ORDER]
    print(f"  existing surplus groups: {[t for t,_ in surplus]}")
    # rename first surplus to first missing target if any
    missing = [t for t in MAHOZ_ORDER if t not in group_ids]
    for (old_title, old_gid), new_title in zip(surplus, missing):
        time.sleep(0.4)
        gql('mutation($b:ID!,$g:String!,$n:String!){ update_group(board_id:$b, group_id:$g, group_attribute:title, new_value:$n){ id } }',
            {"b": BOARD, "g": old_gid, "n": new_title})
        group_ids[new_title] = old_gid
        print(f"  ✓ renamed group '{old_title}' → '{new_title}'")
    # Create the rest
    for title in MAHOZ_ORDER:
        if title in group_ids: continue
        time.sleep(0.4)
        r = gql('mutation($b:ID!,$n:String!){ create_group(board_id:$b, group_name:$n){ id } }',
                {"b": BOARD, "n": title})
        group_ids[title] = r["data"]["create_group"]["id"]
        print(f"  + group '{title}'")
    return group_ids

def move_existing_items_to_jerusalem_admins(group_ids, items):
    """Move the 8 Jerusalem community admins into the dedicated group."""
    target = group_ids["Jerusalem community admins"]
    moved = 0
    for it in items:
        # heuristic: current items are the community admins if their current group is 'Jerusalem'
        # or if we've already got the target group
        if it.get("group",{}).get("id") == target: continue
        time.sleep(0.35)
        try:
            gql('mutation($b:ID!,$i:ID!,$g:String!){ move_item_to_group(item_id:$i, group_id:$g){ id } }',
                {"b": BOARD, "i": it["id"], "g": target})
            moved += 1
        except Exception as e:
            print(f"  ! move {it['name']}: {e}")
    print(f"  ✓ moved {moved} existing items into 'Jerusalem community admins'")

def slug_to_key(slug: str) -> str:
    """External-id form for stations."""
    return f"station.{slug}"

def add_police_stations(cols, group_ids):
    services = json.loads(POLICE_JSON.read_text())["stations"]
    # Existing items by slug to avoid dupes
    r = gql('query($b:ID!){ boards(ids:[$b]){ items_page(limit:500){ items{ id column_values(ids:["' + cols["Slug (external id)"] + '"]){ text } } } } }',
            {"b": BOARD})
    existing_slugs = set()
    for it in r["data"]["boards"][0]["items_page"]["items"]:
        for cv in it["column_values"]:
            if cv["text"]: existing_slugs.add(cv["text"])
    print(f"  existing slugs on board: {len(existing_slugs)}")

    # Column val builders
    def status(l): return {"label": l} if l else None
    def dropdown(l): return {"labels": [l]} if l else None

    q_item = '''mutation($b:ID!,$g:String!,$name:String!,$cv:JSON!){
      create_item(board_id:$b, group_id:$g, item_name:$name, column_values:$cv){ id }
    }'''
    created = skipped = 0
    for s in services:
        slug = slug_to_key(s["slug"])
        if slug in existing_slugs: skipped += 1; continue
        mahoz = s.get("mahoz_he") or ""
        target_group_name = f"מחוז {mahoz}" if not mahoz.startswith("מחוז") else mahoz
        # Map some mahoz name variants
        alias = {
            "ת\"א": "מחוז תל אביב",
            "תל אביב": "מחוז תל אביב",
            "ירושלים": "מחוז ירושלים",
            "מרכז": "מחוז מרכז",
            "חוף": "מחוז חוף",
            "צפון": "מחוז צפון",
            "דרום": "מחוז דרום",
            "ש\"י": "מחוז ש\"י",
        }
        target_group_name = alias.get(mahoz, target_group_name)
        gid = group_ids.get(target_group_name)
        if not gid:
            print(f"  ! no group for '{mahoz}' → skipping {s['name_he']}")
            continue
        cv = {
            cols["Slug (external id)"]:  slug,
            cols["Name (HE)"]:           s.get("name_he",""),
            cols["City"]:                dropdown("Other"),
            cols["Palette"]:             dropdown(MAHOZ_PALETTE.get(target_group_name, "teal")),
            cols["Description"]:         (
                f"{s.get('address','')}"
                + (f"\n📞 {s['phone']}"       if s.get("phone")       else "")
                + (f"\n✉  {s['email']}"       if s.get("email")       else "")
                + (f"\n📠 fax {s['fax']}"     if s.get("fax")         else "")
                + (f"\n🏘️ merhav {s['merhav_he']}" if s.get("merhav_he") else "")
                + ("\n👮 community policing available" if s.get("community_policing") else "")
            ),
            cols["Centre lat"]:          s.get("lat",""),
            cols["Centre lng"]:          s.get("lng",""),
            cols["Publication status"]:  status("Ready to publish"),
        }
        cv = {k: v for k, v in cv.items() if v not in (None, "")}
        try:
            gql(q_item, {"b": BOARD, "g": gid, "name": s.get("name_en") or s.get("name_he"), "cv": json.dumps(cv)})
            created += 1
        except Exception as e:
            print(f"  ✗ {s['name_he']}: {e}")
        time.sleep(0.35)
    print(f"  ✓ created {created} police-station items, skipped {skipped} already present")

def main():
    print("== Loading board state ==")
    cols, groups, items = get_cols_and_groups()
    print(f"  columns: {len(cols)}, groups: {list(groups.keys())}, items: {len(items)}")
    print("\n== Ensuring mahoz groups ==")
    group_ids = ensure_groups(groups)
    print("\n== Moving existing items to 'Jerusalem community admins' ==")
    move_existing_items_to_jerusalem_admins(group_ids, items)
    print("\n== Adding 85 police stations ==")
    add_police_stations(cols, group_ids)
    print("\nDone. Board URL: https://magen-israel.monday.com/boards/5100388371")

if __name__ == "__main__":
    main()
