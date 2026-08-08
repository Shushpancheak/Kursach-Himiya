# Tooling decisions and spike results

Why the pipeline is shaped the way it is. Written so that nobody re-runs an investigation whose answer is already known.

Plan documents: `ror-agent-loop-plan-v2.md` (authoritative), `ror-plan-addendum-A-tooling-survey.md`, `ror-agent-loop-plan.md` (history).

---

## S6 — Claude config isolation: **RESOLVED**

The variable is **`CLAUDE_CONFIG_DIR`**, confirmed against the shipped binary (2.1.220), not from memory or docs. `CLAUDE_SECURESTORAGE_CONFIG_DIR` also exists and is separate — it governs credential storage, not skills and settings.

`.envrc` sets it to `$HOME/.claude-ror`. Applied by `direnv` on directory entry, so it cannot be defeated by forgetting an alias.

Two caveats worth knowing:

- It takes effect in **new** sessions started inside the repo. A session already running when `.envrc` was added keeps the config it started with.
- The isolated directory starts empty, so the first session there needs a fresh login.

Project-scope `permissions.deny` in `.claude/settings.json` covers the owner's work source roots and credential files. Note that user-scope settings on this machine grant broad access; `deny` rules take precedence, which is what makes the project-scope list load-bearing rather than decorative.

---

## S9 — `hoi4skill validate` on unmodified upstream: **FAIL**

`hoi4skill 0.30.2`, run against the fork point with no `--game-root`: **1,439 errors, 23,097 warnings.**

The plan's calibration rule says a tool that fails on upstream is wrong until proven otherwise. Verified category by category:

| Finding | Count | Verdict |
|---|---|---|
| `focus missing relative_position_id` / `uses relative_position_id` | 1,082 | **House style.** Absolute `x`/`y` is legal HOI4. This is its own generator's convention. |
| `idea picture must omit GFX_idea_ prefix` | 119 | **Plausibly real, unresolved.** See N-01 in [known-upstream-defects.md](known-upstream-defects.md). |
| `focus missing completion_reward` | 66 | Real; this repo checks it as `P001`. |
| `£icon£ has no icon name` | 50 | **False positive.** See below. |
| brace imbalance | 20 | **Real**, independently confirmed. |
| `§` colour balance | 15 | 4 real, rest over-strict. |

Warnings are ~90% noise: 10,167 are "missing recommended *generated-template* field" and roughly 4,000 are sprite lookups that cannot resolve without a game root.

### The `£` tokenizer bug

hoi4skill flags **all 37** paired `£victory_points£` forms in this mod and **none of the 208** unpaired `£command_power` forms. It reads the closing `£` as a new marker with an empty name. Both forms are valid, and the flagged strings are vanilla-derived (`EFFECT_ADD_VP`, `MINIMUM_SEAZONE_DOMINANCE_NEEDED`).

### Where it was right

Its brace checker agreed with this repo's independent parser on **20 of 20** files, matching sign and depth. One disagreement: `PRM_contra_2.0.txt`, which hoi4skill called a depth-2 brace imbalance. Raw braces there are 28/28; the actual defect is an unterminated string. Its report was an artefact of its own string handling — right file, wrong reason.

---

## S10 — coverage overlap: **RESOLVED. Do not adopt hoi4skill.**

Re-run on 2026-08-08 with `--game-root` pointed at the real vanilla install, which is what Addendum A said was needed to settle it.

**It got worse, not better: 1,439 errors → 7,418.**

The dominant categories are demonstrably wrong:

| Category | Count | Verdict |
|---|---|---|
| `unknown trigger` | 2,179 | **2,131 are `CONTROLLER`, `OWNER` and `IF`** — scope changers, not triggers. 97.8% false positive in its largest category. |
| `unknown effect` | 999 | `token` and `iteration_output` (261 each) are `special_projects` schema fields; a further 239 are the same scope changers. |
| `idea picture must omit GFX_idea_` | 119 | **Disproved.** All 119 resolve via the engine's verbatim fallback, which vanilla itself relies on 20 times. See N-01. |
| `unknown modifier` | 258 | Not individually verified; the prior is poor. |
| focus layout opinions | ~1,082 | Its own generator's house style. Absolute `x`/`y` is legal. |

It does not model Clausewitz scope changers. In a mod whose triggers are full of `CONTROLLER = { ... }` and `OWNER = { ... }`, that is disqualifying on its own.

**What it got right, and what we kept:** its brace checker agreed with our parser on 20 of 20 files. That check now lives in `tools/clausewitz.py`, verified independently, so nothing is lost by dropping the tool.

**Decision: hoi4skill is not part of this pipeline.** The binary stays in `$ROR_REFS/hoi4skill/bin/` at `v0.30.2` for occasional cross-checking, invoked as a separate process (GPL-3.0-only — do not vendor or link its source). Addendum A's premise, that half of T1 already existed, did not survive contact with the mod. `tools/ror_lint.py` stands alone.

