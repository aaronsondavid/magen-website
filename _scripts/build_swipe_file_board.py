#!/usr/bin/env python3
"""Create the Swipe File board in the Magen Website Content folder.

A cross-channel inspiration library: staff drop in anything they see that
could shape Magen's visuals, copy, layout, or brand. Items graduate from
'Captured' to 'Promote to Ideas', at which point they should be moved to
Content Hub via Monday's built-in Move Item to Board action — column names
are deliberately matched to Content Hub (Owner, Priority, Notes) so the
transfer preserves data.

Groups are by *category* (Visuals, Messaging, Layout, etc.) so the board
scales beyond website work. A *Channel* multi-tag lets the same board serve
socials, newsletter, resources, and fundraising over time.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import requests

FOLDER_ID = 3173106  # Magen Website Content
BOARD_NAME = "Swipe File"
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"

BOARD_DESC = (
    "Cross-channel inspiration library. Anything staff spot that could shape Magen's "
    "visuals, messaging, layout, or brand goes here first, in the group that fits best. "
    "Once we love a swipe enough to build on it, set Status to 'Promote to Ideas', then "
    "right-click the item → Move to → Content Hub (it lands in the Ideas view). Column "
    "names match Content Hub (Owner, Priority, Notes) so the move preserves those fields."
)

# groups = broad categories (kept stable as the board scales beyond website)
GROUPS = [
    "Visuals & imagery",
    "Messaging & copy",
    "Layout & design patterns",
    "Voice & tone",
    "CTAs & conversion",
    "Brand identity",
    "Data & storytelling",
    "General / uncategorised",
]

STATUS_LABELS   = ["Captured", "Under review", "Promote to Ideas", "Used", "Archived"]
PRIORITY_LABELS = ["Low", "Medium", "High"]
CATEGORY_LABELS = GROUPS[:]  # mirror groups so we can filter cross-group
CHANNEL_LABELS  = ["Website", "Instagram", "Facebook", "LinkedIn", "X/Twitter", "TikTok",
                   "YouTube", "Newsletter", "Email", "Resources", "Fundraising", "Event"]

def gql(query, variables=None, retries=4):
    for a in range(retries):
        try:
            r = requests.post(API,
                headers={"Authorization": TOKEN, "Content-Type":"application/json"},
                json={"query": query, "variables": variables or {}}, timeout=45)
            j = r.json()
            if "errors" in j: raise RuntimeError(json.dumps(j["errors"]))
            return j
        except Exception as e:
            if a == retries-1: raise
            print(f"  … retry {a+1} ({e})", file=sys.stderr)
            time.sleep(2**a)

def build():
    # 1. create board
    r = gql('mutation($n:String!, $f:ID!){ create_board(board_name:$n, board_kind:public, folder_id:$f){ id } }',
            {"n": BOARD_NAME, "f": FOLDER_ID})
    board_id = int(r["data"]["create_board"]["id"])
    print(f"created board id={board_id}")

    # 2. board description
    try:
        gql('mutation($b:ID!,$d:String!){ update_board(board_id:$b, board_attribute:description, new_value:$d) }',
            {"b": board_id, "d": BOARD_DESC})
        print("  ✓ description set")
    except Exception as e:
        print(f"  ! description skipped: {e}")

    # 3. columns
    cols_spec = [
        ("Source URL",           "link",     None),
        ("Screenshot",           "file",     None),
        ("Category",             "dropdown", {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(CATEGORY_LABELS)]}}),
        ("Channel",              "tags",     None),
        ("Why it works",         "long_text",None),
        ("How we could use it",  "long_text",None),
        ("Status",               "status",   {"labels": {str(i+1): n for i, n in enumerate(STATUS_LABELS)}}),
        ("Owner",                "people",   None),
        ("Priority",             "status",   {"labels": {str(i+1): n for i, n in enumerate(PRIORITY_LABELS)}}),
        ("Freeform tags",        "tags",     None),
        ("Date added",           "date",     None),
        ("Related Content Hub item", "link", None),  # link column since board_relation isn't API-creatable
        ("Notes",                "long_text",None),
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

    # 4. groups: rename first default, delete other defaults, create the rest in order
    r = gql('query($b:ID!){ boards(ids:[$b]){ groups{ id title } } }', {"b": board_id})
    default_groups = r["data"]["boards"][0]["groups"]
    group_ids: dict[str,str] = {}
    if default_groups:
        first = default_groups[0]
        time.sleep(0.5)
        gql('mutation($b:ID!,$g:String!,$n:String!){ update_group(board_id:$b, group_id:$g, group_attribute:title, new_value:$n){ id } }',
            {"b": board_id, "g": first["id"], "n": GROUPS[0]})
        group_ids[GROUPS[0]] = first["id"]
        for g in default_groups[1:]:
            time.sleep(0.5)
            gql('mutation($b:ID!,$g:String!){ delete_group(board_id:$b, group_id:$g){ id } }',
                {"b": board_id, "g": g["id"]})
    for g in GROUPS[1:]:
        time.sleep(0.5)
        r = gql('mutation($b:ID!,$n:String!){ create_group(board_id:$b, group_name:$n){ id } }',
                {"b": board_id, "n": g})
        group_ids[g] = r["data"]["create_group"]["id"]
        print(f"  + group {g}")

    # 5. one seeded "how to use this board" item at the top so it's not empty on first open
    seed_desc = (
        "This board is our shared library of things worth stealing (well, adapting). "
        "When you see a page, ad, headline, illustration, or piece of copy that could shape "
        "Magen's work, add it here in the group that fits best. Include the source URL, a "
        "screenshot if useful, and one line on 'why it works'. When we're ready to actually "
        "act on a swipe, flip Status to 'Promote to Ideas' and Move → Content Hub."
    )
    q_item = '''mutation($b:ID!,$g:String!,$name:String!,$cv:JSON!){
      create_item(board_id:$b, group_id:$g, item_name:$name, column_values:$cv){ id }
    }'''
    cv = {
        col_ids["Category"]:      {"labels": ["General / uncategorised"]},
        col_ids["Why it works"]:  seed_desc,
        col_ids["Status"]:        {"label": "Captured"},
        col_ids["Priority"]:      {"label": "Low"},
    }
    gql(q_item, {"b": board_id, "g": group_ids["General / uncategorised"],
                 "name": "📌 How to use this board (read me)", "cv": json.dumps(cv)})
    print("  + seeded 'how to use this board' item")

    print(f"\nDone. Board URL: https://magen-israel.monday.com/boards/{board_id}")

if __name__ == "__main__":
    build()
