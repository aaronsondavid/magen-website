#!/usr/bin/env python3
"""Publish the district service directory from Monday to the website.

Reads the two Monday boards (Jerusalem District Directory + Jerusalem Services),
composes data/districts/jerusalem-services.json in the shape the website's
find-your-district.html expects, then scp's it to the preview subdomain
(and, when we're ready, prod).

Run manually with `python3 _scripts/publish_districts_from_monday.py`, or
call from the Cloudflare Worker via subprocess after cloning the repo.
"""
from __future__ import annotations
import json, os, subprocess, sys, time
from pathlib import Path
import requests

DISTRICTS_BOARD = 5100388371
SERVICES_BOARD  = 5100388473
TOKEN           = (Path.home() / ".monday_token").read_text().strip()
API             = "https://api.monday.com/v2"
ROOT            = Path(__file__).resolve().parent.parent
OUT_PATH        = ROOT / "data/districts/jerusalem-services.json"

TYPE_TO_KEY = {
    "Welfare office":       "welfare_office",
    "Police station":       "police_station",
    "Community centre":     "community_centre",
    "Emergency reference":  "crisis_reference",
    "Magen coordinator":    "magen_coordinator",
    "Rape crisis centre":   "rape_crisis_centre",
    "Mental health clinic": "mental_health_clinic",
    "Bituach Leumi":        "bituach_leumi",
    "Other":                "other",
}

def gql(query, variables=None, retries=3):
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

def fetch_board(board_id):
    cols = {}
    items = []
    cursor = None
    r = gql('query($b:ID!){ boards(ids:[$b]){ columns{ id title type } } }', {"b": board_id})
    for c in r["data"]["boards"][0]["columns"]:
        cols[c["id"]] = {"title": c["title"], "type": c["type"]}
    while True:
        q = ('query($b:ID!,$c:String){ boards(ids:[$b]){ items_page(limit:100, cursor:$c){ cursor items{ id name column_values{ id text value } } } } }'
             if cursor else
             'query($b:ID!){ boards(ids:[$b]){ items_page(limit:100){ cursor items{ id name column_values{ id text value } } } } }')
        r = gql(q, {"b": board_id, "c": cursor} if cursor else {"b": board_id})
        page = r["data"]["boards"][0]["items_page"]
        for it in page["items"]:
            cv = {}
            for c in it["column_values"]:
                cv[c["id"]] = c["text"]
            items.append({"id": it["id"], "name": it["name"], "cv": cv})
        cursor = page.get("cursor")
        if not cursor: break
    return cols, items

def col_id_by_title(cols, title):
    for cid, meta in cols.items():
        if meta["title"] == title: return cid
    raise KeyError(title)

def compose_payload():
    d_cols, d_items = fetch_board(DISTRICTS_BOARD)
    s_cols, s_items = fetch_board(SERVICES_BOARD)

    slug_col_d = col_id_by_title(d_cols, "Slug (external id)")
    name_he_col = col_id_by_title(d_cols, "Name (HE)")
    pub_col_d = col_id_by_title(d_cols, "Publication status")

    slug_col_s = col_id_by_title(s_cols, "District slug")
    type_col_s = col_id_by_title(s_cols, "Service type")
    pub_col_s = col_id_by_title(s_cols, "Publication status")
    field_map = {
        "External id": "external_id", "Address": "address", "Phone": "phone",
        "Alt phone": "alt_phone", "Hours": "hours", "Email": "email",
        "Website": "website", "Notes": "notes",
    }
    field_ids = {label: col_id_by_title(s_cols, label) for label in field_map}

    # index services by district slug, only if publishable
    svc_by_district: dict[str, dict] = {}
    for s in s_items:
        pub = s["cv"].get(pub_col_s, "")
        if pub not in ("Ready to publish", "Published"): continue
        dslug = s["cv"].get(slug_col_s) or ""
        if not dslug: continue
        stype = s["cv"].get(type_col_s) or "Other"
        key = TYPE_TO_KEY.get(stype, "other")
        svc_by_district.setdefault(dslug, {})
        # If two services share a key, keep the first (real de-dup lives in SF via unique External Id)
        if key in svc_by_district[dslug]: key = f"{key}_2"
        entry = {"name": s["name"]}
        for label, out_key in field_map.items():
            v = s["cv"].get(field_ids[label], "")
            if v: entry[out_key] = v
        svc_by_district[dslug][key] = entry

    # Assemble output matching what find-your-district.html expects
    out = {
        "_meta": {
            "description": "Jerusalem district service directory.",
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "source": "Monday boards 5100388371 + 5100388473 (published via Salesforce -> Monday sync)",
            "district_count": 0,
            "service_count": 0,
        },
        "districts": {}
    }
    for d in d_items:
        if d["cv"].get(pub_col_d) not in ("Ready to publish", "Published"): continue
        slug = d["cv"].get(slug_col_d)
        if not slug: continue
        out["districts"][slug] = svc_by_district.get(slug, {})

    out["_meta"]["district_count"] = len(out["districts"])
    out["_meta"]["service_count"] = sum(len(v) for v in out["districts"].values())
    return out

def deploy_to_preview(local_path):
    """SCP the generated JSON to the preview subdomain via existing SSH alias."""
    remote = "magen-sg:~/www/preview.magen-israel.org/public_html/data/districts/jerusalem-services.json"
    env = {**os.environ, "SSH_ASKPASS": str(Path.home() / ".ssh/.sg_askpass"),
           "SSH_ASKPASS_REQUIRE": "force", "DISPLAY": ":0"}
    subprocess.run(["scp", str(local_path), remote], env=env, check=True)
    subprocess.run(["ssh", "magen-sg",
                    "cd ~/www/preview.magen-israel.org/public_html/data/districts/ && chmod 644 jerusalem-services.json"],
                   env=env, check=True)
    print(f"deployed to preview: {remote}")

def main():
    dry = "--dry-run" in sys.argv
    payload = compose_payload()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT_PATH.relative_to(ROOT)}: {payload['_meta']['district_count']} districts, {payload['_meta']['service_count']} services")
    if dry:
        print("(dry-run — skipping deploy)")
        return
    deploy_to_preview(OUT_PATH)

if __name__ == "__main__":
    main()
