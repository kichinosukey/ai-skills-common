# skills.yaml schema

Each project repo has a root-level `skills.yaml` that lists the skills it consumes from `~/.ai-skills/<namespace>/`.

## Schema

```yaml
version: 1
targets:
  - dir: .agents/skills     # openclaw
  - dir: .codex/skills      # codex
  - dir: .claude/skills     # claude code
skills:
  - mentalbase/backoffice-daily-triage-review
  - mentalbase/_backoffice-cdp-login-bootstrap
  - _common/loglm-repo-insight-review
  - _common/session-slack-retro
```

## Resolution

`<namespace>/<skill>` resolves to `~/.ai-skills/<namespace>/<skill>` (override via `AI_SKILLS_HOME`). For every `targets[].dir` entry, `sync-skills` creates `<dir>/<skill>` as a symlink to the source directory. The namespace prefix is dropped from the link name.

Name collisions across namespaces are an error — resolve by renaming one skill.

## git ignore

- Track `skills.yaml`.
- Do **not** track `.agents/skills/`, `.codex/skills/`, `.claude/skills/` contents — they are generated symlinks. Typical `.gitignore`:
  ```
  .agents/skills/
  .codex/skills/
  .claude/skills/
  ```

## Repo-local skills (exception)

Skills that only make sense inside a single repo (e.g. `photo-search/parallel-perf-bottleneck-analyzer`) stay as **tracked real directories** under `.agents/skills/<skill>/` — they do not appear in `skills.yaml` and are not symlinks. Adjust `.gitignore` per-repo if you need to un-ignore specific repo-local skill dirs.

## CLI

```
sync-skills [--dry-run] [--prune] [--root <path>]
```

- Reads `<root>/skills.yaml` (default `$PWD`).
- Creates missing target dirs, symlinks every manifest skill, skips already-correct links.
- `--prune` removes symlinks under the target dirs that point into `~/.ai-skills` but are not in the manifest.
- Refuses to overwrite an existing real file/dir at the link path (manual cleanup required).