**What we own, and now verify:** geometry and coordinate collisions, AND-of-OR prerequisite semantics, UTF-8 BOM, focus and idea sprite resolution (with the vanilla index and both engine fallbacks), graph integrity, the period lexicon.

---

## S1 — headless HOI4 on the GPU-less server: **PASS**

The highest-severity risk in the register (R1). Retired.

The game reaches the main menu under Xvfb with Mesa llvmpipe in ~26 s, **with the mod loaded** — `[1917.01.01.01][frontend.cpp:177]: Startup time: 26226ms`. The 1917 date is RoR's, not vanilla's 1936, so the mod is genuinely active.

Three things were required, none of them obvious:

1. **`steamclient.so` symlinked into `~/.steam/sdk64/`.** Without it SteamAPI cannot initialise and the game crashes. The file ships with steamcmd at `steamcmd/linux64/steamclient.so` but nothing links it.
2. **`multi_sampling=0` in `settings.txt`.** It crashed reproducibly at `Using multisampling: 4` with `Video memory: 0` reported by llvmpipe.
3. **`LIBGL_ALWAYS_SOFTWARE=1`**, and `SDL_AUDIODRIVER=dummy` to stop 2,235 lines of missing-sound-effect spam (the server has no audio device).

### DLC on a headless server — **SOLVED. `Active DLC Count: 36`.**

This took three separate fixes and the root cause was not what it looked like.

`dlc_load.json` is a dead end: its `disabled_dlcs` list turns owned DLC *off*, it cannot turn unowned DLC *on*.

1. **The Steam client must be running**, not just steamcmd. `steam-installer` hard-blocks on a zenity dialog ("Steam is proprietary… Install/Cancel") that nobody can click headless — a stub `zenity` in `~/bin` that `exit 0`s answers it.
2. **The client needs one interactive login.** steamcmd's cached token is not interchangeable: steamcmd logged in fine as `[U:1:84616051]` while the client sat at `[U:1:0]`, because there was no `loginusers.vdf` and no `AutoLoginUser`. Done once over VNC (`~/bin/steam-gui.sh` starts Xvfb :99 + x11vnc on localhost:5900). After that the client auto-logins headless forever.
3. **The real cause.** Even logged in, DLC stayed at 0. `steamcmd --force_install_dir` installs *outside any Steam library*, so the client does not know the game exists and reports every DLC as not installed. The fix is to make the install visible to the client:

```bash
S=~/.local/share/Steam/steamapps
cp "$GAME/steamapps/appmanifest_394360.acf" "$S/"
ln -sfn "$GAME" "$S/common/Hearts of Iron IV"
```

Restart Steam, and `libraryfolders.vdf` gains `"394360"`. **`Active DLC Count: 36`.**

Note macOS Screen Sharing will not connect to a `-nopw` VNC server — it hangs waiting for authentication. x11vnc needs `-rfbauth`.

### T4's baseline is empty, which is the best possible outcome

**Vanilla with all 36 DLC active writes a completely empty `error.log`.** Every line the candidate run produces therefore belongs to the mod — no allowlist tuning, no inherited noise.

This also explains the earlier vanilla errors (`game rule LIT_ai_behavior does not exist` and friends): they were DLC-gated content failing *because DLC was inactive*, not vanilla defects.

Current signal: **2,526 error lines from the mod**, including classes no static tier can reach —

- `Unknown effect-type: BLR_bzns_low_popularity_increase_effect` (`common/decisions/npt_BLR_decisions.txt:730`) — a scripted effect that does not exist
- `Undefined ideology: democratic` (`history/countries/RUS - Reichskommisariat Nordamerika.txt:160`)
- `SubUnit <hq_engineer> attempts to unlock ability deeper_dig_in, which doesn't exist`
- `Duplicate subunit category: category_army`

`tools/t4_boot.sh` implements the test. It refuses to proceed when `Active DLC Count` is 0, because a DLC-less run is not comparable to a DLC-ful one — the mod gates on 13 of them, so the loaded content genuinely differs. Override with `T4_REQUIRE_STEAM=0`.

### What T4 found that T1 could not

The boot produced 5,183 non-sound errors with the mod loaded against ~53 for vanilla alone. One category was a genuine gap in the static checks: **1,002 `Texture Handler encountered missing texture file` lines** — sprites that *are* declared in a `.gfx` but whose `texturefile` does not exist. T1 only checked the other direction, icon → declaration, and never followed the declaration to disk.

That is now `R009`. It reproduces the game's own finding exactly: `gfx/interface/goals/LIT/LIT_agrarien_refor.dds` is declared but absent — the real file is `LIT_agrarien_refor**m**.dds`.

Because vanilla's `gfx/` is ~900 MB of `.dds` and is not synced to the Mac, `R009` checks a generated path manifest instead:

```bash
cd "$HOI4_GAME_ROOT" && find gfx dlc integrated_dlc -type f \
  \( -iname '*.dds' -o -iname '*.tga' -o -iname '*.png' \) | sort \
  > "$ROR_REFS/hoi4-vanilla-assets.txt"
```

