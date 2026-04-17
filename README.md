# ai-skills-common

Shared, cross-project Codex / Claude Code / OpenClaw skills. Personal remote.

## Layout

```
ai-skills-common/
├── bin/sync-skills          # CLI that materializes symlinks from skills.yaml
├── docs/manifest.md         # skills.yaml schema
├── docs/bootstrap.md        # new-machine setup
├── <skill-name>/            # one dir per skill, each with SKILL.md
```

## Usage

This repo is cloned to `~/.ai-skills/ai-skills-common`. Project repos declare which skills they want via a root `skills.yaml` manifest, then run `sync-skills` to materialize symlinks under `.agents/skills/`, `.codex/skills/`, `.claude/skills/`.

See `docs/bootstrap.md` for initial setup on a new machine, and `docs/manifest.md` for the manifest schema.
