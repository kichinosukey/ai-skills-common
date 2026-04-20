# skills.yaml schema

Each project repo has a root-level `skills.yaml` that lists the skills it consumes from `~/.ai-skills/<namespace>/`.

## Schema

```yaml
version: 1
targets:
  - dir: .agents/skills     # openclaw
  - dir: .codex/skills      # codex
  - dir: .claude/skills     # claude code (skill entries)
  - dir: .claude/commands   # claude code (slash commands)
    format: command-wrapper
skills:
  - mentalbase/backoffice-daily-triage-review
  - mentalbase/_backoffice-cdp-login-bootstrap
  - _common/loglm-repo-insight-review
  - _common/session-slack-retro
```

## Target formats

Each target has a `format` (default `symlink`).

- `symlink` — `sync-skills` creates `<dir>/<skill>` as a symlink to the source skill directory. The namespace prefix is dropped from the link name.
- `command-wrapper` — `sync-skills` emits `<dir>/<skill>.md` wrapper files that invoke the skill via Claude Code's Skill tool. Enables `/<skill>` slash-command completion. Skills whose names start with `_` are treated as internal (callable only from other skills) and are **skipped** under this format.

Wrapper content:

```markdown
---
description: <description from SKILL.md frontmatter>
---

Use Skill `<skill-name>` with arguments: $ARGUMENTS
```

## Resolution

`<namespace>/<skill>` resolves to `~/.ai-skills/<namespace>/<skill>` (override via `AI_SKILLS_HOME`).

Name collisions across namespaces are an error — resolve by renaming one skill.

## git ignore

- Track `skills.yaml`.
- Do **not** track generated target contents (symlinks or command wrappers). Typical `.gitignore`:
  ```
  .agents/skills/
  .codex/skills/
  .claude/skills/
  .claude/commands/
  ```

## Repo-local skills (exception)

Skills that only make sense inside a single repo (e.g. `photo-search/parallel-perf-bottleneck-analyzer`) stay as **tracked real directories** under `.agents/skills/<skill>/` — they do not appear in `skills.yaml` and are not symlinks. Adjust `.gitignore` per-repo if you need to un-ignore specific repo-local skill dirs.

## CLI

```
sync-skills [--dry-run] [--prune] [--root <path>]
```

- Reads `<root>/skills.yaml` (default `$PWD`).
- Creates missing target dirs, symlinks every manifest skill, skips already-correct links.
- `--prune` removes stale artifacts under the target dirs:
  - `symlink` targets: symlinks into `~/.ai-skills` not in the manifest.
  - `command-wrapper` targets: `.md` files matching the wrapper sentinel (`Use Skill ` … ` with arguments: $ARGUMENTS`) not in the manifest.
- Refuses to overwrite an existing real file/dir at the link path (manual cleanup required).
