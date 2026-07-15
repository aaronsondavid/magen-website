#!/usr/bin/env python3
"""Generate the remaining bonafide preview pages (Resources, What People Say,
Lo Tishtok) from a shared design system so we don't repeat 200 lines of CSS
per page. Each page defines only its <body> content and a page-specific slug
of custom CSS if it needs extra styles beyond the shared block.
"""
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Shared CSS — everything a preview page has in common
# --------------------------------------------------------------------------
SHARED_CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    :root { --teal:#00AEAC; --teal-dk:#008F8D; --purple:#6B4FA1; --pink:#E879A0;
      --dark:#1A1A2E; --gray:#555; --light:#F7F7F7; --amber:#F59E0B; --amber-bg:#FEF3C7; }
    body { font-family:'Open Sans',sans-serif; color:var(--dark); background:#fff; line-height:1.6; }

    .draft-banner { background:var(--amber-bg); color:#78350F; text-align:center; padding:10px 24px;
      font-size:0.85rem; border-bottom:2px solid var(--amber); font-weight:600; letter-spacing:0.02em; }
    .crisis-bar { background:var(--dark); color:#fff; text-align:center; padding:10px 60px;
      font-size:0.82rem; letter-spacing:0.03em; display:flex; align-items:center; justify-content:center; gap:16px; }
    .crisis-bar strong { color:var(--teal); font-weight:700; }
    .crisis-bar a { color:#fff; font-weight:700; text-decoration:none;
      border-bottom:1px solid rgba(255,255,255,0.3); transition:border-color 0.2s; }
    .crisis-bar a:hover { border-color:var(--teal); color:var(--teal); }
    .crisis-dot { width:7px; height:7px; background:var(--teal); border-radius:50%; display:inline-block; animation:pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

    .nav-wrap { position:sticky; top:0; z-index:200; background:#fff;
      border-bottom:3px solid var(--teal); box-shadow:0 2px 12px rgba(0,0,0,0.07); }
    nav { display:flex; justify-content:space-between; align-items:center;
      padding:0 60px; height:72px; background:#fff; max-width:1400px; margin:0 auto; }
    .nav-logo { display:flex; align-items:center; gap:12px; text-decoration:none; }
    .nav-logo-text { display:flex; flex-direction:column; line-height:1; }
    .nav-logo-text .brand { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.5rem; color:var(--teal); letter-spacing:0.08em; }
    .nav-logo-text .sub { font-size:0.62rem; color:var(--gray); letter-spacing:0.06em; text-transform:uppercase; }
    .nav-links { display:flex; align-items:center; gap:4px; list-style:none; height:72px; }
    .nav-links > li > a { text-decoration:none; color:var(--dark); font-size:0.82rem; font-weight:700;
      letter-spacing:0.05em; text-transform:uppercase; padding:0 16px; height:100%; display:flex; align-items:center;
      transition:color 0.2s; white-space:nowrap; border-bottom:3px solid transparent; margin-bottom:-3px; }
    .nav-links > li:hover > a { color:var(--teal); border-bottom-color:var(--teal); }
    .btn-donate { background:var(--teal); color:#fff !important; padding:10px 22px !important; border-radius:4px; margin-left:12px; }

    .hero { background: linear-gradient(135deg, var(--dark) 0%, #232449 65%, var(--purple) 130%);
      color:#fff; padding:100px 60px 110px; text-align:center; position:relative; }
    .hero::before { content:''; position:absolute; top:0; left:0; right:0; height:6px;
      background: linear-gradient(90deg, var(--teal), var(--purple), var(--pink)); }
    .hero .eyebrow { font-family:'Barlow Condensed',sans-serif; letter-spacing:0.25em; text-transform:uppercase;
      color:var(--teal); font-weight:700; font-size:0.95rem; margin-bottom:22px; }
    .hero h1 { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:4rem;
      line-height:1.05; letter-spacing:-0.015em; max-width:960px; margin:0 auto 22px; }
    .hero h1 em { font-style:normal; color:var(--teal); }
    .hero h1 .pink { color:var(--pink); }
    .hero .lead { font-size:1.2rem; color:#C1C1D0; max-width:720px; margin:0 auto 32px; line-height:1.6; }
    .hero-ctas { display:flex; gap:14px; justify-content:center; flex-wrap:wrap; }

    section.block { padding:90px 60px; max-width:1200px; margin:0 auto; }
    .eyebrow-h { font-family:'Barlow Condensed',sans-serif; letter-spacing:0.2em; text-transform:uppercase;
      color:var(--purple); font-weight:700; font-size:0.9rem; margin-bottom:14px; display:block; }
    h2 { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:2.6rem;
      color:var(--dark); letter-spacing:-0.01em; margin-bottom:18px; line-height:1.05; }
    h2 em { font-style:normal; color:var(--teal); }
    .lead-p { color:var(--gray); font-size:1.1rem; margin-bottom:44px; max-width:760px; line-height:1.65; }

    .btn { padding:14px 28px; text-decoration:none; border-radius:4px; font-weight:700;
      letter-spacing:0.05em; text-transform:uppercase; font-size:0.9rem; display:inline-block; transition:all 0.2s; }
    .btn-primary { background:var(--teal); color:#fff; } .btn-primary:hover { background:var(--teal-dk); }
    .btn-ghost { background:transparent; color:#fff; border:2px solid #fff; padding:12px 26px; }
    .btn-ghost:hover { background:#fff; color:var(--dark); }

    .close { background: linear-gradient(135deg, var(--purple) 0%, #4E3583 100%); color:#fff; padding:80px 60px; text-align:center; }
    .close h2 { color:#fff; margin-bottom:16px; }
    .close p { max-width:640px; margin:0 auto 28px; color:rgba(255,255,255,0.9); font-size:1.05rem; }
    .close .btn-ghost { border-color:#fff; }
    .close .btn-ghost:hover { background:#fff; color:var(--purple); }

    footer { background:var(--dark); color:#fff; padding:60px 60px 30px; border-top:1px solid rgba(255,255,255,0.1); }
    .footer-motto { text-align:center; font-family:'Barlow Condensed',sans-serif; font-size:1.3rem; color:var(--teal); letter-spacing:0.05em; margin-bottom:40px; }
    .footer-motto em { font-style:normal; color:var(--pink); font-weight:700; }
    .footer-grid { display:grid; grid-template-columns:2fr 1fr 1fr 1fr; gap:40px; max-width:1400px; margin:0 auto; }
    .footer-brand p { color:#C1C1D0; font-size:0.88rem; line-height:1.6; margin-top:16px; }
    .footer-contact { display:flex; flex-direction:column; gap:6px; margin-top:16px; }
    .footer-contact a { color:#fff; text-decoration:none; font-size:0.85rem; }
    .footer-col h4 { font-family:'Barlow Condensed',sans-serif; font-size:1rem; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:14px; color:var(--teal); }
    .footer-col ul { list-style:none; }
    .footer-col li { margin-bottom:8px; }
    .footer-col a { color:#C1C1D0; text-decoration:none; font-size:0.85rem; }
    .footer-bottom { max-width:1400px; margin:40px auto 0; padding-top:20px;
      border-top:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; font-size:0.78rem; color:#8888A0; }

    @media (max-width:1024px) { .hero h1 { font-size:2.8rem; } }
    @media (max-width:700px) {
      nav { padding:0 20px; } .nav-links > li:not(:last-child) { display:none; }
      .hero { padding:70px 24px 80px; } .hero h1 { font-size:2.1rem; }
      section.block, .close { padding:60px 24px; }
      .footer-grid { grid-template-columns:1fr; }
      .footer-bottom { flex-direction:column; gap:10px; text-align:center; }
    }
"""

CRISIS_BAR = '''
  <div class="crisis-bar">
    <span class="crisis-dot"></span>
    If you or someone is in immediate danger, call emergency services now:
    <a href="tel:100">Israel: 100</a> &nbsp;|&nbsp;
    <a href="tel:911">US: 911</a> &nbsp;|&nbsp;
    <a href="tel:999">UK: 999</a>
    &nbsp;&middot;&nbsp;
    <strong>Magen hotline:</strong>
    <a href="tel:*9781">*9781</a>
    &nbsp;&middot;&nbsp; 24/6
  </div>
'''

NAV = '''
  <div class="nav-wrap">
    <nav>
      <a href="/" class="nav-logo">
        <div class="nav-logo-text"><span class="brand">MAGEN</span><span class="sub">for Jewish Communities</span></div>
      </a>
      <ul class="nav-links">
        <li><a href="safety-and-healing.html">Safety &amp; Healing</a></li>
        <li><a href="advocacy-and-investigations.html">Advocacy &amp; Investigations</a></li>
        <li><a href="education-and-community.html">Education &amp; Community</a></li>
        <li><a href="resources.html">Resources</a></li>
        <li><a href="about.html">Magen</a></li>
        <li><a href="donate.html" class="btn-donate">Donate →</a></li>
      </ul>
    </nav>
  </div>
'''

FOOTER = '''
  <footer>
    <div class="footer-motto"><em>Here.</em> Until sexual abuse isn't.</div>
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="/" class="nav-logo">
          <div class="nav-logo-text"><span class="brand">MAGEN</span><span class="sub">for Jewish Communities</span></div>
        </a>
        <p>Breaking the silence and stigma of sexual abuse. Pursuing justice and healing for survivors across Jewish communities in Israel and beyond.</p>
        <div class="footer-contact">
          <a href="tel:023724073">02-372-4073</a>
          <a href="mailto:support@magen-israel.org">support@magen-israel.org</a>
          <a href="https://www.magen-israel.org">www.magen-israel.org</a>
        </div>
      </div>
      <div class="footer-col"><h4>Get Help</h4><ul>
        <li><a href="safety-and-healing.html">Safety &amp; Healing</a></li>
        <li><a href="in-an-emergency.html">In an Emergency</a></li>
        <li><a href="contact.html">Contact</a></li>
      </ul></div>
      <div class="footer-col"><h4>Programs</h4><ul>
        <li><a href="advocacy-and-investigations.html">Advocacy &amp; Investigations</a></li>
        <li><a href="education-and-community.html">Education &amp; Community</a></li>
        <li><a href="lo-tishtok.html">Lo Tishtok</a></li>
      </ul></div>
      <div class="footer-col"><h4>Magen</h4><ul>
        <li><a href="about.html">About Magen</a></li>
        <li><a href="staff.html">Our Team</a></li>
        <li><a href="what-people-say.html">What People Say</a></li>
        <li><a href="financial-transparency.html">Financial Transparency</a></li>
        <li><a href="resources.html">Resources</a></li>
        <li><a href="donate.html">Donate</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 Magen for Jewish Communities. Registered nonprofit. All rights reserved.</span>
      <span><a href="#">Privacy Policy</a> &middot; <a href="#">Terms of Use</a></span>
    </div>
  </footer>
'''

def render(title, extra_css, body, draft_note):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="noindex,nofollow,noarchive" />
  <title>{title} · Magen for Jewish Communities</title>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=Open+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
  <style>{SHARED_CSS}
{extra_css}
  </style>
</head>
<body>

  <div class="draft-banner">{draft_note}</div>
{CRISIS_BAR}
{NAV}
{body}
{FOOTER}

</body>
</html>
"""
    return html


# ============================================================================
# RESOURCES PAGE
# ============================================================================
RESOURCES_CSS = """
    .toc-strip { background:var(--light); padding:24px 60px; border-bottom:1px solid #E5E7EB; position:sticky; top:72px; z-index:100; }
    .toc-strip .toc { max-width:1200px; margin:0 auto; display:flex; gap:8px; flex-wrap:wrap; justify-content:center; }
    .toc a { padding:8px 16px; border-radius:20px; background:#fff; border:1px solid #E5E7EB; text-decoration:none;
      color:var(--dark); font-size:0.85rem; font-weight:600; transition:all 0.15s; }
    .toc a:hover { border-color:var(--teal); color:var(--teal); }

    .resource-section { padding:80px 60px; max-width:1200px; margin:0 auto; }
    .resource-section:nth-of-type(even) { background:var(--light); max-width:none; }
    .resource-section:nth-of-type(even) .inner { max-width:1200px; margin:0 auto; }
    .funnel-tag { display:inline-block; padding:4px 12px; border-radius:14px; font-family:'Barlow Condensed',sans-serif;
      font-size:0.75rem; letter-spacing:0.15em; text-transform:uppercase; font-weight:700; margin-bottom:10px; }
    .funnel-tag.tofu { background:#DBEAFE; color:#1E40AF; }
    .funnel-tag.mofu { background:#FDE68A; color:#92400E; }
    .funnel-tag.bofu { background:#FCE7F3; color:#9F1239; }

    .item-grid { display:grid; grid-template-columns:repeat(3, 1fr); gap:22px; margin-top:36px; }
    .r-card { background:#fff; border:1px solid #E5E7EB; border-radius:8px; padding:26px 24px;
      text-decoration:none; color:inherit; display:flex; flex-direction:column; transition:transform 0.15s, box-shadow 0.15s; }
    .r-card:hover { transform:translateY(-3px); box-shadow:0 10px 24px rgba(0,0,0,0.06); }
    .r-card .icon { font-size:1.6rem; margin-bottom:12px; }
    .r-card h4 { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.2rem; color:var(--dark); margin-bottom:8px; }
    .r-card p { color:var(--gray); font-size:0.92rem; line-height:1.55; flex-grow:1; }
    .r-card .badge { color:var(--teal); font-weight:700; font-size:0.78rem; letter-spacing:0.05em;
      text-transform:uppercase; margin-top:14px; }

    .r-list { display:flex; flex-direction:column; gap:14px; margin-top:32px; }
    .r-item { background:#fff; padding:22px 26px; border-radius:8px; border:1px solid #E5E7EB;
      display:grid; grid-template-columns:auto 1fr auto; gap:20px; align-items:center; text-decoration:none; color:inherit; transition:border-color 0.15s; }
    .r-item:hover { border-color:var(--teal); }
    .r-item .icon-lg { font-size:1.8rem; }
    .r-item .body h4 { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.1rem; color:var(--dark); }
    .r-item .body p { color:var(--gray); font-size:0.88rem; margin-top:2px; }
    .r-item .cta { color:var(--teal); font-weight:700; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.05em; }

    @media (max-width:1024px) { .item-grid { grid-template-columns:repeat(2, 1fr); } }
    @media (max-width:700px) { .item-grid { grid-template-columns:1fr; } .resource-section { padding:60px 24px; } .toc-strip { padding:18px 24px; } .r-item { grid-template-columns:1fr; text-align:left; } }
"""

RESOURCES_BODY = """
  <section class="hero">
    <div class="eyebrow">Resources</div>
    <h1>Everything we've <em>learned</em>. Ready when you need it.</h1>
    <p class="lead">Articles, guides, podcasts, downloadables, and events, organized by where you are in your own path. Nothing here is behind a paywall.</p>
  </section>

  <div class="toc-strip">
    <div class="toc">
      <a href="#learn">What's happening</a>
      <a href="#blog">Articles &amp; blog</a>
      <a href="#downloadables">Guides &amp; downloadables</a>
      <a href="#podcasts">Podcasts</a>
      <a href="#videos">Videos</a>
      <a href="#books">Books</a>
      <a href="#events">Events</a>
      <a href="#data">Data &amp; reports</a>
    </div>
  </div>

  <!-- ToFu: Learning -->
  <section class="resource-section" id="learn">
    <span class="funnel-tag tofu">Start here</span>
    <h2>Understanding what's happening.</h2>
    <p class="lead-p">If you're new to the topic or wondering whether something is off, these are the resources that answer the questions people search for at 2am. No pressure to act, just information.</p>
    <div class="item-grid">
      <a href="#" class="r-card">
        <div class="icon">🧭</div>
        <h4>What is CSA?</h4>
        <p>A plain-language overview of what child sexual abuse is, how it works, and the warning signs across ages and communities.</p>
        <span class="badge">Guide · 8 min read</span>
      </a>
      <a href="#" class="r-card">
        <div class="icon">👀</div>
        <h4>Is my community safe?</h4>
        <p>Honest thinking about risk in insular Jewish communities, and what an informed adult can watch for without becoming paranoid.</p>
        <span class="badge">Article · 12 min read</span>
      </a>
      <a href="#" class="r-card">
        <div class="icon">🛠</div>
        <h4>Can I do something to make it safer?</h4>
        <p>Concrete actions parents, educators, and community members can take, from conversations with children to institutional policy.</p>
        <span class="badge">Guide · 10 min read</span>
      </a>
    </div>
  </section>

  <!-- MoFu: Blog -->
  <section class="resource-section" id="blog">
    <div class="inner">
      <span class="funnel-tag mofu">Ongoing writing</span>
      <h2>Articles &amp; blog.</h2>
      <p class="lead-p">Writing from Magen's team, guest voices from the communities we serve, and long-form pieces on case dynamics, halachic questions, and cultural change.</p>
      <div class="item-grid">
        <a href="#" class="r-card">
          <div class="icon">✍️</div>
          <h4>The kallah teacher and the survivor</h4>
          <p>Why we built a trauma-sensitive kallah curriculum with the Eden Center, and what it changed for the women who used it first.</p>
          <span class="badge">By Mikey Susan · 2026</span>
        </a>
        <a href="#" class="r-card">
          <div class="icon">✍️</div>
          <h4>What "empowerment" actually means at the case level</h4>
          <p>How Magen's bottom-up approach plays out in practice, from the intake call to the courtroom.</p>
          <span class="badge">By Shana Aaronson · 2026</span>
        </a>
        <a href="#" class="r-card">
          <div class="icon">✍️</div>
          <h4>Halacha and reporting: the actual sources</h4>
          <p>A collected walkthrough of the halachic literature on reporting abuse to secular authorities, in plain English.</p>
          <span class="badge">Guest piece · 2025</span>
        </a>
      </div>
      <p style="margin-top:32px; color:var(--gray);">More writing coming as the blog goes live. <a href="#" style="color:var(--teal); font-weight:700;">Subscribe to updates →</a></p>
    </div>
  </section>

  <!-- Downloadables -->
  <section class="resource-section" id="downloadables">
    <span class="funnel-tag mofu">Take with you</span>
    <h2>Guides &amp; downloadables.</h2>
    <p class="lead-p">Print resources, coloring books, halachic sources, response protocols, and posters. Free to download, share, and adapt for your community.</p>
    <div class="item-grid">
      <a href="#" class="r-card">
        <div class="icon">📘</div>
        <h4>"I'm the boss of my body" coloring book</h4>
        <p>Age-appropriate body-safety concepts for young children, in Hebrew and English.</p>
        <span class="badge">PDF · Ages 3-8</span>
      </a>
      <a href="#" class="r-card">
        <div class="icon">📗</div>
        <h4>Post-disclosure parenting guide</h4>
        <p>Practical steps for parents in the first days and weeks after a child discloses abuse. By Helise Kugler Pollack.</p>
        <span class="badge">PDF · 40 pages</span>
      </a>
      <a href="#" class="r-card">
        <div class="icon">📕</div>
        <h4>Community response protocol</h4>
        <p>Step-by-step for shuls, schools, and community organizations when a disclosure or allegation reaches leadership.</p>
        <span class="badge">PDF · Institutional</span>
      </a>
      <a href="#" class="r-card">
        <div class="icon">📄</div>
        <h4>Kuntress on halacha and abuse</h4>
        <p>Compiled sources and analysis, suitable for beit midrash study and communal discussion.</p>
        <span class="badge">PDF · Hebrew</span>
      </a>
      <a href="#" class="r-card">
        <div class="icon">🖼</div>
        <h4>Awareness posters (set of 5)</h4>
        <p>Print-ready posters for use in shul lobbies, school hallways, and mikvaot. Multiple language variants.</p>
        <span class="badge">Print pack</span>
      </a>
      <a href="#" class="r-card">
        <div class="icon">📞</div>
        <h4>What happens when you call the hotline</h4>
        <p>A one-page overview of what a call to *9781 looks like, so anyone can share it with someone who might need it.</p>
        <span class="badge">PDF · 1 page</span>
      </a>
    </div>
  </section>

  <!-- Podcasts -->
  <section class="resource-section" id="podcasts">
    <div class="inner">
      <span class="funnel-tag mofu">Listen</span>
      <h2>Podcasts &amp; interviews.</h2>
      <p class="lead-p">Long-form conversations with Shana, staff, survivors who chose to speak publicly, and journalists covering the field.</p>
      <div class="r-list">
        <a href="#" class="r-item">
          <div class="icon-lg">🎙</div>
          <div class="body"><h4>Shana Aaronson on the Meaningful People podcast</h4><p>On what fifteen years in this work looks like, from Beit Shemesh to the Malka Leifer extradition.</p></div>
          <div class="cta">Listen →</div>
        </a>
        <a href="#" class="r-item">
          <div class="icon-lg">🎙</div>
          <div class="body"><h4>The Chaim Walder case, retold</h4><p>Yaakov Sela in conversation about the community response, the journalism, and the aftermath.</p></div>
          <div class="cta">Listen →</div>
        </a>
        <a href="#" class="r-item">
          <div class="icon-lg">🎙</div>
          <div class="body"><h4>Advocacy inside the Orthodox world</h4><p>Panel with Rabbi Yosef Blau, Sharon Weiss Greenberg, and Shana on making change from within.</p></div>
          <div class="cta">Listen →</div>
        </a>
      </div>
    </div>
  </section>

  <!-- Videos -->
  <section class="resource-section" id="videos">
    <span class="funnel-tag mofu">Watch</span>
    <h2>Videos.</h2>
    <p class="lead-p">Program explainers, event recordings, and short pieces built for social sharing. Subtitled in Hebrew and English.</p>
    <div class="item-grid">
      <a href="#" class="r-card">
        <div class="icon">🎥</div>
        <h4>What a Magen case looks like</h4>
        <p>A composite walkthrough of intake, accompaniment, and long-term support (identifying details changed).</p>
        <span class="badge">6 min</span>
      </a>
      <a href="#" class="r-card">
        <div class="icon">🎥</div>
        <h4>2022 women's awareness event</h4>
        <p>Highlights from the 420-seat theater event that led to 80 disclosures in the following week.</p>
        <span class="badge">18 min</span>
      </a>
      <a href="#" class="r-card">
        <div class="icon">🎥</div>
        <h4>Shana at the Knesset</h4>
        <p>Testimony before the committee on legislation strengthening protections for child witnesses.</p>
        <span class="badge">22 min</span>
      </a>
    </div>
  </section>

  <!-- Books -->
  <section class="resource-section" id="books">
    <div class="inner">
      <span class="funnel-tag mofu">Read deeper</span>
      <h2>Books we recommend.</h2>
      <p class="lead-p">A curated shelf for parents, professionals, and community leaders who want to go beyond the intro material.</p>
      <div class="item-grid">
        <a href="#" class="r-card">
          <div class="icon">📖</div>
          <h4>Helise Kugler Pollack's post-disclosure work</h4>
          <p>Foundational reading for any parent, therapist, or educator supporting a child after disclosure.</p>
          <span class="badge">Trauma specialist</span>
        </a>
        <a href="#" class="r-card">
          <div class="icon">📖</div>
          <h4>Body Keeps the Score, van der Kolk</h4>
          <p>The go-to primer on how trauma lives in the body and mind, and what heals it.</p>
          <span class="badge">Foundational</span>
        </a>
        <a href="#" class="r-card">
          <div class="icon">📖</div>
          <h4>Orthodox writers on abuse &amp; halacha</h4>
          <p>A curated list of contemporary Orthodox writers grappling with halachic questions in abuse cases.</p>
          <span class="badge">Multiple authors</span>
        </a>
      </div>
    </div>
  </section>

  <!-- Events -->
  <section class="resource-section" id="events">
    <span class="funnel-tag bofu">Show up</span>
    <h2>Events &amp; workshops.</h2>
    <p class="lead-p">Community programs, chugei bayit, professional training, and educational events. Bring one to your neighborhood.</p>
    <div class="item-grid">
      <a href="education-and-community.html" class="r-card">
        <div class="icon">🎤</div>
        <h4>Community workshops</h4>
        <p>Evidence-based workshops for parents, educators, and community leaders. Customized per community.</p>
        <span class="badge">By request</span>
      </a>
      <a href="education-and-community.html" class="r-card">
        <div class="icon">🏠</div>
        <h4>Chug bayit (home circles)</h4>
        <p>Small, in-home gatherings for donors, community members, or families who want a closer look at Magen's work.</p>
        <span class="badge">Host one</span>
      </a>
      <a href="education-and-community.html" class="r-card">
        <div class="icon">🎓</div>
        <h4>Professional training</h4>
        <p>Trauma-informed training for police, therapists, kallah teachers, and school staff.</p>
        <span class="badge">Certified programs</span>
      </a>
    </div>
  </section>

  <!-- Data / archive -->
  <section class="resource-section" id="data">
    <div class="inner">
      <span class="funnel-tag bofu">The numbers</span>
      <h2>Data, reports &amp; archive.</h2>
      <p class="lead-p">For researchers, journalists, and community leaders who want the underlying data. All figures board-audited before publication.</p>
      <div class="item-grid">
        <a href="financial-transparency.html" class="r-card">
          <div class="icon">📊</div>
          <h4>Annual impact reports</h4>
          <p>Caseload volume, program metrics, and financial breakdowns from every year Magen has been operating.</p>
          <span class="badge">2020-2024</span>
        </a>
        <a href="#" class="r-card">
          <div class="icon">📰</div>
          <h4>Media coverage archive</h4>
          <p>Hundreds of articles, TV segments, and podcast appearances catalogued by year, platform, and topic.</p>
          <span class="badge">2020-2026</span>
        </a>
        <a href="#" class="r-card">
          <div class="icon">🔬</div>
          <h4>Research partnerships</h4>
          <p>Ongoing collaborations with academic institutions on trauma, community response, and legal outcomes.</p>
          <span class="badge">Open for partners</span>
        </a>
      </div>
    </div>
  </section>

  <section class="close">
    <h2>Nothing on this page is a substitute for a conversation.</h2>
    <p>If any of this raised something for you, or someone you love, the hotline is open.</p>
    <a href="tel:*9781" class="btn btn-primary" style="background:#fff; color:var(--purple);">Call *9781</a>
    <a href="contact.html" class="btn btn-ghost" style="margin-left:8px;">Send a message</a>
  </section>
"""

# ============================================================================
# WHAT PEOPLE SAY PAGE
# ============================================================================
WPS_CSS = """
    .filter-strip { background:var(--light); padding:20px 60px; border-bottom:1px solid #E5E7EB; position:sticky; top:72px; z-index:100; }
    .filter-strip .filters { max-width:1200px; margin:0 auto; display:flex; gap:8px; flex-wrap:wrap; justify-content:center; }
    .filter { padding:8px 18px; border-radius:20px; background:#fff; border:1px solid #E5E7EB;
      color:var(--dark); font-size:0.85rem; font-weight:600; cursor:pointer; transition:all 0.15s; text-decoration:none; }
    .filter:hover, .filter.active { border-color:var(--teal); color:var(--teal); background:#F0FDFD; }

    .voice-section { padding:80px 60px; max-width:1300px; margin:0 auto; }
    .voice-section:nth-of-type(even) { background:var(--light); max-width:none; }
    .voice-section:nth-of-type(even) .inner { max-width:1300px; margin:0 auto; }

    .voice-tag { display:inline-block; padding:6px 14px; border-radius:14px; font-family:'Barlow Condensed',sans-serif;
      font-size:0.75rem; letter-spacing:0.15em; text-transform:uppercase; font-weight:700; margin-bottom:14px;
      background:var(--teal); color:#fff; }
    .voice-tag.pink { background:var(--pink); } .voice-tag.purple { background:var(--purple); }
    .voice-tag.dark { background:var(--dark); }

    .voice-grid { display:grid; grid-template-columns:repeat(2, 1fr); gap:26px; margin-top:36px; }
    .quote-card { background:#fff; border:1px solid #E5E7EB; border-radius:10px; padding:36px 34px;
      position:relative; border-left:4px solid var(--teal); }
    .quote-card::before { content:'"'; position:absolute; top:14px; right:24px;
      font-family:'Barlow Condensed',sans-serif; font-size:5rem; color:var(--teal); opacity:0.18; line-height:1; }
    .quote-card p.q { font-size:1.05rem; color:var(--dark); line-height:1.7; font-style:italic; margin-bottom:22px; }
    .quote-card .attr { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:0.95rem;
      color:var(--gray); letter-spacing:0.05em; text-transform:uppercase; }
    .quote-card .attr span { display:block; font-size:0.75rem; color:var(--gray); font-weight:600; letter-spacing:0.08em; margin-top:2px; text-transform:none; font-family:'Open Sans',sans-serif; }
    .quote-card.pink { border-left-color:var(--pink); } .quote-card.pink::before { color:var(--pink); }
    .quote-card.purple { border-left-color:var(--purple); } .quote-card.purple::before { color:var(--purple); }

    @media (max-width:1024px) { .voice-grid { grid-template-columns:1fr; } }
    @media (max-width:700px) { .voice-section { padding:60px 24px; } .filter-strip { padding:16px 24px; } }
"""

WPS_BODY = """
  <section class="hero">
    <div class="eyebrow">What People Say</div>
    <h1>The people who know the work best <em>speak.</em></h1>
    <p class="lead">Survivors, families, rabbis, therapists, police officers, journalists, and donors. Everyone who's been close to Magen sees a different piece of the picture. Here they are, in their own words.</p>
  </section>

  <div class="filter-strip">
    <div class="filters">
      <a href="#survivors" class="filter">Survivors</a>
      <a href="#families" class="filter">Families</a>
      <a href="#leaders" class="filter">Community leaders</a>
      <a href="#professionals" class="filter">Professionals</a>
      <a href="#journalists" class="filter">Journalists</a>
      <a href="#donors" class="filter">Donors</a>
    </div>
  </div>

  <!-- Survivors -->
  <section class="voice-section" id="survivors">
    <span class="voice-tag">Survivors</span>
    <h2>From survivors.</h2>
    <p class="lead-p">Names and identifying details are withheld or changed at each survivor's request. Every quote is published with explicit consent.</p>
    <div class="voice-grid">
      <div class="quote-card">
        <p class="q">Magen didn't tell me what to do. They laid out every option, answered every question, and let me choose. For the first time since it happened, I felt like the person in charge of my own life again.</p>
        <div class="attr">Survivor, Bet Shemesh <span>Case opened 2022</span></div>
      </div>
      <div class="quote-card pink">
        <p class="q">I was terrified that reporting would explode my life. My advocate at Magen didn't rush me. She walked me through what would actually happen at each step. When I was ready, she was in every room with me.</p>
        <div class="attr">Survivor, Jerusalem <span>Case closed 2024</span></div>
      </div>
      <div class="quote-card purple">
        <p class="q">I called the hotline three times before I actually said anything. They picked up every time, and never made me feel like I was wasting anyone's time. That patience is what got me to the fourth call.</p>
        <div class="attr">Survivor, US Diaspora <span>Ongoing case</span></div>
      </div>
      <div class="quote-card">
        <p class="q">The peer group changed what I thought was possible. Sitting in a room with other women who understood, without having to explain a single thing, that was healing I didn't know existed.</p>
        <div class="attr">Survivor, Beit Shemesh <span>Peer group participant</span></div>
      </div>
    </div>
  </section>

  <!-- Families -->
  <section class="voice-section" id="families">
    <div class="inner">
      <span class="voice-tag pink">Families</span>
      <h2>From families &amp; loved ones.</h2>
      <p class="lead-p">Parents, spouses, and siblings, on what it looked like when a family member disclosed.</p>
      <div class="voice-grid">
        <div class="quote-card pink">
          <p class="q">When my daughter told us, I did every wrong thing in the first ten minutes. Magen's parent-support call the next morning saved our relationship. They taught us how to actually be there for her.</p>
          <div class="attr">Parent of survivor, Jerusalem <span>2023</span></div>
        </div>
        <div class="quote-card">
          <p class="q">The Kugler Pollack guide arrived at our door within a day. We read it that night. It gave us a script for the next six months when we had no idea what to say.</p>
          <div class="attr">Parents of teen survivor <span>Anonymous</span></div>
        </div>
      </div>
    </div>
  </section>

  <!-- Community leaders -->
  <section class="voice-section" id="leaders">
    <span class="voice-tag purple">Community leaders</span>
    <h2>From rabbis, morot, and community leaders.</h2>
    <p class="lead-p">People who lead shuls, schools, and communities on what changed after they engaged Magen.</p>
    <div class="voice-grid">
      <div class="quote-card purple">
        <p class="q">We used to think this was someone else's problem. After Magen's workshop, we understood it's ours. Every adult in this community is now a first line of defense.</p>
        <div class="attr">Community rabbi, Jerusalem <span>Workshop 2024</span></div>
      </div>
      <div class="quote-card">
        <p class="q">Magen's approach doesn't ask us to choose between our values and our children. It asks us to notice that they've always been the same commitment.</p>
        <div class="attr">Rosh yeshiva, Beit Shemesh <span>2025</span></div>
      </div>
      <div class="quote-card pink">
        <p class="q">The kallah-teacher curriculum they built with the Eden Center is now standard in three of our schools. The feedback from the young women has been extraordinary.</p>
        <div class="attr">Program director, seminary network <span>2025</span></div>
      </div>
      <div class="quote-card">
        <p class="q">When the extremists showed up to protest our workshop in Kiryat Sefer, Magen's response wasn't confrontational. It was calm, halachically grounded, and immoveable. Within a week fifteen more communities were asking for the workshop.</p>
        <div class="attr">Community activist <span>Kiryat Sefer 2024</span></div>
      </div>
    </div>
  </section>

  <!-- Professionals -->
  <section class="voice-section" id="professionals">
    <div class="inner">
      <span class="voice-tag dark">Professionals</span>
      <h2>From detectives, therapists, and social workers.</h2>
      <p class="lead-p">The professionals whose work overlaps with Magen's, on why the partnership matters.</p>
      <div class="voice-grid">
        <div class="quote-card">
          <p class="q">Cases involving religious communities used to reach dead ends. Working with Magen, we get the cultural context and community access we can't get anywhere else. Convictions we couldn't have secured alone.</p>
          <div class="attr">Israeli law enforcement officer <span>Sex crimes unit</span></div>
        </div>
        <div class="quote-card purple">
          <p class="q">My caseload has clients Magen referred to me. What they do upfront, the intake, the safety planning, the family prep, means my sessions can actually go to the healing work.</p>
          <div class="attr">Trauma therapist, Jerusalem <span>Long-time partner</span></div>
        </div>
        <div class="quote-card pink">
          <p class="q">As a chalak worker, I see every day what happens when a community doesn't know how to respond. Magen's training gave our staff a protocol. We're not guessing anymore.</p>
          <div class="attr">Municipal social worker <span>Beit Shemesh</span></div>
        </div>
      </div>
    </div>
  </section>

  <!-- Journalists -->
  <section class="voice-section" id="journalists">
    <span class="voice-tag">Journalists</span>
    <h2>From journalists who cover this work.</h2>
    <div class="voice-grid">
      <div class="quote-card">
        <p class="q">Magen is the only source that combines cultural insider knowledge, professional discipline, and verifiable case records. If you want a story that's accurate and doesn't harm survivors, they're where you start.</p>
        <div class="attr">Investigative journalist, Israeli daily <span>Byline withheld</span></div>
      </div>
      <div class="quote-card purple">
        <p class="q">The Malka Leifer story would not have broken open the way it did without Magen tracking her, and without the survivor advocacy that kept the pressure on for years. Full stop.</p>
        <div class="attr">Foreign correspondent, English-language outlet <span>2021</span></div>
      </div>
    </div>
  </section>

  <!-- Donors -->
  <section class="voice-section" id="donors">
    <div class="inner">
      <span class="voice-tag pink">Donors</span>
      <h2>From donors and partners.</h2>
      <p class="lead-p">People and foundations who fund the work, on why they keep showing up.</p>
      <div class="voice-grid">
        <div class="quote-card pink">
          <p class="q">Every dollar to Magen is board-audited, program-directed, and matched by outcomes I can actually see. In fifteen years of Jewish philanthropy, they're the most transparent nonprofit I've partnered with.</p>
          <div class="attr">Family foundation trustee <span>US, ongoing partner</span></div>
        </div>
        <div class="quote-card">
          <p class="q">We don't ask ourselves whether Magen deserves funding. We ask ourselves whether we're giving enough.</p>
          <div class="attr">Individual donor, monthly circle <span>Anonymous</span></div>
        </div>
      </div>
    </div>
  </section>

  <section class="close">
    <h2>Have your own story to add?</h2>
    <p>If you've worked with Magen and would like to share a testimonial, we'd love to include your voice, on your terms and only with your explicit permission.</p>
    <a href="contact.html" class="btn btn-primary" style="background:#fff; color:var(--purple);">Share your voice</a>
    <a href="donate.html" class="btn btn-ghost" style="margin-left:8px;">Support the work</a>
  </section>
"""

# ============================================================================
# LO TISHTOK PAGE
# ============================================================================
LT_CSS = """
    /* Lo Tishtok specific: bolder, campaign feel */
    .hero { background: linear-gradient(135deg, #1A1A2E 0%, #4E3583 50%, var(--pink) 130%); }
    .hero h1 { font-size:5rem; }
    .hero h1 em { color:var(--pink); }
    .hero .he { display:block; font-family:'Barlow Condensed',sans-serif; font-weight:700;
      font-size:1.3rem; letter-spacing:0.3em; color:rgba(255,255,255,0.7); margin-bottom:14px; }

    .manifesto { padding:100px 60px; max-width:900px; margin:0 auto; text-align:center; }
    .manifesto p { font-family:'Barlow Condensed',sans-serif; font-weight:600; font-size:1.9rem;
      color:var(--dark); line-height:1.35; letter-spacing:-0.005em; margin-bottom:28px; }
    .manifesto p em { font-style:normal; color:var(--pink); font-weight:800; }
    .manifesto p strong { color:var(--purple); font-weight:800; }
    .manifesto .signature { font-size:0.9rem; color:var(--gray); margin-top:40px; letter-spacing:0.05em; }

    .principle-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:26px; margin-top:48px; }
    .principle { background:#fff; border:1px solid #E5E7EB; border-radius:10px; padding:38px 30px; position:relative; }
    .principle::before { content:''; position:absolute; top:0; left:30px; right:30px; height:5px;
      background:var(--pink); border-radius:0 0 4px 4px; }
    .principle:nth-child(2)::before { background:var(--purple); }
    .principle:nth-child(3)::before { background:var(--teal); }
    .principle .num { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:0.85rem;
      color:var(--pink); letter-spacing:0.2em; text-transform:uppercase; margin-bottom:12px; }
    .principle:nth-child(2) .num { color:var(--purple); }
    .principle:nth-child(3) .num { color:var(--teal); }
    .principle h3 { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.7rem;
      color:var(--dark); margin-bottom:14px; line-height:1.15; }
    .principle p { color:var(--gray); font-size:1rem; line-height:1.65; }

    .action { background:var(--dark); color:#fff; padding:90px 60px; }
    .action-inner { max-width:1100px; margin:0 auto; }
    .action h2 { color:#fff; text-align:center; margin-bottom:14px; }
    .action .sub { text-align:center; color:rgba(255,255,255,0.75); margin-bottom:50px; max-width:640px; margin-left:auto; margin-right:auto; }
    .action-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
    .action-card { background:rgba(255,255,255,0.05); padding:30px 26px; border-radius:8px;
      border-left:4px solid var(--pink); text-decoration:none; color:inherit; transition:transform 0.15s; }
    .action-card:hover { transform:translateY(-3px); background:rgba(255,255,255,0.08); }
    .action-card:nth-child(2) { border-left-color:var(--purple); }
    .action-card:nth-child(3) { border-left-color:var(--teal); }
    .action-card h4 { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.4rem;
      color:#fff; margin-bottom:12px; line-height:1.15; }
    .action-card p { color:rgba(255,255,255,0.75); font-size:0.95rem; line-height:1.6; margin-bottom:14px; }
    .action-card .cta { color:var(--pink); font-weight:700; font-size:0.85rem; letter-spacing:0.05em; text-transform:uppercase; }
    .action-card:nth-child(2) .cta { color:var(--purple); }
    .action-card:nth-child(3) .cta { color:var(--teal); }

    @media (max-width:1024px) { .principle-grid, .action-grid { grid-template-columns:1fr; } }
    @media (max-width:700px) { .manifesto { padding:60px 24px; } .manifesto p { font-size:1.4rem; } .action { padding:60px 24px; } }
"""

LT_BODY = """
  <section class="hero">
    <div class="eyebrow" style="color:var(--pink);">The Campaign</div>
    <span class="he">לא תשתוק</span>
    <h1>Lo Tishtok. <em>Do not stay silent.</em></h1>
    <p class="lead">A movement for accountability, responsibility, and voice, built for the moment when silence is no longer the safer choice for anyone.</p>
    <div class="hero-ctas">
      <a href="#join" class="btn btn-primary" style="background:var(--pink);">Join the movement</a>
      <a href="#principles" class="btn btn-ghost">Read the principles</a>
    </div>
  </section>

  <section class="manifesto">
    <p>Abuse thrives in <em>silence</em>. So does the shame that keeps survivors alone. So do the systems that let perpetrators move from community to community without consequences.</p>
    <p>Lo Tishtok is a <strong>refusal</strong>. Not a slogan.</p>
    <p>To refuse silence is to see the child you don't want to see. To ask the question you don't want to ask. To believe the person who was hardest to hear.</p>
    <p>It is to accept that in Torah's own language, <em>lo ta'amod al dam re'echa</em>, do not stand idle by your neighbor's blood, was never a suggestion.</p>
    <p>This is the movement of every rabbi, teacher, parent, neighbor, and survivor who is done pretending they don't know.</p>
    <div class="signature">— Magen for Jewish Communities</div>
  </section>

  <section class="block" id="principles">
    <span class="eyebrow-h" style="text-align:center; display:block;">The three principles</span>
    <h2 style="text-align:center; margin:0 auto 44px;">What Lo Tishtok stands for.</h2>
    <div class="principle-grid">
      <div class="principle">
        <div class="num">Principle 01</div>
        <h3>Every adult is responsible for every child.</h3>
        <p>Prevention isn't a household strategy. It's a communal one. When a whole community sees itself as accountable for its children's safety, silence becomes untenable.</p>
      </div>
      <div class="principle">
        <div class="num">Principle 02</div>
        <h3>Survivors decide. Communities support.</h3>
        <p>Empowerment means bottom-up, evidence-based decision-making by survivors themselves. The community's job is to make sure survivors have the resources, information, and safety they need to choose.</p>
      </div>
      <div class="principle">
        <div class="num">Principle 03</div>
        <h3>Halacha demands this. It doesn't debate it.</h3>
        <p>Torah's mandate to protect the powerless is not up for negotiation. Lo Tishtok isn't a modern departure from tradition; it's the tradition's own instruction, reclaimed.</p>
      </div>
    </div>
  </section>

  <section class="action" id="join">
    <div class="action-inner">
      <h2>How to join the movement.</h2>
      <p class="sub">Three concrete steps for anyone who's ready to stop being a bystander. Pick one, or all three.</p>
      <div class="action-grid">
        <a href="education-and-community.html" class="action-card">
          <h4>Bring a workshop to your community.</h4>
          <p>Educate the adults around you. Magen runs workshops for shuls, schools, and community organizations tailored to your community's specific needs and language.</p>
          <span class="cta">Book a program →</span>
        </a>
        <a href="donate.html" class="action-card">
          <h4>Fund the work.</h4>
          <p>Every hour on the hotline, every case walked through court, every workshop delivered is funded by donors who refuse to leave this to someone else.</p>
          <span class="cta">Support Magen →</span>
        </a>
        <a href="contact.html" class="action-card">
          <h4>Amplify the message.</h4>
          <p>Share Lo Tishtok in your community. If you're a rabbi, teacher, or leader, add your voice to the growing list of endorsements.</p>
          <span class="cta">Get involved →</span>
        </a>
      </div>
    </div>
  </section>

  <section class="block">
    <span class="eyebrow-h">Where Lo Tishtok has already changed things</span>
    <h2>The movement, in evidence.</h2>
    <div class="principle-grid">
      <div class="principle">
        <div class="num">2022</div>
        <h3>420-seat women's event.</h3>
        <p>A single evening. Standing room only, 100 women waitlisted. Within the following week, 80 women came forward with disclosures. Silence broken, one voice at a time.</p>
      </div>
      <div class="principle">
        <div class="num">2024</div>
        <h3>Kiryat Sefer workshop.</h3>
        <p>Extremists protested. The workshop went ahead. Within a week, 15 more communities requested the same program, and Mishpacha magazine backed our work in print.</p>
      </div>
      <div class="principle">
        <div class="num">2025</div>
        <h3>Fifteen years of proof.</h3>
        <p>9,061 crisis contacts. 2,007 survivors supported. 197 law-enforcement cases. Cultural change that used to be considered impossible is measurable now.</p>
      </div>
    </div>
  </section>

  <section class="close">
    <h2>Refuse the silence.</h2>
    <p>You already knew. Now you know what to do with knowing.</p>
    <a href="donate.html" class="btn btn-primary" style="background:#fff; color:var(--purple);">Fund the movement</a>
    <a href="tel:*9781" class="btn btn-ghost" style="margin-left:8px;">Call our hotline · *9781</a>
  </section>
"""

# ============================================================================
# Generate
# ============================================================================
PAGES = [
    ("resources.html",       "Resources",       RESOURCES_CSS, RESOURCES_BODY,
     "DRAFT PREVIEW · resource inventory populated with representative items · content still under review"),
    ("what-people-say.html", "What People Say", WPS_CSS,       WPS_BODY,
     "DRAFT PREVIEW · testimonials illustrative, awaiting real consented quotes"),
    ("lo-tishtok.html",      "Lo Tishtok",      LT_CSS,        LT_BODY,
     "DRAFT PREVIEW · Lo Tishtok campaign page · manifesto and principles under review"),
]

for filename, title, css, body, draft in PAGES:
    html = render(title, css, body, draft)
    (ROOT / filename).write_text(html, encoding="utf-8")
    print(f"wrote {filename} ({len(html):,} bytes)")
