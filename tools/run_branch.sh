#!/usr/bin/env bash
# Track A runner — one OpenSpec change, unattended, on the server.
#
#   tools/run_branch.sh <change-slug>
#
# Implements the flow in plan v2 §5.2. Invariants it enforces:
#   - works only on ror/<slug>; never merges, never touches master
#   - opens a PR only when T1 is green
#   - a killed run leaves an unmerged branch and a log line, never a
#     half-written tree on a shared branch
#   - one run = one branch; bounded scope is the quality lever and, under
#     C3, the only budget lever available
#
# Archiving is NOT done here. `openspec archive` is a claim of completion,
# and per AGENTS.md §5 the agent does not get to make that claim — it runs
# after the owner merges.

set -uo pipefail

SLUG="${1:-}"
if [[ -z "$SLUG" ]]; then
  echo "usage: tools/run_branch.sh <change-slug>" >&2
  exit 2
fi

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCH="ror/$SLUG"
WORKTREE="${ROR_WORKTREE_DIR:-$HOME/ror-work}/$SLUG"
LOG_DIR="$REPO/telemetry/runs"
LOG="$LOG_DIR/$(date +%Y%m%d-%H%M%S)-$SLUG.log"
mkdir -p "$LOG_DIR"

WALL_CLOCK="${ROR_WALL_CLOCK:-5400}"      # 90 min. Tune by observation.
START_FLOOR="${ROR_START_FLOOR:-80}"
ABORT_FLOOR="${ROR_ABORT_FLOOR:-60}"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

# --- preflight: budget ------------------------------------------------------
# Spike S5 is unresolved: there is no supported way to read Codex quota
# programmatically. The plan's rule is fail closed — a quota read that does
# not work means skip the run, never proceed blindly. `quota_remaining` is
# the single place to wire a real reader when one exists.
quota_remaining() {
  if [[ -n "${ROR_QUOTA_CMD:-}" ]]; then
    $ROR_QUOTA_CMD 2>/dev/null && return 0
    return 1
  fi
  return 1
}

if remaining=$(quota_remaining); then
  log "quota: ${remaining}% weekly remaining"
  if (( remaining < START_FLOOR )); then
    log "SKIP: ${remaining}% < ${START_FLOOR}% start floor"
    exit 0
  fi
elif [[ "${ROR_ALLOW_UNMETERED:-0}" != "1" ]]; then
  log "SKIP: cannot read quota and ROR_ALLOW_UNMETERED is not set (fail closed, S5)"
  exit 0
else
  log "WARNING: proceeding without a quota reading — ROR_ALLOW_UNMETERED=1"
fi

# --- the change must exist and be owner-approved ---------------------------
CHANGE_DIR="$REPO/openspec/changes/$SLUG"
if [[ ! -d "$CHANGE_DIR" ]]; then
  log "ABORT: no change folder at openspec/changes/$SLUG"
  log "       Track A changes are proposed by the owner in a design session (C1/C5)."
  log "       The runner never invents its own work — see plan Non-goals."
  exit 2
fi

# --- worktree --------------------------------------------------------------
cd "$REPO" || exit 2
log "fetching"
git fetch -q origin
git fetch -q upstream 2>/dev/null || true

if git show-ref --quiet "refs/heads/$BRANCH"; then
  log "branch $BRANCH exists; resuming"
else
  git branch "$BRANCH" origin/master
fi

rm -rf "$WORKTREE"
mkdir -p "$(dirname "$WORKTREE")"
git worktree prune
git worktree add -q "$WORKTREE" "$BRANCH" || { log "ABORT: worktree failed"; exit 1; }
log "worktree: $WORKTREE on $BRANCH"

cd "$WORKTREE" || exit 1

# --- implementation --------------------------------------------------------
# The OpenSpec apply workflow is a skill, not a slash command, when the target
# is Codex — `openspec init` writes it to .agents/skills/openspec-apply-change.
# Spike S7 confirmed `codex exec` runs non-interactively and can drive the
# openspec CLI; it needs unprivileged user namespaces enabled for its sandbox
# (kernel.unprivileged_userns_clone=1 on Ubuntu 24.04).
PROMPT=$(cat <<EOF
Implement the OpenSpec change '$SLUG' in this repository.

Read, in this order:
  1. AGENTS.md — the domain layer and the hard gates
  2. .agents/skills/openspec-apply-change/SKILL.md — the apply workflow
  3. openspec/changes/$SLUG/ — the approved proposal, design and tasks

Then load the relevant ror-* skill before each kind of edit:
  .agents/skills/ror-focus-tree   before any common/national_focus/ edit
  .agents/skills/ror-event-chain  before any events/ edit
  .agents/skills/ror-voice        before writing ANY player-facing text
  .agents/skills/ror-validation   to run and read the checks

Work the tasks.md checklist. After each task run:
  tools/ror_lint.py --baseline tools/upstream-baseline.json
and fix what it reports before moving on.

Hard rules:
  - Do not commit to master. Do not merge. Do not rebase.
  - Do not run 'openspec archive' — completion is the owner's call.
  - A world-iterating on_action (on_weekly/on_daily/on_monthly without a TAG
    suffix) is a HARD STOP: report it as a blocker instead of implementing it.
  - Never use <= or >=.
  - Localisation is Russian only, UTF-8 with BOM.

Finish with a report containing a section headed
'Simplifications, omissions, and blockers'. If there were none, say so
explicitly and give evidence. Do not pad the report with checks that merely
restate the rules above.
EOF
)

log "starting codex exec (wall clock ${WALL_CLOCK}s)"
timeout "$WALL_CLOCK" codex exec \
  -C "$WORKTREE" \
  -s workspace-write \
  --skip-git-repo-check \
  "$PROMPT" 2>&1 | tee -a "$LOG"
CODEX_RC=${PIPESTATUS[0]}

if (( CODEX_RC == 124 )); then
  log "wall-clock cap hit; leaving the branch unmerged for the next slot"
elif (( CODEX_RC != 0 )); then
  log "codex exited $CODEX_RC"
fi

# --- gate ------------------------------------------------------------------
cd "$WORKTREE" || exit 1
if [[ -z "$(git status --porcelain)" ]]; then
  log "no changes produced; nothing to open a PR for"
  exit 0
fi

log "T1"
if ! python3 tools/ror_lint.py --baseline tools/upstream-baseline.json 2>&1 | tee -a "$LOG"; then
  log "T1 FAILED — branch left unmerged, no PR. This is the intended outcome."
  exit 1
fi

log "graph"
python3 tools/build_graph.py --no-blame >>"$LOG" 2>&1 || log "graph build failed (non-fatal)"

git add -A
git commit -q -m "$SLUG

Implemented from openspec/changes/$SLUG by the Track A runner.

Co-Authored-By: Codex <noreply@openai.com>" || true
git push -q -u origin "$BRANCH" 2>&1 | tee -a "$LOG"

if command -v gh >/dev/null; then
  gh pr create --base master --head "$BRANCH" \
    --title "$SLUG" \
    --body-file <(cat <<EOF
Implemented from \`openspec/changes/$SLUG\`.

T1 green against \`tools/upstream-baseline.json\`.

**Not run:** T2 (CWTools, spike S2 open), T3 (tree render, spike S3 open).
T4 is available on the server via \`tools/t4_boot.sh\` but is not wired into
this runner yet.

Run log: \`${LOG#$REPO/}\`

See the agent's report in the run log for the
'Simplifications, omissions, and blockers' section. Read that before the diff.
EOF
) 2>&1 | tee -a "$LOG"
else
  log "gh not available; branch pushed, open the PR by hand"
fi

log "done"
