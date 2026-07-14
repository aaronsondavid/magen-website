#!/usr/bin/env python3
"""Migrate the Media Library board into a full Content Hub:
  - rename board
  - add pipeline Status + production columns + board_relations + 4 optional columns
  - backfill all existing items with Content Status = Published
  - create Ideas / Creation / Library views (tabs)
"""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
import requests

BOARD_ID = 5100306689
CTAS_BOARD_ID = 5099963376
WEBSITE_BOARD_ID = 2001198672
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"

STATUS_LABELS = ["Ideation", "Scoped", "In Progress", "Review", "Approved", "Scheduled", "Published", "Archived"]
PRIORITY_LABELS = ["Low", "Medium", "High", "Urgent"]
CAMPAIGN_LABELS = ["Lo Tishtok", "Fundraising", "End of Year", "Advocacy push", "Prevention/Education", "General"]
LANG_TARGET_LABELS = ["Hebrew", "English", "Both"]
PERSONA_LABELS = ["Survivor", "Family/Friends", "Professional", "Community leader", "Donor", "General public"]
DISTRIBUTION_LABELS = ["Instagram", "Facebook", "X/Twitter", "LinkedIn", "TikTok", "YouTube", "Newsletter", "WhatsApp", "Website"]

def gql(query, variables=None, retries=3):
    for a in range(retries):
        r = requests.post(API,
            headers={"Authorization": TOKEN, "Content-Type":"application/json", "API-Version":"2024-01"},
            json={"query": query, "variables": variables or {}}, timeout=30)
        j = r.json() if r.status_code == 200 else None
        if j and "data" in j and not j.get("errors"):
            return j
        if a == retries-1:
            print("Error response:", r.status_code, r.text[:500], file=sys.stderr)
            raise RuntimeError(f"GraphQL failed: {j.get('errors') if j else r.text}")
        time.sleep(2**a)

def rename_board():
    # BoardAttributes enum uses unquoted lowercase 'name'
    q = 'mutation($b:ID!,$name:String!){ update_board(board_id:$b, board_attribute:name, new_value:$name) }'
    try:
        r = gql(q, {"b": BOARD_ID, "name": "Content Hub"})
        print(f"  ✓ renamed board → Content Hub")
    except Exception as e:
        print(f"  ! board rename via API failed ({e}) — rename manually in UI")

def add_columns():
    """Idempotent: skip a column if one with the same title already exists."""
    # fetch existing columns
    r = gql('query($b:ID!){ boards(ids:[$b]){ columns{ id title type } } }', {"b": BOARD_ID})
    existing = {c["title"]: c["id"] for c in r["data"]["boards"][0]["columns"]}
    print(f"  existing columns: {list(existing.keys())}")

    specs = [
        ("Content Status",  "status",         {"labels": {str(i+1): n for i, n in enumerate(STATUS_LABELS)}}),
        ("Owner",           "people",         None),
        ("Approver",        "people",         None),
        ("Draft doc",       "link",           None),
        ("Working folder",  "link",           None),
        ("Preview URL",     "link",           None),
        ("Website page",    "board_relation", {"boardIds": [WEBSITE_BOARD_ID]}),
        ("CTA / Lead Magnet","board_relation",{"boardIds": [CTAS_BOARD_ID]}),
        ("Related campaign","dropdown",       {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(CAMPAIGN_LABELS)]}}),
        ("Distribution channels","tags",      None),
        ("Draft due",       "date",           None),
        ("Publish/schedule date","date",      None),
        ("Priority",        "status",         {"labels": {str(i+1): n for i, n in enumerate(PRIORITY_LABELS)}}),
        ("Assets",          "file",           None),
        ("Blockers / Notes","long_text",      None),
        ("Language target", "dropdown",       {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(LANG_TARGET_LABELS)]}}),
        ("Persona",         "dropdown",       {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(PERSONA_LABELS)]}}),
        ("Word/duration target","numbers",    None),
        ("Series / thread", "text",           None),
    ]
    ids = {}
    for title, ctype, defaults in specs:
        if title in existing:
            ids[title] = existing[title]
            print(f"  = kept existing: {title}")
            continue
        time.sleep(0.5)
        if defaults:
            q = '''mutation($b:ID!, $t:String!, $ct:ColumnType!, $d:JSON!){
                create_column(board_id:$b, title:$t, column_type:$ct, defaults:$d){ id title }
            }'''
            args = {"b": BOARD_ID, "t": title, "ct": ctype, "d": json.dumps(defaults)}
        else:
            q = '''mutation($b:ID!, $t:String!, $ct:ColumnType!){
                create_column(board_id:$b, title:$t, column_type:$ct){ id title }
            }'''
            args = {"b": BOARD_ID, "t": title, "ct": ctype}
        try:
            r = gql(q, args)
            cid = r["data"]["create_column"]["id"]
            ids[title] = cid
            print(f"  + {title} ({ctype}) → {cid}")
        except Exception as e:
            print(f"  ✗ failed to create '{title}': {e}")
    # save manifest
    manifest = Path(__file__).parent / "content_hub_manifest.json"
    manifest.write_text(json.dumps({"board_id": BOARD_ID, "columns": ids}, indent=2))
    print(f"  → manifest saved to {manifest}")
    return ids

