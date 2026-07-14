# CANON — Program Page 1: Safety & Healing (Muganut & Shikum)

> **What this document is.** The authoritative, organized record of the one program page we have already designed and pushed live to the preview site. It captures the page's role, structure, copy (verbatim), design system, reusable components, and open items — so that **Program Page 2 (Advocacy & Investigations)** and **Program Page 3 (Community & Network)** can be drafted to match it. Treat this as the constitution: when we build the next pages, they inherit these rules unless we deliberately amend them.

- **Live source of truth:** <https://preview.magen-israel.org/> (hand-built static HTML, self-contained, base64-embedded images — NOT WordPress/Avada)
- **Local file:** `index.html` in this repo (note: the working copy has uncommitted edits and differs slightly from what is live — the *live* page is the canon captured here)
- **Captured from live on:** 2026-07-07
- **Status:** Preview only. Sticky amber "under construction" banner + `noindex,nofollow,noarchive`.

---

## 1. The three-pillar architecture

The site is organized around **three program pillars**. Each becomes one program page. This page is Pillar 1.

| # | Pillar (nav label) | Hebrew / transliteration | Sub-programs (from the mega-menu) | Status |
|---|---|---|---|---|
| **1** | **Safety & Healing** | מוגנות ושיקום · *Muganut & Shikum* | Crisis Hotline · Case Management · Therapy Referrals · Peer Support Groups · Government Assistance *(coming soon)* | ✅ **Live — this page** |
| 2 | Advocacy & Investigations | — | Legal Support · Investigation Support · Legislative Work | ⏳ Draft pending (Rivky, Google Docs) |
| 3 | Community & Network | — | Community Workshops · Professional Training · Awareness & Prevention | ⏳ Draft pending (Rivky, Google Docs) |

Two further top-level nav sections are **not** program pillars: **Resources** (Blog, Downloadables, Media) and **Magen** (About, Our Team, Financial Transparency, What People Say, Resources). Plus a **Donate** button.

> **Note on scope.** This page currently doubles as the site's landing experience *and* the Safety & Healing program page. Under this canon we treat it as **the Safety & Healing program page**; if a separate homepage is later needed, the hero/voices/book/team/FAQ blocks are the reusable candidates.

---

## 2. Page anatomy (section order & purpose)

The page is a single scroll of stacked full-width sections. This sequence is the **template contract** for sibling pages — same skeleton, pillar-specific content.

