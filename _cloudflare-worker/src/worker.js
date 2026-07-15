/**
 * Magen District Publisher — Cloudflare Worker
 *
 * Wire: Monday automation "when Publish trigger changes to 'Publish now'"
 *       POSTs to this Worker's URL with header X-Magen-Secret: <shared secret>.
 * Job:  Read the two Monday boards, compose data/districts/jerusalem-services.json
 *       in the shape find-your-district.html expects, and commit it to the
 *       aaronsondavid/magen-website GitHub repo. A GitHub Action watches the
 *       data/ folder and deploys to SiteGround via SFTP.
 *
 * Env secrets:  MONDAY_TOKEN, GITHUB_TOKEN, PUBLISH_SHARED_SECRET
 * Env vars:     DISTRICTS_BOARD_ID, SERVICES_BOARD_ID, GITHUB_REPO, GITHUB_BRANCH, JSON_PATH
 */

const MONDAY_API = "https://api.monday.com/v2";

const TYPE_TO_KEY = {
  "Welfare office":       "welfare_office",
  "Police station":       "police_station",
  "Community centre":     "community_centre",
  "Emergency reference":  "crisis_reference",
  "Magen coordinator":    "magen_coordinator",
  "Rape crisis centre":   "rape_crisis_centre",
  "Mental health clinic": "mental_health_clinic",
  "Bituach Leumi":        "bituach_leumi",
  "Other":                "other",
};

