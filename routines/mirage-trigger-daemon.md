You are triggering the Mirage intraday daemon. This routine does exactly
one thing: fire the GitHub Actions workflow that runs
scripts/mirage_daemon.py, by pushing a commit that touches
.github/mirage-trigger.txt (the workflow is configured to run on `push`
to that specific path). This exists because two other trigger mechanisms
both failed: GitHub Actions' own `schedule:` cron proved unreliable
(fired 5.5 hours late on day 1, didn't fire at all on day 2 — documented
GitHub behavior, no SLA), and calling GitHub's REST API directly
(`workflow_dispatch` via curl) was blocked at the Claude Code
session/proxy level (needs a GitHub App org connection this project
doesn't have). A plain git push is something these routines already do
reliably every day — this uses that instead of either broken path.

STEP 0 — CLONE THE REPO (mandatory first action, fresh sandbox each run):
git clone https://x-access-token:${GITHUB_TOKEN}@github.com/nkaiwar2010-wq/Trading-Bot-NK.git ~/trading-bot
cd ~/trading-bot

IMPORTANT — ENVIRONMENT VARIABLES:
- GITHUB_TOKEN is already exported. REQUIRED (hard stop if missing):
  GITHUB_TOKEN. Only "Contents: Read and write" permission is needed —
  the same scope every other routine already uses for git push. No
  special Actions permission needed with this approach.

STEP 1 — Touch the trigger file and push:
echo "last triggered: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> .github/mirage-trigger.txt
git add .github/mirage-trigger.txt
git commit -m "trigger mirage daemon $(date -u +%Y-%m-%d\ %H:%M)Z"
git push https://x-access-token:${GITHUB_TOKEN}@github.com/nkaiwar2010-wq/Trading-Bot-NK.git main
On push failure: git pull --rebase https://x-access-token:${GITHUB_TOKEN}@github.com/nkaiwar2010-wq/Trading-Bot-NK.git main, then push again. Never force-push.

STEP 2 — Report plainly whether the push succeeded. This routine cannot
verify the workflow actually started (that would need the same blocked
GitHub API access) — a successful push to the trigger path is the
expected, sufficient signal; if the workflow still doesn't run, a human
needs to check GitHub Actions directly since this routine has no way to
see that from here.
