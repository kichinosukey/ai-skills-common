---
name: local-skill-to-ai-skills
description: |
  repo ローカルの skill を `~/.ai-skills` 配下の共有 skill に昇格し、
  Codex と Claude から再利用できるようにするための移設 skill。
  `.codex/skills/<name>` や `.agents/skills/<name>` にある既存 skill を
  `~/.ai-skills/<name>` へ移し、必要な symlink と最小限の参照整理を行いたいときに使う。
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Local Skill To AI Skills

## Purpose

`~/.ai-skills` を共有 skill の正本とし、repo ローカル skill の重複管理をやめる。
移設後は少なくとも次を満たす。

- 正本は `~/.ai-skills/<skill-name>`
- Codex は `~/.codex/skills/<skill-name>` から見える
- Claude は `~/.claude/skills/<skill-name>` から見える
- repo 側に残すものは最小限にする

## When To Use

- repo 内だけに置いていた skill を他 repo からも使いたい
- Claude と Codex の両方から同じ skill を触りたい
- `.codex/skills` と `~/.ai-skills` の二重管理をやめたい
- 既存 skill を共有化したいが、手順確認を毎回やりたくない

## Inputs

最低限、次を確定する。

- skill 名
- 現在の正本ディレクトリ
- 共有先を `~/.ai-skills/<skill-name>` にするか
- repo 側を削除するか、bridge を残すか

明示指定がなければ、repo 側の正本は削除し、共有先を唯一の正本とする。

## Workflow

1. 現在の skill 実体を確認する。
   - 優先順は `.codex/skills/<name>`、`.agents/skills/<name>`、その他ユーザー指定パス
   - `SKILL.md`、`agents/`、`scripts/`、`references/`、`assets/` の有無を確認する
2. `SKILL.md` の frontmatter を確認し、`name` が移設対象と一致することを確かめる。
3. 共有先 `~/.ai-skills/<name>` が未作成なら作る。既存なら差分を読んで、上書きが安全か確認する。
4. skill 一式を `~/.ai-skills/<name>` へ移す。
   - `SKILL.md`
   - `agents/openai.yaml` があればそれも移す
   - bundled resources があれば構造を保ったまま移す
5. 共有リンクを揃える。
   - `~/.codex/skills/<name> -> ~/.ai-skills/<name>`
   - `~/.claude/skills/<name> -> ~/.ai-skills/<name>`
6. repo 側を整理する。
   - 既定では repo ローカル正本は削除する
   - repo に名前だけ残したい明確な理由がある場合だけ、薄い bridge を残す
   - local 環境依存の絶対パスを repo docs に増やしすぎない
7. 参照を最小限だけ更新する。
   - docs は skill 名ベースの参照を優先する
   - path を書く必要がある場合だけ、shared canonical が `~/.ai-skills/<name>` であることを明記する
8. 検証する。
   - `ls -l ~/.ai-skills/<name>`
   - `ls -l ~/.codex/skills/<name>`
   - `ls -l ~/.claude/skills/<name>`
   - 必要なら repo 内の `rg` で古い canonical path を確認する

## Guardrails

- repo に machine-local absolute path を正本として commit しない
- shared canonical と repo copy を両方正本扱いにしない
- bridge を残す場合も、実体編集先は 1 か所だけにする
- 既存 shared skill があるときは、先に差分を確認してから上書きする
- 削除を伴う場合は、shared 側が完全に揃ってから repo 側を消す

## Output Contract

回答では次を短く示す。

1. 共有化した skill 名
2. 新しい canonical path
3. Codex と Claude の参照 path
4. repo 側に何を残したか、または消したか
5. 未解決の差分や follow-up