async function gql(env, query, variables = {}) {
  const r = await fetch(MONDAY_API, {
    method: "POST",
    headers: { "Authorization": env.MONDAY_TOKEN, "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });
  const j = await r.json();
  if (j.errors) throw new Error("Monday GraphQL: " + JSON.stringify(j.errors));
  return j.data;
}

async function fetchBoard(env, boardId) {
  const cols = {};
  const items = [];
  const boardMeta = await gql(env,
    `query($b:ID!){ boards(ids:[$b]){ columns{ id title type } } }`, { b: boardId });
  for (const c of boardMeta.boards[0].columns) cols[c.id] = { title: c.title, type: c.type };

  let cursor = null;
  do {
    const q = cursor
      ? `query($b:ID!,$c:String){ boards(ids:[$b]){ items_page(limit:100, cursor:$c){ cursor items{ id name column_values{ id text value } } } } }`
      : `query($b:ID!){ boards(ids:[$b]){ items_page(limit:100){ cursor items{ id name column_values{ id text value } } } } }`;
    const d = await gql(env, q, cursor ? { b: boardId, c: cursor } : { b: boardId });
    const page = d.boards[0].items_page;
    for (const it of page.items) {
      const cv = {};
      for (const c of it.column_values) cv[c.id] = c.text || "";
      items.push({ id: it.id, name: it.name, cv });
    }
    cursor = page.cursor;
  } while (cursor);
  return { cols, items };
}

function colIdByTitle(cols, title) {
  for (const [id, meta] of Object.entries(cols)) if (meta.title === title) return id;
  throw new Error(`Column not found: ${title}`);
}

async function composeJson(env) {
  const [d, s] = await Promise.all([
    fetchBoard(env, env.DISTRICTS_BOARD_ID),
    fetchBoard(env, env.SERVICES_BOARD_ID),
  ]);

  const dSlug = colIdByTitle(d.cols, "Slug (external id)");
  const dPub  = colIdByTitle(d.cols, "Publication status");
  const sDSlug = colIdByTitle(s.cols, "District slug");
  const sType  = colIdByTitle(s.cols, "Service type");
  const sPub   = colIdByTitle(s.cols, "Publication status");
  const fields = {
    "External id": "external_id",
    "Address":     "address",
    "Phone":       "phone",
    "Alt phone":   "alt_phone",
    "Hours":       "hours",
    "Email":       "email",
    "Website":     "website",
    "Notes":       "notes",
  };
  const fieldIds = {};
  for (const label of Object.keys(fields)) fieldIds[label] = colIdByTitle(s.cols, label);

  const byDistrict = {};
  for (const svc of s.items) {
    if (!["Ready to publish","Published"].includes(svc.cv[sPub] || "")) continue;
    const dslug = svc.cv[sDSlug]; if (!dslug) continue;
    const stype = svc.cv[sType] || "Other";
    let key = TYPE_TO_KEY[stype] || "other";
    byDistrict[dslug] ||= {};
    if (byDistrict[dslug][key]) key = `${key}_2`;
    const entry = { name: svc.name };
    for (const [label, outKey] of Object.entries(fields)) {
      const v = svc.cv[fieldIds[label]];
      if (v) entry[outKey] = v;
    }
    byDistrict[dslug][key] = entry;
  }

  const districts = {};
  for (const dist of d.items) {
    if (!["Ready to publish","Published"].includes(dist.cv[dPub] || "")) continue;
    const slug = dist.cv[dSlug]; if (!slug) continue;
    districts[slug] = byDistrict[slug] || {};
  }

  return {
    _meta: {
      description: "Jerusalem district service directory.",
      last_updated: new Date().toISOString(),
      source: `Monday boards ${env.DISTRICTS_BOARD_ID} + ${env.SERVICES_BOARD_ID} (published via Salesforce → Monday sync)`,
      district_count: Object.keys(districts).length,
      service_count: Object.values(districts).reduce((n, d) => n + Object.keys(d).length, 0),
    },
    districts,
  };
}

async function commitToGithub(env, contentString) {
  const base = `https://api.github.com/repos/${env.GITHUB_REPO}/contents/${env.JSON_PATH}`;
  const headers = {
    "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
    "User-Agent":    "magen-district-publisher",
    "Accept":        "application/vnd.github+json",
  };
  // Get current file to fetch its sha
  const currentR = await fetch(`${base}?ref=${env.GITHUB_BRANCH}`, { headers });
  let sha = null;
  if (currentR.ok) { sha = (await currentR.json()).sha; }

  const b64 = btoa(unescape(encodeURIComponent(contentString)));
  const body = {
    message: `Publish Jerusalem district directory (${new Date().toISOString()})`,
    content: b64,
    branch: env.GITHUB_BRANCH,
    ...(sha ? { sha } : {}),
  };
  const put = await fetch(base, { method: "PUT", headers, body: JSON.stringify(body) });
  if (!put.ok) throw new Error(`GitHub write failed: ${put.status} ${await put.text()}`);
  return await put.json();
}

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("POST only", { status: 405 });
    }

    // Read body once (v2); Monday sends {"challenge": "..."} for handshake and
    // for actual events sends {"event": {...}, "challenge": undefined}.
    let bodyText = "";
    try { bodyText = await request.text(); } catch { bodyText = ""; }
    let bodyJson = {};
    try { bodyJson = bodyText ? JSON.parse(bodyText) : {}; } catch { bodyJson = {}; }

    // Monday webhook verification handshake — echo challenge back, no auth check
    if (bodyJson && typeof bodyJson.challenge === "string" && !bodyJson.event) {
      return new Response(JSON.stringify({ challenge: bodyJson.challenge }),
        { status: 200, headers: { "Content-Type": "application/json" } });
    }

    // For real triggers, require the shared secret — either as X-Magen-Secret
    // header (preferred) or as ?s=<secret> query string (fallback for automation
    // UIs that don't let you set custom headers).
    const url = new URL(request.url);
    const secret = request.headers.get("X-Magen-Secret") || url.searchParams.get("s");
    if (secret !== env.PUBLISH_SHARED_SECRET) {
      return new Response("Unauthorised", { status: 401 });
    }

    try {
      const payload = await composeJson(env);
      const body = JSON.stringify(payload, null, 2);
      const commit = await commitToGithub(env, body);
      return new Response(JSON.stringify({
        ok: true,
        district_count: payload._meta.district_count,
        service_count: payload._meta.service_count,
        commit: commit.commit?.sha?.slice(0, 7),
        url: commit.content?.html_url,
      }, null, 2), { status: 200, headers: { "Content-Type": "application/json" } });
    } catch (e) {
      return new Response(JSON.stringify({ ok: false, error: String(e) }, null, 2),
                          { status: 500, headers: { "Content-Type": "application/json" } });
    }
  },
};
