# telemetry/

`error-baseline.txt` — T4's baseline: the normalised `error.log` from booting
**vanilla with all 36 DLC active and no mod**.

It is empty, and that is correct. Vanilla is clean under those conditions, so
every line a candidate run produces is attributable to the mod. Do not "fix"
the emptiness by baselining a mod run — that would hide exactly what T4 exists
to find.

Regenerate on the server after a HOI4 update:

    tools/t4_boot.sh --baseline

`runs/` holds per-run logs and is gitignored.
