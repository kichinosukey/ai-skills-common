# ai-skills-common

Shared, cross-project Codex / Claude Code / OpenClaw skills. Personal remote.

## Layout

```
ai-skills-common/
├── bin/sync-skills          # CLI that materializes skill artifacts from skills.yaml
├── docs/manifest.md         # skills.yaml schema
├── docs/bootstrap.md        # new-machine setup
├── <skill-name>/            # one dir per skill, each with SKILL.md
```

## Usage

This repo is cloned to `~/.ai-skills/ai-skills-common`. Project repos declare which skills they want via a root `skills.yaml` manifest, then run `sync-skills` to materialize skill artifacts under target directories (e.g. `.agents/skills/`, `.codex/skills/`, `.claude/skills/`).

See `docs/bootstrap.md` for initial setup on a new machine, and `docs/manifest.md` for the manifest schema.

## ターゲット形式

`targets[]` の各エントリは `format` を持つ（デフォルト `symlink`）。

- `symlink` — 各 skill を `<dir>/<skill>` として元ディレクトリへ symlink 展開。Codex / Claude Code / OpenClaw の skill ディレクトリ向け。
- `command-wrapper` — `<dir>/<skill>.md` の wrapper ファイルを生成し、Claude Code の Skill ツール経由で skill を呼び出す。Claude Code で **スラッシュ補完** (`/<skill>`) 有効化。`_` プレフィックス skill は internal 扱いで生成対象外。

例 — Claude Code スラッシュ補完対応:

```yaml
targets:
  - dir: .claude/skills              # skill 実体 (symlink)
  - dir: .claude/commands            # slash commands (wrapper)
    format: command-wrapper
skills:
  - mentalbase/backoffice-daily-triage-review
  - mentalbase/_backoffice-cdp-login-bootstrap   # internal, wrapper生成されない
```

`sync-skills` 実行後、Claude Code で `/backoffice-` と入力すると `/backoffice-daily-triage-review` が補完候補表示され、選択で Skill ツール起動。

スキーマ全体と format 別 `--prune` 挙動は `docs/manifest.md` 参照。
