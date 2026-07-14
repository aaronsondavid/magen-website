#!/usr/bin/env python3
"""Create the 'Graphics' board in Magen Website Content folder and load Rifki's
initial 27 graphic ideas with section/page grouping.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import openpyxl, requests

XLSX = Path.home() / "Downloads/Graphic Ideas (1).xlsx"
FOLDER_ID = 3173106  # Magen Website Content
BOARD_NAME = "Graphics"
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"

# ---- schema -------------------------------------------------------------------

# groups by main page/section
GROUPS = [
    "Homepage",
    "In an Emergency",
    "Safety & Healing",
    "Advocacy & Investigations",
    "Education & Community",
    "About Us",
    "Donate",
    "Cross-page / General",
]

STATUS_LABELS = ["Idea", "Briefed", "In Progress", "Review", "Approved", "Delivered", "Not needed"]
PRIORITY_LABELS = ["Low", "Medium", "High"]
TYPE_LABELS = [
    "Illustration", "Photo (studio/staged)", "Photo (candid)",
    "Icon", "Composite / mixed", "Abstract graphic", "Headshot", "Video", "Signage / photo of place",
]
FORMAT_LABELS = ["SVG", "PNG", "JPG", "WebP", "MP4", "GIF"]

# ---- classify each row to a group ---------------------------------------------

def classify(section: str) -> str:
    s = (section or "").lower()
    if "hadar 4" in s or "heder" in s or "emergency" in s: return "In an Emergency"
    if "homepage" in s or "home page" in s or "impact section" in s or "phone call" in s or "stay informed" in s: return "Homepage"
    if "muganut" in s or "peer support" in s or "healing" in s or "shapiro" in s or "schapiro" in s: return "Safety & Healing"
    if "livui" in s or "chakirot" in s or "police" in s or "knesset" in s or "teacher story" in s: return "Advocacy & Investigations"
    if "mudaut" in s or "kehilla" in s or "chinuch" in s or "community" in s or "yaakov" in s: return "Education & Community"
    if "about us" in s or "board meeting" in s or "staff meeting" in s: return "About Us"
    if "donate" in s: return "Donate"
    return "Cross-page / General"

def infer_type(desc: str) -> str:
    d = (desc or "").lower()
    if "headshot" in d: return "Headshot"
    if "icon" in d: return "Icon"
    if "abstract" in d or "flashback" in d or "maelstrom" in d: return "Abstract graphic"
    if "sign" in d or "sign," in d or "signage" in d: return "Signage / photo of place"
    if "silhouette" in d or "character" in d or "graphic of" in d or "stick man" in d or "question mark" in d or "megaphone" in d or "heartbeat" in d or "podcast mike" in d or "email graphic" in d: return "Illustration"
    if "video" in d: return "Video"
    if "pic at" in d or "one pic" in d: return "Photo (candid)"
    if "someone " in d or "teenager " in d or "child" in d or "women in" in d or "dad and mum" in d or "teacher closing" in d or "rabbi character" in d: return "Illustration"
    return "Illustration"

# ---- API ---------------------------------------------------------------------

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

# ---- Load rows ---------------------------------------------------------------

def load_items():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Sheet1"]
    items = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        graphic, section = row[0], row[1]
        # skip fully blank rows
        if not graphic and not section: continue
        name = (str(graphic).strip() if graphic else "").rstrip('.')
        sect = str(section).strip() if section else ""
        if not name and not sect: continue
        # if graphic is blank but section is present (row 17 "Emergency pull down"), use section as name
        if not name:
            name = sect
            sect = ""
        # truncate item name for Monday (255 chars max)
        display = name[:120] + ("…" if len(name) > 120 else "")
        items.append({
            "name": display,
            "full_desc": name,
            "section_raw": sect,
            "group": classify(sect if sect else name),
            "type": infer_type(name),
        })
    return items

# ---- Build board -------------------------------------------------------------

def build():
    items = load_items()
    print(f"Loaded {len(items)} items")

    # create board
    r = gql('mutation($n:String!, $f:ID!){ create_board(board_name:$n, board_kind:public, folder_id:$f){ id } }',
            {"n": BOARD_NAME, "f": FOLDER_ID})
    board_id = int(r["data"]["create_board"]["id"])
    print(f"created board id={board_id}")

    # columns
    cols_spec = [
        ("Section / location", "text", None),
        ("Description",       "long_text", None),
        ("Status",            "status", {"labels": {str(i+1): n for i, n in enumerate(STATUS_LABELS)}}),
        ("Type",              "dropdown", {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(TYPE_LABELS)]}}),
        ("Owner",             "people", None),
        ("Assigned to",       "people", None),
        ("Priority",          "status", {"labels": {str(i+1): n for i, n in enumerate(PRIORITY_LABELS)}}),
        ("Delivery format",   "tags", None),
        ("Reference / brief", "link", None),
        ("Draft file link",   "link", None),
        ("Final asset",       "file", None),
        ("Due date",          "date", None),
        ("Notes",             "long_text", None),
    ]
    col_ids = {}
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

    # groups: rename default to first, delete extras, create the rest in order
    r = gql('query($b:ID!){ boards(ids:[$b]){ groups{ id title } } }', {"b": board_id})
    default_groups = r["data"]["boards"][0]["groups"]
    group_ids: dict[str, str] = {}
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

    # items
    q_item = '''mutation($b:ID!,$g:String!,$name:String!,$cv:JSON!){
      create_item(board_id:$b, group_id:$g, item_name:$name, column_values:$cv){ id }
    }'''
    for it in items:
        cv = {
            col_ids["Section / location"]: it["section_raw"] or "",
            col_ids["Description"]:        it["full_desc"],
            col_ids["Status"]:             {"label": "Idea"},
            col_ids["Type"]:               {"labels": [it["type"]]},
            col_ids["Priority"]:           {"label": "Medium"},
        }
        try:
            r = gql(q_item, {"b": board_id, "g": group_ids[it["group"]],
                             "name": it["name"], "cv": json.dumps(cv)})
            print(f"  + [{it['group']:26}] {it['name'][:60]}")
        except Exception as e:
            print(f"  ✗ {it['name']}: {e}")
        time.sleep(0.5)

    print(f"\nDone. Board URL: https://magen-israel.monday.com/boards/{board_id}")

if __name__ == "__main__":
    build()
