You are triggering the Mirage intraday daemon. This routine does exactly
one thing: kick off the GitHub Actions workflow that runs
scripts/mirage_daemon.py, because GitHub Actions' own `schedule:` cron
trigger proved unreliable (fired 5.5 hours late on day 1, didn't fire at
all on day 2 — this is documented GitHub behavior, no SLA on scheduled
workflows, especially for lower-traffic repos). This routine's own cron
(via Claude Code's RemoteTrigger scheduler) has been reliable all session
for every other routine, so it does the triggering instead.

IMPORTANT — ENVIRONMENT VARIABLES:
- GITHUB_TOKEN is already exported. REQUIRED (hard stop if missing):
  GITHUB_TOKEN. This token must have "Actions: Read and write" permission
  in addition to "Contents: Read and write" (needed by other routines) —
  if the dispatch call below returns 403/404, that's the most likely
  cause; report it plainly rather than retrying blindly.
  [[ -n "${GITHUB_TOKEN:-}" ]] && echo "GITHUB_TOKEN: set" || echo "GITHUB_TOKEN: MISSING"

STEP 1 — Trigger the workflow via the GitHub API (no repo clone needed —
this routine doesn't touch any files):
curl -fsS -X POST \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/nkaiwar2010-wq/Trading-Bot-NK/actions/workflows/mirage-daemon.yml/dispatches" \
  -d '{"ref":"main"}'

STEP 2 — Verify it actually started (the dispatch call above returns no
body on success, so confirm separately):
sleep 5
curl -fsS "https://api.github.com/repos/nkaiwar2010-wq/Trading-Bot-NK/actions/workflows/mirage-daemon.yml/runs?per_page=1" \
  -H "Authorization: Bearer ${GITHUB_TOKEN}"
Check the most recent run's created_at is within the last minute and
status is "queued" or "in_progress". If not, report the failure clearly
(this routine does not retry or fall back — a human should look at it).

This routine makes no git commits — its only job is the trigger above.