| Order | Section | `class` | Purpose | Reusable across pages? |
|---|---|---|---|---|
| 0 | Under-construction banner | inline | Preview-only notice | Preview global (remove at launch) |
| 1 | Crisis bar | `.crisis-bar` | Emergency numbers + Magen hotline, always visible | **Global** (identical on all pages) |
| 2 | Nav + mega-menu | `.nav-wrap` | Sticky nav, 5 dropdowns + Donate | **Global** |
| 3 | Hero (text + image carousel) | `.hero` | Emotional entry: promise of safety + "Talk to us" | **Per-page** (pillar-specific headline/images) |
| 4 | Two stages | `.two-paths` | The pillar's conceptual model — here: Muganut → Shikum | **Per-page** (each pillar has its own 2-stage or N-stage model) |
| 5 | Programs grid | `.programs` | The concrete sub-programs as cards | **Per-page** (cards = that pillar's sub-programs) |
| 6 | Voices / social proof | `.voices` | Testimonials + donor logos | **Global-ish** (shared quote pool; donor strip identical) |
| 7 | Book CTA | `.book-cta` | Promote Helise's book | **Global** (same on all pages) |
| 8 | Team strip | `.team-strip` | Faces of the division | **Per-page** (team = the relevant division's people) |
| 9 | FAQ (schema.org) | `.faq` | SEO/AI-search Q&A | **Per-page** (pillar-specific questions; same schema pattern) |
| 10 | Footer | `footer` | Sitemap, contact, legal | **Global** |

---

## 3. Copy inventory (verbatim canon)

### 3.1 Crisis bar
> If you or someone is in immediate danger, call emergency services now: **Israel: 100** | **US: 911** | **UK: 999** · **Magen hotline:** `[★ CEO to provide]` · 24/6

### 3.2 Hero
- **Eyebrow:** Safety & Healing
- **H1:** *The first step in your journey to healing is **safety**. Safety begins with **being heard**.*
- **Sub:** Whether you're a survivor, family member, or concerned friend — we're here to listen.
- **Primary CTA:** Talk to us → `tel:023724073`
- **Reassurance chips:** ✓ Confidential ✓ Professional ✓ Available 24/6
- **Carousel alts (5 slides):** Support and connection · Community peer support group · Advocacy and legal support · Magen leadership · The journey to healing

### 3.3 Two stages — "Safety & Healing" (מוגנות ושיקום)
Intro: *Whether you're currently in an unsafe space or working your way to healing, Magen is your partner in that journey.*

- **01 · Muganut — "Let's make sure you're safe"**
  Our first priority is ensuring that a victim is out of danger. Whether you're actively subject to abuse or in an unsafe emotional space, we can help you learn your options and make a safety plan. We hear you.
- **02 · Shikum — "Healing from your experience"**
  From a place of safety, you can address the trauma and find healing. The journey to healing is typically complex and confusing. We can help you find the right therapist, navigate the mental health system, learn your rights, and make a plan. You're not alone.
- **Footer line:** We provide case management for ongoing support throughout your journey. → **Talk to us** (`tel:023724073`)

### 3.4 Programs grid — "Muganut & Shikum Programs / How can we help?"
1. **📞 24/6 Crisis Hotline — "Find someone to talk to"** — If something feels wrong or unsafe, call Magen's crisis hotline to speak with someone caring and experienced. You'll learn your options and get immediate support. *(Languages: English, Hebrew, Yiddish)* — CTA: Call now →
2. **🌱 Therapy Referrals — "Find the right therapist"** — Get connected to experienced, trauma-informed therapists offering evidence-based care — matched to your needs, background, and where you are in your journey. — CTA: Find therapy →
3. **👥 Peer Support — "Don't go it alone"** — Join a confidential peer support group for survivors, mothers of survivors, fathers, and spouses. We also innovate with specialized groups: art therapy, trauma-informed yoga, and therapeutic writing. — CTA: Join a group →
4. **📋 Gov't Assistance · Coming Soon — "Navigate your benefits"** — Understand your rights and get guided support navigating Bituach Leumi benefits — which are often difficult to access without someone who knows the system. — CTA: Find out more → *(card dimmed, non-interactive)*

### 3.5 Voices — "People Love Magen"
Intro: *From survivors to social workers, from law enforcement to parents — Magen has earned deep trust from the people it serves and the professionals who work alongside it.*
- **Survivor (real):** "Magen has literally saved many lives. Including my own. Shana was like my own personal cheerleading squad. Continue your avodas hakodesh, Shana and the Magen team. Continue saving lives." — *Anonymous Survivor, Donation message*
- **Placeholder:** Senior Official, Revacha — `[to be provided]`
- **Placeholder:** Parents of a survivor — `[to be provided]`
- **Donor strip ("Supported by"):** Hadassah Foundation · Cross River · Mayberg Foundation · Hirsch Legacy Fund · Israel Gives

### 3.6 Book CTA — "New from Magen"
- **Title:** `[Helise's Book Title]` · **Body:** `[to be provided]` · **CTA:** Get the book →

### 3.7 Team strip — "The People Behind the Work / You're Not Alone"
Intro: *Magen's team of experienced professionals walks with you through every step — with care, expertise, and professionalism.*
- Shana Aaronson — Executive Director
- Sharon Weiss-Greenberg — Chairwoman of the Board
- Rabbi Yosef Blau — Rabbinic Advisor
- Ester Horovits — Clinical Director *(initials placeholder)*
- Rikki Weiss — Investigation Director *(initials placeholder)*
- Link: Meet the full team →
- **Design note in source:** "Team members to be updated with those from the relevant division." → **On sibling pages, swap in that division's people.**

### 3.8 FAQ (13 questions — full verbatim set)
Wrapped in `schema.org/FAQPage` markup for SEO/AI search. Questions:
1. What happens when I contact Magen for the first time?
2. Is Magen's crisis hotline confidential?
3. Does Magen work with rabbis as part of the process?
4. What if I'm not sure if what happened to me was abuse?
5. What if I'm scared to tell anyone or worried about how this could affect my family or community?
6. Do I need to be religious to use Magen's services?
7. Are Magen's services free?
8. How does Magen's case management work?
9. Can you help me navigate legal processes or Bituach Leumi in Israel?
10. What kind of support is available for survivors of sexual abuse in Israel?
11. What mental health support does Magen provide?
12. What if I'm not ready to talk?
- **FAQ micro-CTA:** *If you're unsure where to start, you can reach out by phone, WhatsApp, or email. You don't need to have everything figured out — you can just begin.* → Reach out to Magen → (`tel:STARNUM`)

*(Full answers are preserved verbatim in `index.html` §FAQ; captured here by question. If we edit answers, edit both.)*

### 3.9 Footer
- **Tagline:** Breaking the silence and stigma of sexual abuse. Pursuing justice and healing for survivors across Jewish communities in Israel and beyond.
- **Contact:** 02-372-4073 · support@magen-israel.org · www.magen-israel.org
- **Columns:** Get Help / Advocacy / Magen (see nav taxonomy)
- **Legal:** © 2026 Magen for Jewish Communities. Registered nonprofit. · Privacy Policy · Terms of Use

---

## 4. Design system (the visual constitution)

### 4.1 Color tokens (CSS `:root`)
| Token | Hex | Use |
|---|---|---|
| `--teal` | `#00AEAC` | Primary brand accent, eyebrows, links, stage 02 |
| `--teal-dk` | `#008F8D` | Teal hover |
| `--purple` | `#6B4FA1` | Primary CTA buttons (Donate, Talk to us) |
| `--pink` | `#E879A0` | Tertiary accent (a voice card) |
| `--dark` | `#1A1A2E` | Body text, dark sections (hero, book CTA, footer, crisis bar) |
| `--gray` | `#555` | Secondary body text |
| `--light` | `#F7F7F7` | Alt section backgrounds (programs, FAQ) |

### 4.2 Typography
- **Display / headings:** `Barlow Condensed` (700–900), UPPERCASE, wide letter-spacing. Used for H1/H2/H3, eyebrows, buttons, nav brand.
- **Body:** `Open Sans` (300–700).
- **Hebrew:** falls back to `Frank Ruhl Libre`, serif; Hebrew eyebrow is slightly larger/looser (see `.two-paths-eyebrow[lang="he"]`).
- **Serif accent:** Georgia for the decorative quote mark in voice cards.
- Type scale (desktop): H1 3.8rem · section H2 2.6–2.8rem · stage number 5rem · H3 1.45–1.7rem.

### 4.3 Signature components (reuse these verbatim on sibling pages)
- **Crisis bar** with pulsing teal dot (`@keyframes pulse`).
- **Sticky nav** (72px, 3px teal bottom border) with hover **mega-menus** (some right-aligned to avoid clipping via `:nth-last-child`).
- **Purple primary buttons** (`.btn-primary`), **teal variant** (`.btn-primary--teal`), **outline program buttons** (`.btn-program`), **donate button** (`.btn-donate`).
- **Hero carousel:** absolute-positioned image stack bleeding into a dark gradient zone, diagonal teal overlay (`clip-path`), auto-advance every 4.5s, dot controls (JS at bottom of file).
- **Two-stage grid** with giant Barlow numbers + kicker underline (`.stage-kicker`, teal variant for stage 2).
- **Program cards** with teal top-accent bar on hover, "coming soon" dimmed variant, pill-style language chips (`.program-langs`).
- **Voice cards** with colored left border (teal/purple/pink) + avatar (initials or photo).
- **FAQ accordion** with `schema.org` FAQPage/Question/Answer microdata + `toggleFaq()` JS (single-open behavior).
- Responsive: current CSS is desktop-first; **mobile breakpoints are not yet in the captured page** — see open items.

---

## 5. Voice & tone (derived principles — apply to all pages)
1. **Survivor-centered, second person.** "We hear you." "You're not alone." "You decide the pace."
2. **No pressure, no prerequisites.** "You don't need to prepare anything." "You don't need to be certain before reaching out."
3. **Confidential + honest about limits.** States confidentiality *and* the legal-reporting caveat plainly.
4. **Culturally fluent, not gatekeeping.** Orthodox/traditional context assumed; religion not required. Hebrew/Yiddish/English. Uses "avodas hakodesh," "kuntress," rabbinic collaboration.
5. **Concrete and calm.** Names systems (Bituach Leumi, Revacha, police processes) and offers to navigate them *with* the person.
6. **Trauma-informed clinical framing.** "Trauma-informed," "evidence-based," "case management," "at your own pace."

---

## 6. Open items / placeholders ledger
Carry these forward; several are page-global and will affect all three pages.

| Item | Where | Needed |
|---|---|---|
| **Magen crisis hotline number** | Crisis bar + FAQ CTA use placeholder `tel:STARNUM` / `[★ CEO to provide]` | Real dedicated hotline number (CEO to provide) |
| **Phone inconsistency** | Hero & stages "Talk to us" use `tel:023724073` (= 02-372-4073, the office line); crisis/FAQ use `STARNUM` | Decide: one number or office-vs-hotline split, then make consistent |
| **"People Love Magen"** | Voices eyebrow **and** H2 are identical | Likely a placeholder — give the eyebrow distinct text |
| **Revacha official quote** | Voices card 2 | Real quote + name |
| **Parents-of-survivor quote** | Voices card 3 | Real quote + name |
| **Helise's book** | Book CTA | Title, 1–2 sentence description, cover image |
| **Team = division** | Team strip note | Confirm the correct people per pillar; add real photos for Ester Horovits & Rikki Weiss (currently initials) |
| **All nav/footer links** | Everywhere | `href="#"` throughout — real page URLs once pages exist |
| **Mobile responsiveness** | Whole page | No media queries captured; needs mobile pass before launch |
| **Hebrew (HE) version** | Whole page | Only one Hebrew eyebrow so far; full HE localization planned (old site used WPML) |
| **Live vs. local drift** | `index.html` | Working copy differs from live; reconcile before next deploy |

---

## 7. How to build Program Pages 2 & 3 (the contract)
1. **Keep global sections byte-identical:** crisis bar, nav+mega-menu, book CTA, footer. (Consider extracting to shared partials later; for now, copy exactly.)
2. **Reskin per-page sections** using the same components and tokens:
   - Hero: pillar eyebrow + a headline in the same "promise" cadence + relevant carousel images.
   - Stage model: each pillar gets its own conceptual stages (Pillar 1 = Muganut→Shikum; Pillars 2 & 3 TBD from Rivky's drafts).
   - Programs grid: one card per sub-program (see the pillar table in §1).
   - Team strip: that division's people.
   - FAQ: pillar-specific questions, same `schema.org` markup.
3. **Obey the voice principles (§5) and design system (§4) exactly.**
4. **Log new placeholders** into §6-style ledgers in each page's own canon doc.

---

## 8. Related material
- `reference-docs/Magen for Jewish Communities - Campaign Statement.xlsx` — freshest campaign messaging (updated 2026-07-03); check for copy newer than this page.
- `reference-docs/Magen - Cross River - Website Upgrade Proposal .pdf` — the agency alternative to this DIY build.
- `reference-docs/Magen_branding.pdf` — brand guidelines (verify color/type against §4).
- `Magen Website Companion.docx`, `Magen Project Summary (1).docx` — project background.
- **Pending:** Rivky's Google Docs drafts for Pillars 2 (Advocacy & Investigations) and 3 (Community & Network) — the next thing we review.
