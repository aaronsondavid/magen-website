#!/usr/bin/env python3
"""Create the 'People' board in the Magen Website Content folder and populate it
with 17 team + board members scraped from magen-israel.org.

Groups: Staff · Board of Directors · Board of Advisors · Committee
Columns: Name (item) · Role · Type · Photo (file) · Bio (long text) · Bio EN
         · Email · LinkedIn · Live URL · Show on site · Notes · Status
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import requests

FOLDER_ID = 3173106  # Magen Website Content
TOKEN = (Path.home() / ".monday_token").read_text().strip()
API = "https://api.monday.com/v2"
FILE_API = "https://api.monday.com/v2/file"
CACHE = Path("/tmp/magen-people/logos"); CACHE.mkdir(parents=True, exist_ok=True)

TYPES  = ["Staff", "Board of Directors", "Board of Advisors", "Committee"]
STATUS = ["Draft", "Approved", "Live", "Hidden"]

# ---- curated people list ------------------------------------------------------
# Order = order shown on the live site. Bios are the full Hebrew paragraphs
# from magen-israel.org (edited only to strip trailing site-chrome). Roles are
# separated from name+bio.

PEOPLE = [
    # STAFF (8) — from /הצוות-שלנו/
    {
        "name": "Shana Aaronson",
        "name_he": "שאנה אהרנסון",
        "role": "Executive Director / מנהלת",
        "type": "Staff",
        "bio_he": ("שאנה היא בעלת תואר Bs. בפסיכולוגיה, כמו גם הסמכה והכשרה בייעוץ לליווי חינוכי, "
                   "מניעת התעללות וטיפול IFS. ניסיונה החל בהדרכת נוער בסיכון במספר תוכניות. היא הייתה עוזרת מנהלת "
                   'ב"צופיה", בית מגורים טיפולי לנערות מתבגרות, בו פיקחה על הצוות, הנחתה מפגשי קבוצת DBT וריכזה '
                   'את הצרכים האדמיניסטרטיביים של המרכז. היא הפכה לרכזת השירותים החברתיים של "מגן" בתחום הגנת ילדים, '
                   'אחר כך התקדמה למנהלת טיפול, ולאחר מכן מנהלת "מגן". שאנה מתנדבת כמאמנת לדיני אישות יהודיים ועוזרת '
                   "לידה לנשים עם היסטוריה של פגיעה מינית ונפגעות אלימות. היא מתגוררת עם משפחתה במטה יהודה, ישראל."),
        "photo": "https://magen-israel.org/wp-content/uploads/2021/12/IMG_4110.JPG-scaled-e1639870630400-1024x1024.jpg",
    },
    {
        "name": "Esther Horowitz",
        "name_he": "אסתר הורוביץ",
        "role": "Clinical Director / מנהלת קלינית",
        "type": "Staff",
        "bio_he": ("אסתר הורוביץ בעלת B.A. בחינוך מיוחד M.A. בטיפול במוזיקה - אוניברסיטת בר אילן. הכשרות והתמחות "
                   "בטיפול בהורים, פעוטות, ילדים ונוער בתחום הפגיעות המיניות. נפגעים, בעלי התנהגות מינית לא מותאמת "
                   'או פוגענית. בעלת רקע וניסיון טיפולי וניהולי בטיפול בטראומה. בעברה הקימה וניהלה את מרכז "מיטל" '
                   "בביתר עילית. בתהליך הכשרה לטיפול זוגי משפחתי ומיני ברותם. גרה עם משפחתה בירושלים."),
        "photo": "https://magen-israel.org/wp-content/uploads/2023/04/WhatsApp-Image-2023-04-30-at-11.03.20-1-e1682955660101-300x300.jpeg",
    },
    {
        "name": "Sigal Gabai",
        "name_he": "סיגל גבאי",
        "role": "Intake Coordinator / רכזת אינטייק",
        "type": "Staff",
        "bio_he": ("לסיגל תואר ראשון בחינוך מאוניברסיטת Western Ontario ותואר שני בחינוך עם התמקדות בחינוך מיוחד "
                   "ופסיכולוגיה חינוכית ממקגיל. סיגל מוסמכת לטיפול במערכות משפחתיות, עובדת שנים רבות בחינוך וייעוץ "
                   "בנושא בטיחות נגד התעללות מינית בקנדה ולאחר מכן בישראל דרך משרד החינוך. סיגל מתגוררת עם בן זוגה "
                   "וילדיה בבית שמש."),
        "photo": "https://magen-israel.org/wp-content/uploads/2021/12/Cigal-e1639870710557.jpeg",
    },
    {
        "name": "Shimon Bell",
        "name_he": "שמעון בל",
        "role": "Advocacy & Investigations Coordinator / רכז ליווי וחקירות",
        "type": "Staff",
        "bio_he": ('שמעון עלה לארץ כילד מארה"ב ולאחר שנותיו בישיבה שירת ביחידת "נצח" בצה"ל כחובש קרבי. הוא בעל תואר '
                   "ראשון במדעי ההתנהגות ופסיכולוגיה מאוניברסיטת אריאל, הכשרה לאחר תואר בפרופילאות פלילית, וסיים "
                   "את התמחותו בבית החולים הפסיכיאטרי אברבנאל. שמעון מסיים בימים אלה את התואר השני בקרימינולוגיה "
                   "קלינית באוניברסיטת בר אילן. הוא מתגורר עם בת זוגו באזור ירושלים."),
        "photo": "https://magen-israel.org/wp-content/uploads/2021/12/Shimon-e1639870740985.jpeg",
    },
    {
        "name": "Riki Weiss",
        "name_he": "ריקי וויס",
        "role": "Advocacy & Investigations Coordinator / רכזת ליווי וחקירות",
        "type": "Staff",
        "bio_he": ("ריקי בעלת תואר ראשון בקרימינולוגיה בהצטיינות מג'ון ג'יי קולג בניו יורק. היא עבדה בעבר במוסד גמילה "
                   "מהתמכרויות ועם נוער בסיכון. לאחרונה סיימה תואר שני בפשיעה גלובלית, צדק, וביטחון מאוניברסיטת "
                   "אדינבורו בסקוטלנד. ריקי חזרה לארץ לאחרונה ומתגוררת בבית שמש בימים אלו."),
        "photo": "https://magen-israel.org/wp-content/uploads/2023/10/WhatsApp-Image-2023-10-29-at-18.05.29-e1698595790775-300x300.jpeg",
    },
    {
        "name": "Yaakov Sela",
        "name_he": "יעקב סלע",
        "role": "Head of PR & Communications / מנהל דוברות וקשרי ציבור",
        "type": "Staff",
        "bio_he": ("ליעקב יש B.A בתקשורת וM.A. במשפטים, שניהם מאוניברסיטת בר אילן. את עבודתו בארגון החל בשנת 2018, "
                   "לאחר שהסתייע בעצמו בארגון לחשיפת הפגיעה בו. מאז ועד היום מלווה יעקב את כל הצד התקשורתי אסטרטגי "
                   "של הארגון, מלווה את הנפגעים המעוניינים להוציא את סיפורם לאור, וניהל את האסטרטגיה התקשורתית סביב "
                   "הפרשיות הגדולות בהם עסק הארגון כגון פרשיות מלכה לייפר ויהודה משי זהב."),
        "photo": "https://magen-israel.org/wp-content/uploads/2023/08/IMG-20221003-WA0017-e1691936001236-300x300.jpg",
    },
    {
        "name": "Mikey Susan",
        "name_he": "מייקי סוסאן",
        "role": "Head of Education & Research / מנהלת חינוך ומחקר",
        "type": "Staff",
        "bio_he": ("כנערה, מייקי סוסאן החלה לדבר בפומבי על התעללות בקהילה היהודית האורתודוקסית, וכך החלה את הקריירה "
                   'שלה כאקטיביסטית. בגיל 16 עלתה מניו ג\'רזי, ושירתה כקצינה בצה"ל במשך 3 שנים. מייקי למדה תואר ראשון '
                   "משותף בפסיכולוגיה קלינית וקרימינולוגיה, שם נכנסה לרשימת הדיקן וסיימה את לימודיה בהצטיינות. היא "
                   "זכתה במלגת הנשיא היוקרתית, והחלה לעבוד לקראת תואר שני ודוקטורט משותף בקרימינולוגיה קלינית עם "
                   "התמקדות בטכניקות ראיונות משפטיים, ומתכננת לקדם את הקריירה שלה בתחום חקר הטראומה. מייקי גרה עם "
                   "משפחתה באיזור המרכז."),
        "photo": "https://magen-israel.org/wp-content/uploads/2021/12/mikee-e1639870851359.jpg",
    },
    {
        "name": "Chana Barzel",
        "name_he": "חנה ברזל",
        "role": "Office Manager / מנהלת משרד",
        "type": "Staff",
        "bio_he": ("חנה נולדה בלונדון ועלתה לארץ ב-1995 למושב בשפלה. מתעסקת בתחום ניהול משרד מעל 10 שנים במהלכם עבדה "
                   'במכבי שירותי בריאות, א. שנהב הנדסה ושמאות בע"מ, תצפית נדל"ן וארנון רונד יועצים בע"מ.'),
        "photo": "https://magen-israel.org/wp-content/uploads/2024/05/WhatsApp-Image-2024-05-06-at-12.07.42-e1714986738668-300x300.jpeg",
    },

    # BOARD (9) — from /נאמנים/
    {
        "name": "Sharon Weiss Greenberg",
        "name_he": "שרון וייס גרינברג",
        "role": "Chair of the Board / יו״ר ועד מנהל",
        "type": "Board of Directors",
        "bio_he": ("לשרון ניסיון רב בהגדלת ארגונים במגוון מרכיבים. היא הגדילה את מספר התורמים ורמות הנתינה במספר "
                   "ארגונים, ומאפשרת לארגונים להגדיל את התקציב והיעילות שלהם. היא הביאה כמה עמותות לשלב הבא תוך "
                   "שימוש במיומנויות שיווק, חינוך, תקשורת ושותפויות."),
        "photo": "https://magen-israel.org/wp-content/uploads/2022/01/Sharon.jpeg",
    },
    {
        "name": "Rabbi Yosef Blau",
        "name_he": "הרב יוסף בלאו",
        "role": "Board Member / חבר הנהלה",
        "type": "Board of Directors",
        "bio_he": ("הרב יוסף בלאו סיים את התואר הראשון בקולג' Yeshiva ואת התואר השני שלו בבית הספר ללימודי מדעים "
                   'בבלפר של YU. הוא הוסמך בשנת 1961 ב-RITS של YU ומונה ל"משגיח רוחני" בשנת 1977. הרב בלאו הוא היועץ '
                   "הרוחני בבתי הספר Yeshiva לתואר ראשון."),
        "photo": "https://magen-israel.org/wp-content/uploads/2022/01/Rabbi-Blau.jpeg",
    },
    {
        "name": "Chaim Evers",
        "name_he": "חיים אוורס",
        "role": "Board Member / חבר הנהלה",
        "type": "Board of Directors",
        "bio_he": ("לחיים תעודה בניהול מלונאות מאקדמיית הסחר ההולנדית, הסמכה בדירוג יהלומים מ-IGI ותואר שני בחינוך. "
                   "הוא עבד בבלגיה ובריטניה. חיים עובד כיום כיועץ עסקי. הוא היה מעורב וייעץ באופן פעיל לעמותות, "
                   "ובראשן המועדון בלונדון, שם סייע בפיתוח ארגונים."),
        "photo": "https://magen-israel.org/wp-content/uploads/2022/01/anonymous-avatar-icon-25.png",
        "notes": "No photo on file — anonymous avatar used on live site.",
    },
    {
        "name": "Goldie Levy",
        "name_he": "גולדי לוי",
        "role": "Board Member / חברת הנהלה",
        "type": "Board of Directors",
        "bio_he": ('גולדי גדלה בקהילת חב"ד בצפת, ישראל. היא למדה בקולג\' בארה"ב וסיימה תואר B.A. בפסיכולוגיה '
                   "מאוניברסיטת Yeshiva. במשך 6 שנים, גולדי פיתחה ופיקחה על תוכניות לילדים ונוער בסיכון, ביקרה "
                   "ארגונים המבקשים מענקים, וליוותה ארגונים לא ממשלתיים."),
        "photo": "https://magen-israel.org/wp-content/uploads/2023/09/IMG-20230822-WA0050-300x268.jpg",
    },
    {
        "name": "Gruny Zibin",
        "name_he": "גרוני ציבין",
        "role": "Board Member / חברת הנהלה",
        "type": "Board of Directors",
        "bio_he": ("גרוני קיבלה תואר ראשון בחינוך ופסיכולוגיה לצרכים מיוחדים מ-SUNY, היא מטפלת מוסמכת ABA ובעלת "
                   "תעודת הוראה ממכללת בנק סטריט. ניסיונה של גרוני הוא בעבודה עם ילדים עם צרכים מיוחדים ותיאום "
                   "צהרונים עבור ארגוני נוער קהילתיים."),
        "photo": "https://magen-israel.org/wp-content/uploads/2022/01/Gruny.jpeg",
    },
    {
        "name": "David Weiner",
        "name_he": "דוד ויינר",
        "role": "Board Member / חבר ועד מנהל",
        "type": "Board of Directors",
        "bio_he": ("לדוד יש תואר שני במדעים בהנדסת תעופה וחלל ומכונות מאוניברסיטת פלורידה. הוא עובד עבור ServiceNow "
                   "במחקר מתקדם. דוד מעורב באופן פעיל בקהילה שלו, הוא גייס תרומות עבור Lubavitch באוניברסיטת "
                   'פלורידה ומייסד-שותף של חטיבת האנגלו של "הליכות".'),
        "photo": "https://magen-israel.org/wp-content/uploads/2022/01/David.jpeg",
    },
    {
        "name": "Tzviki Fleishman",
        "name_he": "צביקי פליישמן",
        "role": "Strategic Advisor / חבר ועדה מייעצת - ייעוץ אסטרטגי",
        "type": "Board of Advisors",
        "bio_he": ('צביקי נולד וגדל בשכונת חב"ד בקרית מלאכי. לאחר סיום לימודיו בישיבות בארץ ישראל הוא השתלם בלימודי '
                   'רבנות בבודפשט הונגריה, לאחר מכן פעל כשליח במשך ארבע שנים בבתי חב"ד ברחבי העולם. בעת עבודתו '
                   "כמדריך במעונות בישיבה בירושלים חשף פרשיית התעללות מינית ופעל להעמדתה של הפרשה במרכז השיח הציבורי."),
        "photo": "https://magen-israel.org/wp-content/uploads/2022/01/Tzviki.jpeg",
    },
    {
        "name": "Avraham Katzin",
        "name_he": "אברהם קצין",
        "role": "Financial Audit Committee / ועדת ביקורת פיננסית",
        "type": "Committee",
        "bio_he": ("אברהם קיבל את תואר JF באוניברסיטה למשפטים Benjamin N. Cardozo בניו יורק, וחבר בלשכת עורכי הדין "
                   "בישראל ובניו יורק. הוא החל את הקריירה שלו בחברת ביטוח בניו יורק והתמחה במשפט ביטוחי, תוך הובלת "
                   "צוות התביעות ומשא ומתן."),
        "photo": "https://magen-israel.org/wp-content/uploads/2022/01/Avraham-768x1024.jpeg",
    },
    {
        "name": "Sarah Nadav",
        "name_he": "שרה נדיב",
        "role": "Financial Audit Committee / ועדת ביקורת פיננסית",
        "type": "Committee",
        "bio_he": ("שרה נולדה וגדלה ברוצ'סטר, ניו יורק ועלתה לארץ בשנת 1988. היא קיבלה תואר ראשון במדעי קוגניציה "
                   "וניתוח חברתי מאוניברסיטת Hampshire ותואר שני בניהול ארגונים ללא מטרות רווח מהאוניברסיטה העברית. "
                   "שרה מביאה איתה ניסיון הן במגזר העסקי והן במגזר החברתי."),
        "photo": "https://magen-israel.org/wp-content/uploads/2022/01/Sarah-Nadav-1024x1018.jpeg",
    },
]

# ---- API helpers --------------------------------------------------------------

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

def download(url: str) -> Path:
    fname = url.rsplit("/", 1)[-1]
    safe = "".join(c if c.isascii() and c not in '<>:"|?*' else "_" for c in fname)
    p = CACHE / safe
    if p.exists() and p.stat().st_size > 0: return p
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    p.write_bytes(r.content)
    return p

def upload_file(item_id: str, col_id: str, path: Path):
    query = ('mutation($file: File!, $item: ID!, $col: String!) {'
             '  add_file_to_column(item_id: $item, column_id: $col, file: $file) { id } }')
    files = {
        "query":     (None, query),
        "variables": (None, json.dumps({"file": None, "item": int(item_id), "col": col_id})),
        "map":       (None, json.dumps({"image": ["variables.file"]})),
        "image":     (path.name, path.open("rb"), "application/octet-stream"),
    }
    r = requests.post(FILE_API, headers={"Authorization": TOKEN}, files=files, timeout=90)
    r.raise_for_status()
    j = r.json()
    if "errors" in j: raise RuntimeError(f"upload error: {j['errors']}")
    return j

# ---- Board creation -----------------------------------------------------------

def build():
    # 1. create board in folder
    m = 'mutation($n:String!, $f:ID!){ create_board(board_name:$n, board_kind:public, folder_id:$f){ id } }'
    r = gql(m, {"n": "People", "f": FOLDER_ID})
    board_id = int(r["data"]["create_board"]["id"])
    print(f"created board id={board_id}")

    # 2. columns
    cols_spec = [
        ("Role",         "text",     None),
        ("Type",         "dropdown", {"settings": {"labels": [{"id": i+1, "name": n} for i, n in enumerate(TYPES)]}}),
        ("Photo",        "file",     None),
        ("Bio (Hebrew)", "long_text",None),
        ("Bio (English)","long_text",None),
        ("Email",        "email",    None),
        ("LinkedIn",     "link",     None),
        ("Live URL",     "link",     None),
        ("Show on site", "dropdown", {"settings": {"labels": [{"id": 1, "name": "Yes"}, {"id": 2, "name": "No"}]}}),
        ("Status",       "status",   {"labels": {str(i+1): n for i, n in enumerate(STATUS)}}),
        ("Notes",        "long_text",None),
    ]
    col_ids = {}
    for title, ctype, defaults in cols_spec:
        time.sleep(0.6)
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
        print(f"  + col {title} → {col_ids[title]}")

    # 3. rename default group + create other groups
    r = gql('query($b:ID!){ boards(ids:[$b]){ groups{ id title } } }', {"b": board_id})
    default_groups = r["data"]["boards"][0]["groups"]
    group_ids: dict[str,str] = {}
    if default_groups:
        first = default_groups[0]
        time.sleep(0.5)
        gql('mutation($b:ID!,$g:String!,$n:String!){ update_group(board_id:$b, group_id:$g, group_attribute:title, new_value:$n){ id } }',
            {"b": board_id, "g": first["id"], "n": TYPES[0]})
        group_ids[TYPES[0]] = first["id"]
        # delete extras
        for g in default_groups[1:]:
            time.sleep(0.5)
            gql('mutation($b:ID!,$g:String!){ delete_group(board_id:$b, group_id:$g){ id } }',
                {"b": board_id, "g": g["id"]})
    for t in TYPES[1:]:
        time.sleep(0.5)
        r = gql('mutation($b:ID!,$n:String!){ create_group(board_id:$b, group_name:$n){ id } }',
                {"b": board_id, "n": t})
        group_ids[t] = r["data"]["create_group"]["id"]
        print(f"  + group {t}")

    # 4. create each person + upload photo
    q_item = '''mutation($b:ID!,$g:String!,$name:String!,$cv:JSON!){
      create_item(board_id:$b, group_id:$g, item_name:$name, column_values:$cv){ id }
    }'''
    for p in PEOPLE:
        cv = {
            col_ids["Role"]:          p["role"],
            col_ids["Type"]:          {"labels": [p["type"]]},
            col_ids["Bio (Hebrew)"]:  p["bio_he"],
            col_ids["Show on site"]:  {"labels": ["Yes"]},
            col_ids["Status"]:        {"label": "Live"},
        }
        if "notes" in p: cv[col_ids["Notes"]] = p["notes"]
        try:
            r = gql(q_item, {"b": board_id, "g": group_ids[p["type"]],
                             "name": p["name"], "cv": json.dumps(cv)})
            item_id = r["data"]["create_item"]["id"]
            print(f"  + {p['name']:35} ({p['type']:20}) id={item_id}")
        except Exception as e:
            print(f"  ✗ {p['name']}: {e}")
            continue
        # upload photo
        time.sleep(0.4)
        try:
            path = download(p["photo"])
            upload_file(item_id, col_ids["Photo"], path)
            print(f"      photo uploaded ({path.name})")
        except Exception as e:
            print(f"      ✗ photo upload failed: {e}")
        time.sleep(0.5)

    print(f"\nDone. Board URL: https://magen-israel.monday.com/boards/{board_id}")

if __name__ == "__main__":
    build()
