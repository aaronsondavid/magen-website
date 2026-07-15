# Magen District Publisher — Cloudflare Worker

Reads the two Monday boards (Jerusalem District Directory + Jerusalem Services), composes `data/districts/jerusalem-services.json`, and commits it to the `aaronsondavid/magen-website` GitHub repo. A GitHub Actions workflow (`.github/workflows/deploy-district-data.yml`) picks up the commit and SFTPs the JSON to SiteGround.

## One-time setup

1. **Cloudflare account** — free tier is fine. Install the Wrangler CLI:
   ```
   npm install -g wrangler
   wrangler login
   ```

2. **Deploy the Worker**:
   ```
   cd _cloudflare-worker
   wrangler deploy
   ```
   Note the URL Wrangler prints (e.g. `https://magen-district-publisher.<subdomain>.workers.dev`).

3. **Set secrets** (each command prompts for the value):
   ```
   wrangler secret put MONDAY_TOKEN
   wrangler secret put GITHUB_TOKEN
   wrangler secret put PUBLISH_SHARED_SECRET
   ```
   - `MONDAY_TOKEN`: your Monday API token (same one in `~/.monday_token`).
   - `GITHUB_TOKEN`: a GitHub PAT with `repo:contents:write` on `aaronsondavid/magen-website`. Fine-grained token, single-repo scope recommended.
   - `PUBLISH_SHARED_SECRET`: any long random string. Monday's automation will send this back so the Worker knows it's a real trigger.

4. **GitHub Actions secrets** (in the `aaronsondavid/magen-website` repo → Settings → Secrets):
   - `SITEGROUND_SFTP_USER`: `u1214-6mgzp0hmri36` (from `~/.ssh/config`)
   - `SITEGROUND_SFTP_PASSWORD`: your SiteGround SFTP password
   - `SITEGROUND_SITE_ID`, `SITEGROUND_API_TOKEN`: optional, for the cache-purge step. Skip if you don't have the API token.

## Wire the Monday button

On the Jerusalem District Directory board (id `5100388371`):

1. Change the **Publish trigger** column status to `Publish now` — this is what staff click.
2. Add an automation: **Board → Automations → Custom Automation** →
   - Trigger: `When status changes to something → Publish now (Publish trigger column)`
   - Action: `Send a webhook`
   - URL: `https://magen-district-publisher.<subdomain>.workers.dev`
   - Method: `POST`
   - Custom header: `X-Magen-Secret: <the shared secret you set>`
   - Body: `{}` (empty JSON)
3. Save and enable the automation.

## The publish loop

```
Staff flip 'Publish trigger' → Publish now
   ↓ Monday automation
Cloudflare Worker (this project)
   ↓ Reads Monday boards, composes JSON
GitHub commit to aaronsondavid/magen-website
   ↓ GitHub Action fires (deploy-district-data.yml)
SFTP → SiteGround preview.magen-israel.org/data/districts/
   ↓
find-your-district.html serves fresh data
```

## Local dev
Run locally with:
```
wrangler dev
```
Then POST to `http://localhost:8787` with the `X-Magen-Secret` header to test.
