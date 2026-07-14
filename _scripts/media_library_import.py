#!/usr/bin/env python3
"""Read the Website Media Links spreadsheet, normalize & classify each entry,
then either print a dry-run distribution or push everything to a new Monday board.

Usage:
    python3 media_library_import.py dry-run
    python3 media_library_import.py create-board     # creates board + columns + groups
    python3 media_library_import.py import <board_id> <group_map_json>
"""
from __future__ import annotations
import json, os, re, sys, time, urllib.request, urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import openpyxl

XLSX = Path.home() / "Downloads/Website Media Links (1).xlsx"
FOLDER_ID = 3173106  # Magen Website Content folder in Main workspace
BOARD_NAME = "Media Library"
TOKEN = (Path.home() / ".monday_token").read_text().strip()

# ---------- Normalization tables -----------------------------------------------

PLATFORM_ALIASES = {
    # Israeli mainstream
    "ynet": "Ynet", "ynet ": "Ynet", "YNet": "Ynet", "YNET": "Ynet",
    "kan": "Kan", "Kan 11": "Kan", "kan 11": "Kan",
    "channel 10": "Channel 10", "channel 12": "Channel 12",
    "channel 13": "Channel 13", "mako channel 12": "Mako (Channel 12)",
    "chadrei charedim": "Chadrei Charedim", "chredim 10": "Charedim 10",
    "kikar shabbat": "Kikar Shabbat", "kikar hashabat": "Kikar Shabbat",
    "times of israel": "Times of Israel", "israel hayom": "Israel Hayom",
    "jerusalem post": "Jerusalem Post", "the jerusalem post": "Jerusalem Post",
    "haaretz": "Haaretz", "walla": "Walla", "maariv": "Maariv",
    "makor rishon": "Makor Rishon", "arutz 7": "Arutz 7", "arutz sheva": "Arutz 7",
    "kipa": "Kipa", "srugim": "Srugim",
    "jta": "JTA", "globes": "Globes",
}

CHAREDI_RELIGIOUS = {
    "Kikar Shabbat", "Kipa", "Srugim", "Chadrei Charedim", "Charedim 10",
    "Bhadrei Haredim", "Makor Rishon", "Arutz 7", "Hidabroot",
    "Mishpacha", "Yated Neeman", "HaModia", "Hamodia",
}
US_DIASPORA = {
    "JTA", "The Forward", "Forward", "Jewish Week", "Times of Israel",
    "Jerusalem Post", "Tablet", "The Times of Israel",
}
INTERNATIONAL = {
    "ABC Australia", "CBS", "BBC", "The Guardian", "Al Jazeera",
    "Australian Women's Weekly", "The Australian Women's Weekly",
}
TV_PLATFORMS = {
    "Kan", "Channel 10", "Channel 12", "Channel 13", "Mako", "Mako (Channel 12)",
    "Reshet 13", "Keshet 12", "ABC Australia", "CBS", "BBC", "P.TV",
}
RADIO_PLATFORMS = {"Reshet Bet", "Galei Tzahal", "Kan Bet", "Kan Reshet Bet"}

# Keyword → topic tag (multilingual)
TOPIC_KEYWORDS = [
    ("Legislation",         ["חוק ", "חקיקה", "כנסת", "law", "legislat", "bill ", "knesset"]),
    ("Investigation",       ["חקירה", "חוקר", "investigation", "probe"]),
    ("Prevention/Education",["מניעה", "חינוך", "prevention", "educat", "awareness"]),
    ("Community response",  ["קהילה", "community", "congregation", "shul", "synagogue"]),
    ("COVID-era",           ["קורונה", "corona", "covid", "pandemic", "lockdown", "סגר"]),
    ("Individual case",     ["הורשע", "הואשם", "convicted", "charged", "sentenced", "arrest"]),
    ("Lo Tishtok campaign", ["לא תשתוק", "lo tishtok", "lotishtok"]),
    ("Shana / CEO",         ["shana", "aaronson", "שנה ארונסון", "רבקי", "rifki"]),
    ("Advocacy",            ["advocacy", "סנגור", "activist", "פעילות", "lobby"]),
]

