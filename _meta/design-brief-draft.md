# Design brief draft — Magen website

Drafted 2026-07-21 from the December 2024 vision doc (`Vision.docx`) + the victim-guide content strategy + the pattern library. Send this to the designer as a starting point; David to red-line before sharing externally.

## A. What are we designing?

**1. What is the website?**
The website of Magen, an Israel-based nonprofit addressing sexual abuse in the global Jewish community. It serves simultaneously as a lifeline for survivors, a plain-language guide to legal and practical realities, an educator for communities and professionals, and a bridge between insular Jewish communities and secular legal systems.

**2. What does it help people do?**
Survivors and the people around them navigate the aftermath (safety, legal process, healing, rights) at their own pace and on their own terms. Communities and professionals learn to prevent, recognize and respond to abuse. Donors and partners understand the work well enough to fund it.

**3. Who is the main audience?**
Primary: survivors and their supporters (family, friends, community frontline roles) across the observant Jewish spectrum, in Israel and internationally. Secondary: community leaders, professionals (rabbis, educators, therapists, social workers, mandatory reporters), donors, and press.

**4. What should visitors understand or feel within five seconds?**
"You are not alone, this is a safe place to be right now, and the choice about what to do next is yours."

**5. What action should they take?**
Start a journey (get help, understand your options, take one small next step) or, as a secondary action, support the work (donate, get involved).

## B. Assets — yes / maybe / no

- Website backgrounds: **yes** (photography-driven, may add subtle texture options)
- Hero illustrations: **yes** (illustration is primary; photography could complement)
- Full scene illustrations: **no** (would feel infantilizing for the subject)
- Abstract decorative graphics: **maybe** (subtle texture on tool result screens, glossary cards, callouts)
- Product or technical diagrams: **yes - but this isn't a tech product, it's a human journey so the feel from the client has to be simplicity, comfort, support** (Criminal Process flow, statute of limitations table, MENA portal walkthrough, evidence timeline)
- Icons: **yes**, extensively (hotline types, urgency badges, journey identifiers, glossary categories, downloadable formats)
- Logos or brand marks: **yes** (Magen shield plus partner, rabbinical, and press logos)
- Data visualizations: **yes** (impact numbers, the 71% case closure stat, cases-per-year, community training reach)
- Interactive web elements: **yes**, central to the plan (SoL Checker, What Now? triage, Which Path?, journey cards, glossary tooltips)
- Buttons, cards, interface components: **yes** (journey cards, article cards, tool wrappers, hotline strips, where-next grids)
- Social media graphics: **yes** (already a tracked distribution channel; cross-promotion of articles and campaigns)
- Presentation graphics: **yes** (donor decks, QBR templates, professional training decks)
- Animation or motion elements: **maybe**, subtle only (pulse on the crisis dot, hover states on journey cards, loading animations). No scroll-triggered spectacle.

## C. Brand feel

Six words: **trustworthy, warm, calm, precise, professional, leadership.**
Not: **sterile, corporate, tech, childish.**

Short reasoning:

- **Trustworthy** carries the credibility of Torah alignment, evidence-based practice, and years of real cases handled.
- **Warm** preserves the survivor-first voice ("the choice remains yours").
- **Calm** signals steadiness in a crisis moment, never shrill or alarmist.
- **Precise** reflects the legal specificity of the content (exact windows, exact rights, exact next steps).
- **Professional** signals adult respect for the topic and meets donor-facing expectations.
- Not **sterile** because this is human work, not clinical.
- Not **corporate** because transactional register is wrong for survivor work.
- Not **childish** because copy or illustration that infantilizes would insult survivors' dignity.

## References to share with the designer

**Live pages that show current direction:**

- `https://preview.magen-israel.org/safety-and-healing.html` — photography-first hero, journey pattern, existing color and type system.
- `https://preview.magen-israel.org/advocacy-and-investigations.html` — the other primary pillar.
- `https://preview.magen-israel.org/pattern-library.html` — victim-guide component reference (tokens, voice, safety mechanics, hotline strip, reassurance callout, journey cards, article layout, glossary tooltip, where-next grid, tool wrapper, glossary index and term pages).

**Printed reference:**

- The English quadfold brochure (`English Version 14x8.5.pdf`) and the Hebrew quadfold (`Magen Quadfold 14x8.5.pdf`). These are the finalized print voice and color palette. The web should feel like a continuation of the brochure when someone scans the QR code, not a jarring rebrand.

**A "not this" reference:**

The vision doc calls out that Magen is "not intended to be combative," "not about rallying the troops," and constructive with community institutions. Design should not read as protest, activist, or oppositional. Warm authority, not warfare.

## Notes for future iteration

- Bilingual constraint (Hebrew + English) means every layout must survive RTL flipping. Test any illustration or icon library for RTL-safe versions before committing.
- Safety mechanics are non-negotiable design constraints: persistent hotline strip, quick-exit button, no forced auth, no cross-session storage, mobile-first (crisis access is nearly always phone).
- Copy style: no em dashes anywhere in deliverables (standing rule).
