#!/usr/bin/env bash
# T4 — headless boot smoke test.
#
# Launches HOI4 under Xvfb with software rendering, waits for the main menu,
# kills it, and diffs error.log against a baseline. New lines are the finding.
#
#   tools/t4_boot.sh --baseline          # boot WITHOUT the mod, write baseline
#   tools/t4_boot.sh                     # boot WITH the mod, diff vs baseline
#
# Server-only. Requires the settings established by spike S1:
#   - steamclient.so symlinked into ~/.steam/sdk64 (SteamAPI init)
#   - multi_sampling=0 in settings.txt (it crashes at 4 with llvmpipe)
#   - LIBGL_ALWAYS_SOFTWARE=1
#
# Known limitation: without a running Steam client the game reports
# `Active DLC Count: 0`. Harmless for a boot smoke test, but it means this
# is NOT a faithful basis for Lane B2 telemetry — see docs/tooling-decisions.md.

set -uo pipefail

GAME_ROOT="${HOI4_GAME_ROOT:-$HOME/.local/share/Steam/steamcmd/~/hoi4-download}"
DATA_DIR="${HOI4_DATA_DIR:-$HOME/.local/share/Paradox Interactive/Hearts of Iron IV}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASELINE="$REPO/telemetry/error-baseline.txt"
TIMEOUT="${T4_TIMEOUT:-200}"

mode="candidate"
[[ "${1:-}" == "--baseline" ]] && mode="baseline"

if [[ ! -x "$GAME_ROOT/hoi4" ]]; then
  echo "T4: no HOI4 at $GAME_ROOT — set HOI4_GAME_ROOT" >&2
  exit 2
fi

# Enable or disable the mod for this run.
mkdir -p "$DATA_DIR/mod"
cat > "$DATA_DIR/mod/ror.mod" <<EOF
name="Revolution or Reaction (fork)"
path="$REPO"
supported_version="1.19.*"
EOF
if [[ "$mode" == "baseline" ]]; then
  printf '{\n\t"enabled_mods": [],\n\t"disabled_dlcs": []\n}\n' > "$DATA_DIR/dlc_load.json"
else
  printf '{\n\t"enabled_mods": ["mod/ror.mod"],\n\t"disabled_dlcs": []\n}\n' > "$DATA_DIR/dlc_load.json"
fi

# The game rewrites settings.txt on exit, so these are reapplied every run
# rather than set once (the same reason the plan prefers save melting over
# save_as_binary=no).
if [[ -f "$DATA_DIR/settings.txt" ]]; then
  sed -i 's/multi_sampling=[0-9]*/multi_sampling=0/; s/vsync=yes/vsync=no/' "$DATA_DIR/settings.txt"
fi

rm -rf "$DATA_DIR/logs"
echo "T4: booting ($mode), ${TIMEOUT}s cap..."
( cd "$GAME_ROOT" && \
  SDL_AUDIODRIVER=dummy LIBGL_ALWAYS_SOFTWARE=1 \
  timeout "$TIMEOUT" xvfb-run -a -s "-screen 0 1280x720x24" ./hoi4 -debug ) >/dev/null 2>&1

LOG="$DATA_DIR/logs/error.log"
if [[ ! -f "$LOG" ]]; then
  echo "T4: FAIL — no error.log produced; the game did not start" >&2
  exit 1
fi

if ! grep -aq "Startup time" "$DATA_DIR/logs/setup.log" 2>/dev/null; then
  echo "T4: FAIL — never reached the main menu" >&2
  tail -5 "$DATA_DIR/logs/system.log" 2>/dev/null >&2
  exit 1
fi
echo "T4: reached main menu — $(grep -ah 'Startup time' "$DATA_DIR/logs/setup.log" | tail -1)"

# Normalise: drop timestamps and game dates so the diff is about content.
# Sound-effect spam is excluded — the server has no audio device and the
# resulting noise would bury everything else.
normalise() {
  grep -av "sound effect" "$1" \
    | sed -E 's/^\[[0-9:]+\]\[[^]]*\]//' \
    | sort -u
}

mkdir -p "$(dirname "$BASELINE")"
if [[ "$mode" == "baseline" ]]; then
  normalise "$LOG" > "$BASELINE"
  echo "T4: baseline written — $(wc -l < "$BASELINE") distinct lines -> $BASELINE"
  exit 0
fi

if [[ ! -f "$BASELINE" ]]; then
  echo "T4: no baseline at $BASELINE. Run: tools/t4_boot.sh --baseline" >&2
  exit 2
fi

NEW=$(mktemp)
normalise "$LOG" > "$NEW"
DIFF=$(comm -13 "$BASELINE" "$NEW")
COUNT=$(printf '%s' "$DIFF" | grep -c . || true)

echo "T4: $COUNT error line(s) not in the baseline"
if (( COUNT > 0 )); then
  printf '%s\n' "$DIFF" | head -40
  (( COUNT > 40 )) && echo "  ... and $((COUNT - 40)) more"
fi
rm -f "$NEW"

# Advisory by default: upstream already contributes thousands of these, and
# failing the gate on inherited noise would make it useless. Set
# T4_FAIL_ON_NEW=1 once a branch-scoped baseline exists.
[[ "${T4_FAIL_ON_NEW:-0}" == "1" && $COUNT -gt 0 ]] && exit 1
exit 0