def backfill_status(status_col_id: str):
    """Set Content Status = Published on all existing items (no null-check — safe to overwrite)."""
    # Fetch all item ids
    all_ids = []
    cursor = None
    while True:
        if cursor:
            q = 'query($b:ID!, $c:String!){ boards(ids:[$b]){ items_page(limit:500, cursor:$c){ cursor items{ id } } } }'
            r = gql(q, {"b": BOARD_ID, "c": cursor})
        else:
            q = 'query($b:ID!){ boards(ids:[$b]){ items_page(limit:500){ cursor items{ id } } } }'
            r = gql(q, {"b": BOARD_ID})
        page = r["data"]["boards"][0]["items_page"]
        all_ids.extend(it["id"] for it in page["items"])
        cursor = page.get("cursor")
        if not cursor: break
    print(f"  found {len(all_ids)} items to backfill")
    q = '''mutation($b:ID!, $i:ID!, $c:String!, $v:JSON!) {
      change_column_value(board_id:$b, item_id:$i, column_id:$c, value:$v){ id }
    }'''
    ok=0; fail=0
    for i, item_id in enumerate(all_ids, 1):
        try:
            gql(q, {"b": BOARD_ID, "i": item_id, "c": status_col_id, "v": json.dumps({"label": "Published"})})
            ok += 1
        except Exception as e:
            fail += 1
            print(f"  ✗ {item_id}: {e}", file=sys.stderr)
        if i % 25 == 0:
            print(f"    … {i}/{len(all_ids)} (ok={ok} fail={fail})")
        time.sleep(0.45)
    print(f"  Done. ok={ok} fail={fail}")

def create_views():
    """Create Ideas / Creation / Library views (tabs). Filter setup is UI-only."""
    q = '''mutation($b:ID!, $n:String!, $k:BoardViewType!) {
      create_board_view(board_id:$b, view_name:$n, view_type:$k){ id name }
    }'''
    for name, kind in [("Ideas", "table"), ("Creation", "kanban"), ("Library", "table")]:
        try:
            r = gql(q, {"b": BOARD_ID, "n": name, "k": kind})
            print(f"  + view '{name}' ({kind}) → {r['data']['create_board_view']['id']}")
        except Exception as e:
            print(f"  ! view '{name}' via API failed: {e}")
            print("    (create manually in UI: + View → {kind} → name it)".replace('{kind}', kind))
        time.sleep(0.5)

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("all", "rename"):
        print("== rename =="); rename_board()
    if step in ("all", "columns"):
        print("\n== columns ==")
        ids = add_columns()
    if step in ("all", "backfill"):
        print("\n== backfill Content Status = Published ==")
        manifest = json.loads((Path(__file__).parent / "content_hub_manifest.json").read_text())
        status_col = manifest["columns"].get("Content Status")
        if not status_col:
            print("  ! Content Status column id not found in manifest — skipping backfill")
        else:
            backfill_status(status_col)
    if step in ("all", "views"):
        print("\n== views ==")
        create_views()
