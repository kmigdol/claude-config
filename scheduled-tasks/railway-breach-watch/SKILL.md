---
name: railway-breach-watch
description: Hourly: read Railway incident updates; check Supabase, Vercel, Railway and OpenAI usage for access by anyone but us
---

You are watching for fallout from Railway's security incident of 2026-10-21. An unauthorized party may have read decrypted Railway environment variables. nextbest (Kayleigh's skincare site) stores these secrets in Railway (project "attractive-vision", environment "production"): OPENAI_API_KEY, DATABASE_URL (Supabase prod Postgres), SUPABASE_KEY (Supabase sb_secret key, also used by Vercel), VERCEL_TOKEN, VERCEL_DEPLOY_HOOK_URL, plus Reddit, Amazon Creators, Awin, Rakuten, Sentry, PostHog and Prefect credentials.

This is READ-ONLY. Never rotate, revoke or change any secret, env var, deployment or setting. Kayleigh does all rotation herself.

Work from /Users/kayleigh/dev/nextbest. Keep state in ~/.cache/nextbest/railway-breach-watch.json (create it if it doesn't exist). It holds the last Railway update seen and any IPs already reported, so you only report what is NEW.

## Steps

1. **Railway news.** Fetch https://status.railway.com/ and https://blog.railway.com/p/security-disclosure-wednesday-october-21st with WebFetch. Note any update newer than the one in the state file. Look especially for: the access time window, which customers are affected, whether builds and deployments have resumed, and any new instructions for customers.

2. **Supabase prod (project ref rfejgzsgzkfhnaynfjaq).** Use the Supabase MCP `query_logs` tool (load it with ToolSearch "query_logs execute_sql"; pass project_id). Cover the window since the last run, or the last 2 hours if there is no state yet.
   - Secret-key REST calls: `source='edge_logs'`, where `log_attributes['request.sb.apikey.apikey.prefix']` or `['request.sb.apikey.authorization.prefix']` starts with `sb_secret`. Group by `log_attributes['request.headers.cf_connecting_ip']`, `request.cf.asOrganization`, `request.cf.country`, `request.headers.user_agent`, with count and non-GET count.
     - Expected: AWS Virginia orgs (Amazon Data Services Northern Virginia / Amazon Technologies Inc. / Amazon.com, Inc.) with UA `node` (Vercel). Org "Railway" with UA `python-httpx/*`. Verizon Business IP 71.120.19.214 (Kayleigh's home).
     - Flag anything else: a non-US country, another org, an odd user agent, or writes from an unknown source.
   - Direct DB logins: `source='supavisor_logs'` with an `event_message` containing "Connection authenticated". Group by `log_attributes['peer_ip']` and `['user']`.
     - Expected: private 10.x IPs; Railway AS400940 IPs (e.g. 162.220.232.159 = the daily pipeline 10:00–~21:00 UTC; 152.55.178.38 = the retailer-refresh cron around 07:00 UTC); 71.120.19.214; user `posthog_reader` from AWS IPs around 04:00 UTC and on the hour.
     - Look up any other public IP with `curl -s https://ipinfo.io/<ip>/json` and flag it if it isn't Railway, AWS, Supabase or Kayleigh.

3. **Vercel (team team_U4P2EcHH7Nx4ZDKhzsfAhANZ, project prj_AU3PyaiBiVuWWDm9DQStn62UoKX5).** Run `vercel api "/v3/events?teamId=team_U4P2EcHH7Nx4ZDKhzsfAhANZ&since=<window start ISO>&limit=100" --method GET`.
   - Expected: deployments by kmigdol from kmigdol/nextbest, "railway-trigger hook" deploys just after the daily pipeline finishes, alias assignments and env-variable-masked events.
   - Flag: new tokens, members, env var changes, domain changes, deploys from an unknown repo or user, or hook deploys at odd times.

4. **Railway deploys.** Run `railway deployment list -s <svc> -e production --json` for nextbest, prefect-worker, prefect-server, retailer-refresh and Postgres. Flag any deploy whose commit isn't on kmigdol/nextbest `main` (check with `git cat-file -t <sha>` after `git fetch origin`), and any variable-change trigger.

5. **OpenAI key status.** For each of the nextbest, prefect-worker and retailer-refresh services, pipe the key straight into curl, `railway variables -s <svc> -e production --json | jq -r .OPENAI_API_KEY`, then call `https://api.openai.com/v1/models`. Report the key's last 4 characters and the HTTP code: 200 means live, 401 means revoked. Never print or log more of the key than those last 4 characters.
   - Baseline at 2026-10-22 ~00:00 UTC: all three services hold `...5RkA` (key "nextbest-mig"). Kayleigh revoked it herself on 2026-10-21 and it returns 401.
   - Until Kayleigh puts a new key in Railway and builds resume, the daily pipeline's OpenAI stages will fail. Say this once per run while it is still true.

6. **OpenAI usage (dashboard, via Claude in Chrome).** Load the Chrome tools in one ToolSearch call (`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__tabs_close_mcp`). Open a new tab and close it when you are done. If Chrome isn't connected or the page asks for a sign-in, say "OpenAI usage: not checked (Chrome unavailable / signed out)" and move on. Never sign in or type credentials.
   - Go to https://platform.openai.com/api-keys and read it with get_page_text. For every key, record name, status, created date, last used and monthly spend.
     - Baseline at 2026-10-22: "nextbest-mig" Revoked, last used Oct 21, $103.83 this month. "remix" Active, last used Aug 27, $0.00. "nextbest" Revoked, last used Oct 18, $0.00.
     - Flag: any key not in the baseline that wasn't created by Kayleigh Migdol. Any key whose "last used" moves later than its baseline. Any jump in a key's monthly spend since the last run. A new key that Kayleigh created is expected (her rotation); report its name and spend.
   - Go to https://platform.openai.com/usage?date_range=7d. Make sure the project filter shows "All projects": if a "Default project ×" chip is present, click its ×. Take a screenshot. Read the total spend, today's bar, the "October spend" figure and the API Keys tab on the right.
     - Our normal spend is about $4–21/day, nearly all during the daily pipeline (10:00–21:00 UTC).
     - Flag: usage on a key outside the baseline, spend today while every Railway key is revoked and no new key exists, or a daily total above $30.
   - Store the per-key spend and the October total in the state file, so the next run can compare against them.

7. **Reddit app quota (someone else using our leaked Reddit credentials).** Kayleigh can't get a new Reddit app, so this secret was NOT rotated. Never reset, delete or edit the Reddit app. Run this probe. It pipes the secrets straight through and never prints them:
   ```bash
   V=$(railway variables -s nextbest -e production --json); ID=$(echo "$V"|jq -r .REDDIT_CLIENT_ID); SE=$(echo "$V"|jq -r .REDDIT_CLIENT_SECRET); UA='nextbest:v0.1 (by /u/nextbest-app)'
   T=$(curl -s -u "$ID:$SE" -A "$UA" -d grant_type=client_credentials https://www.reddit.com/api/v1/access_token | jq -r '.access_token // empty')
   [ -z "$T" ] && echo "TOKEN FAILED" || curl -s -o /dev/null -D - -A "$UA" -H "Authorization: bearer $T" https://oauth.reddit.com/r/SkincareAddiction/about | grep -iE '^(HTTP|x-ratelimit)'
   ```
   - Baseline at 2026-10-22 00:40 UTC: token OK, `x-ratelimit-used: 1`, `remaining: 999`. That is our probe alone. The quota is about 1000 requests per 10-minute window.
   - Our own scraper only calls Reddit during the daily pipeline, which runs from 10:00 UTC to about 13:00 UTC (the scrape stage comes first).
   - Flag:
     - `x-ratelimit-used` above about 5 while our scrape isn't running. Re-run the probe once to confirm.
     - Any 429.
     - TOKEN FAILED, or a 401/403. That means the secret was reset, or Reddit suspended the app; say which, if it's clear.
   - Caveat to keep in mind: Reddit may count the quota per access token rather than per app. In that case this probe can't see someone else's use. Treat "used: 1" as "nothing seen", not proof of no abuse.

## Output

Write in plain, short sentences.
- **Nothing new or suspicious:** one line, e.g. "Railway watch HH:MM UTC: no new Railway update, no unknown access. OpenAI: Railway key ...5RkA revoked, Oct spend $299.20 (no change), no new keys. Reddit quota 1/1000 (no outside use). Builds still paused."
- **Otherwise:** lead with the finding. Name the IP or event, when it happened, and what it touched. Then give the new Railway update in 1–3 bullets.
- **Builds resumed:** say so prominently. That is when Kayleigh can rotate secrets without breaking services.
- **Railway marks the incident resolved and 24h have passed with nothing suspicious:** say this watch can be turned off.

Update the state file at the end of every run.