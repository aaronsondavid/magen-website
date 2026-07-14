#!/usr/bin/env python3
"""Add a 'Class' dropdown to Content Hub separating external media coverage
from Magen's own produced content, then backfill the 316 imported news/media
items with Class = 'News coverage (external)' so tab filters can exclude
them from Ideas/Creation/Library views.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import requests

BOARD_ID = 5100306689
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"

# labels — order matters (index 1 becomes the default label in the UI)
CLASS_LABELS = ["Original content", "News coverage (external)"]

def gql(query, variables=None, retries=4):
    for a in range(retries):
        try:
            r = requests.post(API,
                headers={"Authorization": TOKEN, "Content-Type":"application/json"},
                json={"query": query, "variables": variables or {}}, timeout=45)
            j = r.json()
            if "errors" in j:
                raise RuntimeError(json.dumps(j["errors"]))
            return j
        except Exception as e:
            if a == retries-1: raise
            print(f"  … retry {a+1} ({e})", file=sys.stderr)
            time.sleep(2**a)

def find_or_create_class_col() -> str:
    r = gql('query($b:ID!){ boards(ids:[$b]){ columns{ id title type } } }', {"b": BOARD_ID})
    for c in r["data"]["boards"][0]["columns"]:
        if c["title"] == "Class":
            print(f"  = Class column already exists: {c['id']}")
            return c["id"]
    defaults = {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(CLASS_LABELS)]}}
    q = '''mutation($b:ID!,$t:String!,$ct:ColumnType!,$d:JSON!){
        create_column(board_id:$b, title:$t, column_type:$ct, defaults:$d){ id }
    }'''
    r = gql(q, {"b": BOARD_ID, "t": "Class", "ct": "dropdown", "d": json.dumps(defaults)})
    cid = r["data"]["create_column"]["id"]
    print(f"  + Class (dropdown) → {cid}")
    return cid

def imported_media_item_ids() -> list[str]:
    """Fetch every item on the board — all 316 originals were imported by
    _scripts/media_library_import.py and they're the only current inhabitants,
    so 'all items' == 'items to tag as News coverage'."""
    ids = []
    cursor = None
    while True:
        if cursor:
            q = 'query($b:ID!,$c:String!){ boards(ids:[$b]){ items_page(limit:500, cursor:$c){ cursor items{ id } } } }'
            r = gql(q, {"b": BOARD_ID, "c": cursor})
        else:
            q = 'query($b:ID!){ boards(ids:[$b]){ items_page(limit:500){ cursor items{ id } } } }'
            r = gql(q, {"b": BOARD_ID})
        page = r["data"]["boards"][0]["items_page"]
        ids.extend(it["id"] for it in page["items"])
        cursor = page.get("cursor")
        if not cursor: break
    return ids

def backfill(col_id: str, ids: list[str]):
    q = '''mutation($b:ID!,$i:ID!,$c:String!,$v:JSON!){
      change_column_value(board_id:$b, item_id:$i, column_id:$c, value:$v){ id }
    }'''
    value = json.dumps({"labels": ["News coverage (external)"]})
    ok=0; fail=0
    for n, item_id in enumerate(ids, 1):
        try:
            gql(q, {"b": BOARD_ID, "i": item_id, "c": col_id, "v": value})
            ok += 1
        except Exception as e:
            fail += 1
            print(f"  ✗ {item_id}: {e}", file=sys.stderr)
        if n % 25 == 0:
            print(f"    … {n}/{len(ids)} (ok={ok} fail={fail})")
        time.sleep(0.45)
    print(f"  Done. ok={ok} fail={fail}")

if __name__ == "__main__":
    print("== ensure Class column ==")
    col = find_or_create_class_col()
    print("\n== fetch items to backfill ==")
    ids = imported_media_item_ids()
    print(f"  {len(ids)} items")
    print("\n== backfill Class = News coverage (external) ==")
    backfill(col, ids)
