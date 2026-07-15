#!/usr/bin/env python3
"""Create the 'Jerusalem District Directory' board in Magen Website Content.

Structure mirrors Salesforce: one item per District, subitems per Service.
Column schema matches the SF field names so the SF -> Monday sync is a
straight field-for-field push. A dedicated 'Publish to website' status
column is the trigger for the Cloudflare Worker (via Monday Automation).
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import requests

FOLDER_ID = 3173106  # Magen Website Content
BOARD_NAME = "Jerusalem District Directory"
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"

PUB_STATUS = ["Draft", "Ready to publish", "Published", "Retired"]
PUBLISH_TRIGGER = ["Waiting", "Publish now", "Publishing…", "Published", "Failed"]
CITIES = ["Jerusalem", "Bet Shemesh", "Tel Aviv", "Other"]
PALETTE = ["teal", "teal-dk", "teal-lt", "purple", "purple-dk", "purple-lt", "pink", "pink-dk"]
SERVICE_TYPES = ["Welfare office", "Police station", "Community centre",
                 "Emergency reference", "Magen coordinator",
                 "Rape crisis centre", "Mental health clinic", "Bituach Leumi", "Other"]

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

def build():
    r = gql('mutation($n:String!, $f:ID!){ create_board(board_name:$n, board_kind:public, folder_id:$f){ id } }',
            {"n": BOARD_NAME, "f": FOLDER_ID})
    board_id = int(r["data"]["create_board"]["id"])
    print(f"created board id={board_id}")

    desc = ("Directory of city districts and the social services that serve each. "
            "Salesforce is the source of truth; this board is the staff-editable surface. "
            "Set Publish Trigger to 'Publish now' to push the current board state to the website's "
            "data/districts/jerusalem-services.json via the Cloudflare Worker.")
    try:
        gql('mutation($b:ID!,$d:String!){ update_board(board_id:$b, board_attribute:description, new_value:$d) }',
            {"b": board_id, "d": desc})
    except Exception as e:
        print(f"  ! description skipped: {e}")

    # --- Parent (District) columns ---
    cols_spec = [
        ("Slug (external id)", "text", None),
        ("Name (HE)", "text", None),
        ("City", "dropdown", {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(CITIES)]}}),
        ("Palette", "dropdown", {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(PALETTE)]}}),
        ("Centre lat", "numbers", None),
        ("Centre lng", "numbers", None),
        ("Description", "long_text", None),
        ("Publication status", "status", {"labels": {str(i+1): n for i, n in enumerate(PUB_STATUS)}}),
        ("Publish trigger", "status", {"labels": {str(i+1): n for i, n in enumerate(PUBLISH_TRIGGER)}}),
        ("Sort order", "numbers", None),
        ("SF Id", "text", None),
        ("Last published at", "date", None),
        ("Last publish log", "long_text", None),
    ]
    col_ids: dict[str,str] = {}
    for title, ctype, defaults in cols_spec:
        time.sleep(0.5)
        if defaults:
            q = '''mutation($b:ID!,$t:String!,$ct:ColumnType!,$d:JSON!){
                create_column(board_id:$b, title:$t, column_type:$ct, defaults:$d){ id }
            }'''
            args = {"b": board_id, "t": title, "ct": ctype, "d": json.dumps(defaults)}
        else:
            q = '''mutation($b:ID!,$t:String!,$ct:ColumnType!){
                create_column(board_id:$b, title:$t, column_type:$ct){ id }
            }'''
            args = {"b": board_id, "t": title, "ct": ctype}
        r = gql(q, args)
        col_ids[title] = r["data"]["create_column"]["id"]
        print(f"  + col {title}")

    # --- Subitem (Service) columns: get subitem board id, then create ---
    time.sleep(0.5)
    # Trigger subitems creation by creating one and looking up subitem_board
    r = gql('mutation($b:ID!,$n:String!){ create_group(board_id:$b, group_name:$n){ id } }',
            {"b": board_id, "n": "Jerusalem"})
    jer_group = r["data"]["create_group"]["id"]
    # rename existing default group to something clear (or delete extras)
    time.sleep(0.5)
    r = gql('query($b:ID!){ boards(ids:[$b]){ groups{ id title } } }', {"b": board_id})
    for g in r["data"]["boards"][0]["groups"]:
        if g["id"] != jer_group and g["title"] in ("Group Title", "New Group", "Group 1"):
            time.sleep(0.3)
            gql('mutation($b:ID!,$g:String!){ delete_group(board_id:$b, group_id:$g){ id } }',
                {"b": board_id, "g": g["id"]})

    # Add a subitems column so subitem_board is auto-created
    time.sleep(0.5)
    try:
        r = gql('mutation($b:ID!){ create_column(board_id:$b, title:"Subitems", column_type:subtasks){ id } }',
                {"b": board_id})
        subitems_col = r["data"]["create_column"]["id"]
        print(f"  + col Subitems (subtasks) → {subitems_col}")
    except Exception as e:
        print(f"  ! Subitems col: {e}")

    # Fetch subitem board id
    time.sleep(0.5)
    r = gql('''query($b:ID!){ boards(ids:[$b]){ columns{ id title type settings_str } } }''', {"b": board_id})
    subitem_board_id = None
    for c in r["data"]["boards"][0]["columns"]:
        if c["type"] == "subtasks":
            s = json.loads(c["settings_str"]) if c["settings_str"] else {}
            subitem_board_id = (s.get("boardIds") or [None])[0]
            break
    print(f"  subitem board id: {subitem_board_id}")

    # Create service columns on the subitem board (Monday sub-boards can accept most column types)
    if subitem_board_id:
        sub_cols = [
            ("External id", "text", None),
            ("Service type", "dropdown", {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(SERVICE_TYPES)]}}),
            ("Address", "text", None),
            ("Phone", "phone", None),
            ("Alternate phone", "phone", None),
            ("Hours", "text", None),
            ("Email", "email", None),
            ("Website", "link", None),
            ("Notes", "long_text", None),
            ("Sort order", "numbers", None),
            ("Publication status", "status", {"labels": {str(i+1): n for i, n in enumerate(PUB_STATUS)}}),
            ("SF Id", "text", None),
        ]
        for title, ctype, defaults in sub_cols:
            time.sleep(0.5)
            try:
                if defaults:
                    q = '''mutation($b:ID!,$t:String!,$ct:ColumnType!,$d:JSON!){
                        create_column(board_id:$b, title:$t, column_type:$ct, defaults:$d){ id }
                    }'''
                    args = {"b": subitem_board_id, "t": title, "ct": ctype, "d": json.dumps(defaults)}
                else:
                    q = '''mutation($b:ID!,$t:String!,$ct:ColumnType!){
                        create_column(board_id:$b, title:$t, column_type:$ct){ id }
                    }'''
                    args = {"b": subitem_board_id, "t": title, "ct": ctype}
                r = gql(q, args)
                print(f"    + sub-col {title}")
            except Exception as e:
                print(f"    ! sub-col {title}: {e}")

    print(f"\nDone. Board URL: https://magen-israel.monday.com/boards/{board_id}")
    manifest = {"board_id": board_id, "columns": col_ids, "subitem_board_id": subitem_board_id, "group_ids": {"Jerusalem": jer_group}}
    (Path(__file__).parent / "district_directory_manifest.json").write_text(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    build()
