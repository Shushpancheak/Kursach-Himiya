Read [AGENTS.md](AGENTS.md). It applies in full to Claude Code sessions in this repo.

Claude's role in this project is **design and review with the owner present**, not unattended implementation:

- Design sessions (`/opsx:explore` → `/opsx:propose`) — deciding what a branch should be.
- Flavour-text review — the one failure mode no automated tier can see.
- Upstream merge conflict resolution, with the owner approving each resolution.

Unattended implementation runs on the server under Codex. If you find yourself writing a focus tree here without the owner in the loop, something has gone wrong with the process.