# ---------- Data model ---------------------------------------------------------

MEDIA_TYPES = ["News article", "TV / Video", "Radio", "Podcast", "Print", "Social / Blog", "Op-ed", "Interview", "Documentary", "Other"]
LANGS = ["Hebrew", "English", "Other"]
AUDIENCES = ["Israeli mainstream", "Charedi / Religious", "US / Diaspora Jewish", "International non-Jewish"]

@dataclass
class Entry:
    row_idx: int
    title: str
    url: Optional[str]
    platform: Optional[str]
    date_iso: Optional[str]     # YYYY-MM-DD
    year: Optional[str]
    language: str               # Hebrew / English / Other
    excerpt: Optional[str]
    media_type: str
    audience: str
    tags: list[str] = field(default_factory=list)

def normalize_platform(raw: Optional[str]) -> Optional[str]:
    if not raw: return None
    s = str(raw).strip()
    key = s.lower()
    return PLATFORM_ALIASES.get(key, s)

def normalize_lang(raw) -> str:
    if not raw: return "Other"
    s = str(raw).strip().lower()
    if "heb" in s: return "Hebrew"
    if "eng" in s: return "English"
    return "Other"

def classify_media_type(platform: Optional[str], title: str, url: Optional[str]) -> str:
    t = (title or "").lower()
    p = platform or ""
    u = (url or "").lower()
    if any(x in t for x in ["podcast", "פודקסט"]): return "Podcast"
    if "(television)" in t or "(tv)" in t: return "TV / Video"
    if "(radio)" in t: return "Radio"
    if "(print)" in t or "(newspaper)" in t: return "Print"
    if "op-ed" in t or "opinion" in t or "טור" in t: return "Op-ed"
    if "interview" in t or "ראיון" in t: return "Interview"
    if "documentary" in t or "סרט תיעוד" in t: return "Documentary"
    if p in TV_PLATFORMS: return "TV / Video"
    if p in RADIO_PLATFORMS: return "Radio"
    if "facebook.com" in u or "youtube.com" in u or "instagram.com" in u or "twitter.com" in u or "tiktok.com" in u:
        # facebook.com/*/videos/* is often a TV rebroadcast; still tag as Social/Blog
        return "Social / Blog"
    if "blog" in u or "blogs.timesofisrael.com" in u: return "Social / Blog"
    if p: return "News article"
    return "Other"

def classify_audience(platform: Optional[str], lang: str) -> str:
    if not platform:
        return "Israeli mainstream" if lang == "Hebrew" else "US / Diaspora Jewish"
    if platform in CHAREDI_RELIGIOUS: return "Charedi / Religious"
    if platform in INTERNATIONAL:     return "International non-Jewish"
    if platform in US_DIASPORA:       return "US / Diaspora Jewish"
    return "Israeli mainstream"

def extract_tags(title: str, excerpt: Optional[str]) -> list[str]:
    hay = ((title or "") + " " + (excerpt or "")).lower()
    return [tag for tag, kws in TOPIC_KEYWORDS if any(kw in hay for kw in kws)]

def parse_date(v) -> tuple[Optional[str], Optional[str]]:
    """Return (ISO date, year) or (None, None)."""
    if v is None: return None, None
    s = str(v).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m: return f"{m[1]}-{m[2]}-{m[3]}", m[1]
    # try to salvage year at least
    m = re.search(r"(20\d{2})", s)
    return None, m[1] if m else None

# ---------- Excel parsing ------------------------------------------------------