39,214 paths, 2.3 MB. Regenerate after a HOI4 update.

## S7 — driving OpenSpec from `codex exec`: **PASS**

`codex exec` runs fully non-interactively — `approval: never`, `sandbox`, `-C <dir>`, `--ephemeral`, and `--output-schema` for structured results. It executes shell commands in the repo and runs the `openspec` CLI successfully.

One infrastructure blocker, now fixed: Codex sandboxes commands with bubblewrap, and **Ubuntu 24.04 blocks unprivileged user namespaces**, so every command failed with `bwrap: No permissions to create a new namespace`. Persisted in `/etc/sysctl.d/60-codex-userns.conf`:

```
kernel.apparmor_restrict_unprivileged_userns=0
kernel.unprivileged_userns_clone=1
user.max_user_namespaces=15000
```

**Shape correction to plan v2 §5.2:** when the target is Codex, `openspec init` writes its workflows to `.agents/skills/` as **skills**, not as `/opsx:*` slash commands — those are Claude-only. The runner therefore points Codex at `.agents/skills/openspec-apply-change/SKILL.md` in the prompt rather than invoking a command. R8's inline-prompt fallback was not needed.

`tools/run_branch.sh` implements plan v2 §5.2. It fails closed in two places: no quota reading means skip (S5 is still unresolved — there is no supported programmatic quota source, so `quota_remaining` is a single stub to wire one into), and no owner-approved change folder means abort.

## Vanilla HOI4 — installed, and what it changed

`v1.19.2.0` "Operation Postern", matching RoR's `supported_version="1.19.*"`. 20 GB on the server via steamcmd; a 139 MB text subset synced to the Mac at `$HOI4_VANILLA_ROOT`.

**DLC: complete.** The game script references 16 distinct `has_dlc` gates and all 16 have an installed DLC; the mod gates on 13, all present. All four integrated expansions (Together for Victory, Death or Dishonor, Waking the Tiger, Man the Guns) are in `integrated_dlc/`. Gaps in the `dlcNNN` numbering are cosmetic and music packs sold as separate Steam apps that never appear in a `has_dlc` gate.

Worth knowing: **DLC ships its script in the base install**, gated at runtime. The `dlc/*/` folders hold only `gfx/`, `interface/`, `music/`, `portraits/` and `sound/`. Reference checking would work with no DLC owned at all.

### Effect on T1

Indexing vanilla changed the result set enormously:

| Check | Without vanilla | With vanilla |
|---|---|---|
| `R007` focus icons | 690 | **14** |
| `R008` idea pictures | 1,685 | **76** |

Because the two modes differ so much, the baseline records `vanilla_indexed` and the lint warns loudly when a comparison mixes them. A baseline built in one mode and used in the other reports thousands of phantom regressions.

`R008` had to learn two engine behaviours before it was trustworthy — the verbatim sprite fallback and graphical-culture suffix variants. Without those it reported ~1,600 phantom findings. Both were discovered by checking vanilla's own content, not by reading documentation.

## Why the reference material lives outside the repo

`$ROR_REFS` (default `~/ror-refs`) holds the Paradox wiki snapshot, the vanilla HOI4 text subset and the hoi4skill binary.

- The wiki snapshot ships inside `klimPaskov/Agentic-HOI4-Modding`, which has **no licence file** — all rights reserved by default. It does not belong in a public fork.
- Vanilla game files are Paradox's.
- Fewer files in the repo means fewer upstream conflict sites (C7).

---

## T1 calibration

`tools/ror_lint.py` runs in ~5 s over 4,863 script files, 196 localisation files and 2,628 focuses.

First run against upstream produced 328 errors. **Three checks were wrong and were corrected, not suppressed:**

1. **Dead-node detection** compared options *within* one `prerequisite` block. That block is an OR, and options inside it being mutually exclusive is the ordinary "two branches converge here" pattern. It must compare *across* AND-ed blocks. The wrong version flagged ~160 healthy focuses.
2. **Colour-code validation** accepted only letters after `§`. Digits (`§1`) and signs (`§+`, `§-`) are valid. 15 false positives.
3. **Unary-minus detection** fired on `add = -num_armies` in `common/scorers/`, where the token is an engine scorer, not a script variable. The check now skips AI grammar.

After correction: **150 errors, all verified real** — 149 focuses with no localisation key, and one prerequisite deadlock. Both are upstream content problems, recorded in `known-upstream-defects.md` and frozen in `tools/upstream-baseline.json` (2,608 findings).

Branches gate on what they introduce:

```bash
tools/ror_lint.py --baseline tools/upstream-baseline.json
```

The gate was verified against deliberately planted defects — `>=`, a missing BOM, a non-Russian language header, a dangling prerequisite, missing localisation, an unreachable AND-group node, and a coordinate collision were all caught while all 2,608 inherited findings stayed suppressed.

**Refresh the baseline only after an upstream merge**, never to silence a branch's own findings.
