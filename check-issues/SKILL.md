---
name: check-issues
description: GitHub issueの確認・整理。gh CLIでissue一覧を取得し、ステータス・ラベル・担当者で整理して表示する。「issue確認」「issue一覧」「issueチェック」「open issues」「残タスク確認」などのリクエストで起動。
---

# Check Issues

カレントリポジトリのGitHub issueを取得し、整理して表示する。

## Workflow

### 1. リポジトリ確認

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

失敗したら `gh auth login` が必要な旨を伝えて終了。

### 2. Issue取得

Open issueを取得（デフォルト上限30件）:

```bash
gh issue list --state open --json number,title,state,labels,assignees,createdAt,updatedAt,milestone --limit 100
```

ユーザーがclosedも見たい場合:

```bash
gh issue list --state all --json number,title,state,labels,assignees,createdAt,updatedAt,milestone --limit 100
```

### 3. 整理・表示

取得結果を以下の形式で整理して表示:

**ラベル別にグループ化**して、各issueを1行で表示:

```
## Open Issues (N件)

### bug (2件)
| # | Title | Assignee | Updated |
|---|-------|----------|---------|
| #12 | ログインエラー | @user | 2d ago |
| #8  | DB接続タイムアウト | — | 1w ago |

### enhancement (3件)
| # | Title | Assignee | Updated |
|---|-------|----------|---------|
| ...

### ラベルなし (1件)
| ...
```

- ラベルが複数あるissueは最初のラベルでグループ化
- 担当者なしは `—` で表示
- 更新日は相対表示（2d ago, 1w ago など）
- 件数サマリーを冒頭に表示

### 4. オプション対応

ユーザーの追加リクエストに応じて:

- **特定ラベルのみ**: `gh issue list --label "bug" ...`
- **特定担当者のみ**: `gh issue list --assignee "@me" ...`
- **マイルストーン別**: `--milestone "v1.0"` で絞り込み
- **検索**: `gh issue list --search "keyword" ...`
