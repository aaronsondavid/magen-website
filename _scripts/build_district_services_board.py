#!/usr/bin/env python3
"""Sibling flat board for individual district services. One row per service.
Linked to Jerusalem Districts board by 'District slug' text column so the
sync + worker can join without needing an API-uncreatable board_relation.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import requests

FOLDER_ID = 3173106  # Magen Website Content
BOARD_NAME = "Jerusalem Services"
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"

PUB_STATUS = ["Draft", "Ready to publish", "Published", "Retired"]
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

    desc = ("Individual service records (welfare offices, police stations, etc.). "
            "Joined to Jerusalem District Directory by 'District slug' column. "
            "Source of truth is Salesforce District_Service__c.")
    try:
        gql('mutation($b:ID!,$d:String!){ update_board(board_id:$b, board_attribute:description, new_value:$d) }',
            {"b": board_id, "d": desc})
    except Exception as e:
        print(f"  ! description skipped: {e}")

    cols_spec = [
        ("External id",  "text", None),
        ("District slug","text", None),
        ("Service type", "dropdown", {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(SERVICE_TYPES)]}}),
        ("Address",      "text", None),
        ("Phone",        "phone", None),
        ("Alt phone",    "phone", None),
        ("Hours",        "text", None),
        ("Email",        "email", None),
        ("Website",      "link", None),
        ("Notes",        "long_text", None),
        ("Sort order",   "numbers", None),
        ("Publication status", "status", {"labels": {str(i+1): n for i, n in enumerate(PUB_STATUS)}}),
        ("SF Id",        "text", None),
    ]
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
        print(f"  + col {title}")

    # Rename default group to By District
    r = gql('query($b:ID!){ boards(ids:[$b]){ groups{ id title } } }', {"b": board_id})
    for g in r["data"]["boards"][0]["groups"][:1]:
        time.sleep(0.4)
        gql('mutation($b:ID!,$g:String!,$n:String!){ update_group(board_id:$b, group_id:$g, group_attribute:title, new_value:$n){ id } }',
            {"b": board_id, "g": g["id"], "n": "Jerusalem"})

    print(f"\nDone. Board URL: https://magen-israel.monday.com/boards/{board_id}")

if __name__ == "__main__":
    build()
