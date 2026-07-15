#!/usr/bin/env python3
"""Create the Team Tasks board at the root of Main workspace.

Cross-project coordination board (not tied to any single content area).
Modeled on the existing 'Magen Salesforce' board's schema (Status, Type,
Notes, Reference Doc, Subitems) but expanded with Assignee, Requestor,
Priority, Due date, and Related board so any task can point at the
board it belongs near without adding a task tracker to every board.

Groups are by domain, mirroring how the SF board organises its own areas.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import requests

WORKSPACE_ID = 4414073  # Main workspace
BOARD_NAME = "Team Tasks"
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"

USERS = {
    "David":  77152892,
    "Shana":  77378283,
    "Rifki":  79016647,
    "Shimon": 82123248,
    "Chana":  96682082,
    "Rikki":  96682085,
}

BOARD_DESC = (
    "Cross-project tasks. Anything that isn't a page, content item, contact, or media entry "
    "lives here. Groups roughly match Magen's work areas. Use the Related-board link column "
    "to point a task at the specific board it references (e.g. the People board for a bio "
    "review). Sub-items for anything that needs breaking down."
)

GROUPS = [
    "Website & Content",
    "Salesforce",
    "Fundraising & Development",
    "Communications & Media",
    "Operations & Admin",
    "People & HR",
    "Backlog / Later",
]

STATUS_LABELS   = ["Not started", "In progress", "Blocked", "In review", "Done", "Cancelled"]
PRIORITY_LABELS = ["Low", "Medium", "High", "Urgent"]
TYPE_LABELS     = ["Review", "Build", "Fix / bug", "Research", "Document", "Meeting", "Decision needed", "Follow-up", "Admin"]

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
    # create board at workspace root (no folder_id)
    r = gql('mutation($n:String!, $w:ID!){ create_board(board_name:$n, board_kind:public, workspace_id:$w){ id } }',
            {"n": BOARD_NAME, "w": WORKSPACE_ID})
    board_id = int(r["data"]["create_board"]["id"])
    print(f"created board id={board_id}")

    try:
        gql('mutation($b:ID!,$d:String!){ update_board(board_id:$b, board_attribute:description, new_value:$d) }',
            {"b": board_id, "d": BOARD_DESC})
        print("  ✓ description set")
    except Exception as e:
        print(f"  ! description skipped: {e}")

    cols_spec = [
        ("Assignee",         "people",   None),
        ("Requestor",        "people",   None),
        ("Status",           "status",   {"labels": {str(i+1): n for i, n in enumerate(STATUS_LABELS)}}),
        ("Priority",         "status",   {"labels": {str(i+1): n for i, n in enumerate(PRIORITY_LABELS)}}),
        ("Type",             "dropdown", {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(TYPE_LABELS)]}}),
        ("Due date",         "date",     None),
        ("Related board",    "link",     None),
        ("Reference doc",    "link",     None),
        ("Notes",            "long_text",None),
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

    # groups
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

    # seed the requested first task
    q_item = '''mutation($b:ID!,$g:String!,$name:String!,$cv:JSON!){
      create_item(board_id:$b, group_id:$g, item_name:$name, column_values:$cv){ id }
    }'''
    cv = {
        col_ids["Assignee"]:      {"personsAndTeams": [{"id": USERS["Shana"], "kind": "person"}]},
        col_ids["Requestor"]:     {"personsAndTeams": [{"id": USERS["David"], "kind": "person"}]},
        col_ids["Status"]:        {"label": "Not started"},
        col_ids["Priority"]:      {"label": "Medium"},
        col_ids["Type"]:          {"labels": ["Review"]},
        col_ids["Related board"]: {"url": "https://magen-israel.monday.com/boards/5100311256", "text": "People board"},
        col_ids["Notes"]:         ("Full team + board directory pulled from the live site. "
                                   "Please check names (EN + HE), roles, and bios; flag anyone missing or moved. "
                                   "Photos and Hebrew bios are already loaded on the board."),
    }
    r = gql(q_item, {"b": board_id, "g": group_ids["Website & Content"],
                     "name": "Review the People board and confirm it's up to date",
                     "cv": json.dumps(cv)})
    print(f"  + seeded task: 'Review the People board…' id={r['data']['create_item']['id']}")

    print(f"\nDone. Board URL: https://magen-israel.monday.com/boards/{board_id}")

if __name__ == "__main__":
    build()