def load_entries() -> list[Entry]:
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["All links"]
    out = []
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        cal, plat, mo, title, lang, excerpt = row[0], row[1], row[2], row[3], row[4], row[5]
        if not (title or cal or plat): continue  # skip blank
        title_str = str(title or cal or "").strip()
        if not title_str: continue
        # detect URL
        url = str(cal).strip() if cal and str(cal).strip().startswith("http") else None
        date_iso, year = parse_date(mo)
        platform = normalize_platform(plat)
        language = normalize_lang(lang)
        mt = classify_media_type(platform, title_str, url)
        aud = classify_audience(platform, language)
        tags = extract_tags(title_str, str(excerpt) if excerpt else "")
        out.append(Entry(
            row_idx=i, title=title_str[:255], url=url, platform=platform,
            date_iso=date_iso, year=year, language=language,
            excerpt=str(excerpt)[:2000] if excerpt else None,
            media_type=mt, audience=aud, tags=tags,
        ))
    return out

# ---------- Monday API ---------------------------------------------------------

def gql(query: str, variables: Optional[dict]=None, retries: int=4) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                "https://api.monday.com/v2", data=body, method="POST",
                headers={"Authorization": TOKEN, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            if attempt == retries - 1: raise
            wait = 2 ** attempt
            print(f"  … retry {attempt+1} after {wait}s ({e})", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("unreachable")

# ---------- Commands -----------------------------------------------------------

def cmd_dry_run():
    entries = load_entries()
    print(f"Loaded {len(entries)} entries")
    from collections import Counter
    mt = Counter(e.media_type for e in entries)
    lg = Counter(e.language for e in entries)
    au = Counter(e.audience for e in entries)
    yr = Counter(e.year or "Undated" for e in entries)
    tg = Counter()
    for e in entries: tg.update(e.tags)
    print("\nMedia Type distribution:")
    for k,v in mt.most_common(): print(f"  {v:4}  {k}")
    print("\nLanguage:")
    for k,v in lg.most_common(): print(f"  {v:4}  {k}")
    print("\nAudience:")
    for k,v in au.most_common(): print(f"  {v:4}  {k}")
    print("\nYear:")
    for k,v in sorted(yr.items()): print(f"  {v:4}  {k}")
    print("\nTopic Tags:")
    for k,v in tg.most_common(): print(f"  {v:4}  {k}")
    print(f"\nEntries missing URL: {sum(1 for e in entries if not e.url)}")
    print(f"Entries missing date: {sum(1 for e in entries if not e.date_iso)}")
    print(f"Entries missing platform: {sum(1 for e in entries if not e.platform)}")

def cmd_create_board():
    entries = load_entries()
    # figure out which media type groups have entries (drop empty ones)
    from collections import Counter
    mt_counts = Counter(e.media_type for e in entries)
    groups_wanted = [mt for mt in MEDIA_TYPES if mt_counts.get(mt, 0) > 0]
    # create board
    m = '''mutation($name:String!, $folder:ID!) {
      create_board(board_name:$name, board_kind:public, folder_id:$folder) { id }
    }'''
    r = gql(m, {"name": BOARD_NAME, "folder": FOLDER_ID})
    board_id = r["data"]["create_board"]["id"]
    print(f"Created board id={board_id}")
    # create columns
    columns = [
        ("URL",              "link",      None),
        ("Publication date", "date",      None),
        ("Platform",         "text",      None),
        ("Language",         "dropdown",  {"settings": {"labels": [{"id":i+1,"name":n} for i,n in enumerate(LANGS)]}}),
        ("Media Type",       "dropdown",  {"settings": {"labels": [{"id":i+1,"name":n} for i,n in enumerate(MEDIA_TYPES)]}}),
        ("Audience",         "dropdown",  {"settings": {"labels": [{"id":i+1,"name":n} for i,n in enumerate(AUDIENCES)]}}),
        ("Topic Tags",       "tags",      None),
        ("Excerpt",          "long_text", None),
    ]
    col_ids = {}
    for title, ctype, defaults in columns:
        time.sleep(0.6)
        args = {"board": int(board_id), "title": title, "col": ctype}
        if defaults:
            q = '''mutation($board:ID!, $title:String!, $col:ColumnType!, $d:JSON!){
                create_column(board_id:$board, title:$title, column_type:$col, defaults:$d){ id title }
            }'''
            args["d"] = json.dumps(defaults)
        else:
            q = '''mutation($board:ID!, $title:String!, $col:ColumnType!){
                create_column(board_id:$board, title:$title, column_type:$col){ id title }
            }'''
        r = gql(q, args)
        cid = r["data"]["create_column"]["id"]
        col_ids[title] = cid
        print(f"  + col {title} ({ctype}) → {cid}")
    # rename default group to first media type, create the rest
    time.sleep(0.6)
    q = '''query($b:ID!){ boards(ids:[$b]){ groups{ id title } } }'''
    r = gql(q, {"b": int(board_id)})
    default_groups = r["data"]["boards"][0]["groups"]
    group_ids: dict[str,str] = {}
    # rename first default group to first media type
    if default_groups and groups_wanted:
        first = default_groups[0]
        time.sleep(0.6)
        gql('mutation($b:ID!,$g:String!,$n:String!){ update_group(board_id:$b, group_id:$g, group_attribute:title, new_value:$n){ id } }',
            {"b": int(board_id), "g": first["id"], "n": groups_wanted[0]})
        group_ids[groups_wanted[0]] = first["id"]
    # delete any other pre-existing default groups
    for g in default_groups[1:]:
        time.sleep(0.6)
        gql('mutation($b:ID!,$g:String!){ delete_group(board_id:$b, group_id:$g){ id } }',
            {"b": int(board_id), "g": g["id"]})
    # create remaining media-type groups
    for mt in groups_wanted[1:]:
        time.sleep(0.6)
        r = gql('mutation($b:ID!,$n:String!){ create_group(board_id:$b, group_name:$n){ id } }',
                {"b": int(board_id), "n": mt})
        group_ids[mt] = r["data"]["create_group"]["id"]
        print(f"  + group {mt} → {group_ids[mt]}")
    manifest = {"board_id": board_id, "columns": col_ids, "groups": group_ids}
    manifest_path = Path(__file__).parent / "media_library_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nWrote manifest → {manifest_path}")
    print(f"Board URL: https://magen.monday.com/boards/{board_id}")

def cmd_import():
    manifest_path = Path(__file__).parent / "media_library_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    board_id = int(manifest["board_id"])
    cols = manifest["columns"]
    groups = manifest["groups"]
    entries = load_entries()
    q = '''mutation($b:ID!, $g:String!, $name:String!, $cv:JSON!) {
      create_item(board_id:$b, group_id:$g, item_name:$name, column_values:$cv) { id }
    }'''
    ok = 0; fail = 0
    for i, e in enumerate(entries, 1):
        gid = groups.get(e.media_type) or groups.get("Other") or next(iter(groups.values()))
        cv = {}
        if e.url:                cv[cols["URL"]] = {"url": e.url, "text": (e.platform or e.title)[:80]}
        if e.date_iso:           cv[cols["Publication date"]] = {"date": e.date_iso}
        if e.platform:           cv[cols["Platform"]] = e.platform
        if e.language:           cv[cols["Language"]] = {"labels": [e.language]}
        if e.media_type:         cv[cols["Media Type"]] = {"labels": [e.media_type]}
        if e.audience:           cv[cols["Audience"]] = {"labels": [e.audience]}
        if e.tags:               cv[cols["Topic Tags"]] = {"tag_names": e.tags}
        if e.excerpt:            cv[cols["Excerpt"]] = e.excerpt
        try:
            gql(q, {"b": board_id, "g": gid, "name": e.title[:255], "cv": json.dumps(cv)})
            ok += 1
        except Exception as ex:
            fail += 1
            print(f"  ✗ row {e.row_idx}: {ex}", file=sys.stderr)
        if i % 25 == 0:
            print(f"  … {i}/{len(entries)} (ok={ok} fail={fail})")
        time.sleep(0.55)
    print(f"\nDone. ok={ok} fail={fail}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "dry-run"
    if cmd == "dry-run":       cmd_dry_run()
    elif cmd == "create-board": cmd_create_board()
    elif cmd == "import":       cmd_import()
    else: print(f"Unknown command: {cmd}"); sys.exit(2)
