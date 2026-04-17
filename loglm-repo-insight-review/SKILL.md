---
name: loglm-repo-insight-review
description: |
  loglm が保存した Codex 端末セッションログを clean text 化し、
  経営者にも分かる言葉でリポジトリ改善候補を抽出する skill。
  `logs/loglm-codex-log-*.txt` や明示されたログパスから、
  docs、tests、CLI、CDP/認証、state model、運用 runbook の改善点を見つけたいときに使う。
  プロジェクト横断で使える。
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# loglm Repo Insight Review

## Purpose

`loglm-codex-log-*.txt` はアプリ実行ログではなく、ANSI 制御文字と画面再描画を含む Codex 端末セッション録画である。ANSI 除去は公式の `loglm-decode` に任せ、この skill はデコード済みテキストの分類と改善候補抽出に専念する。

## Guardrails

- ログはローカルで処理し、Slack permalink、業務情報、認証導線を外部サービスに送らない。
- clean output と insight candidates は中間成果物であり、候補をそのまま事実扱いしない。
- `logs/` は未追跡の一時ログとして扱う。削除や `.gitignore` 更新はユーザーの依頼がある場合だけ行う。
- 大きな docs/code 更新に進む前に、その repo のローカル運用ルールや `AGENTS.md` 相当を確認し、複数観点で短くレビューする。

## Workflow

1. 対象ログを確認する。通常は `logs/` または `logs/loglm-codex-log-*.txt`。別ディレクトリが指定されたらそれを使う。
2. まず `loglm-decode` で ANSI を除去する（`loglm-decode logs/*.txt`）。`.decoded.txt` が生成される。
3. helper script でデコード済みテキストから summary と insight candidates を `/tmp` など repo 外または明示された出力先に作る。
4. `summary.md` でファイル数と raw/kept 行数を確認する。
4. `insight_candidates.md` を読み、候補を次の観点に分類する。
   - `ops_cdp_auth`: CDP、Chrome、LaunchAgent、認証、手動ログイン導線
   - `state_model`: `failed`, `not_found`, `review_needed`, `dry_run_ready`, terminal/non-terminal 判定
   - `docs_runbook`: README、runbook、service docs、TODO、明文化すべき手順
   - `tests_guardrails`: pytest、selector hardening、guardrail、RuntimeError、verification
   - `slack_voucher_flow`: Slack thread、UPSIDER、証憑 upload、settlement
   - `service_collectors`: AWS、ekinet、freee、amazon、openai、times_car、collector
   - `tooling_errors`: MCP startup、invalid_grant、ConnectError、timeout、warning
5. 最終出力では、まず社長にも分かる要約を書き、その後に技術者向け evidence を短く添える。
6. 実装に進む場合は、候補を `docs-only`, `test-only`, `CLI/healthcheck`, `state-model`, `ops automation` に分け、最小 diff から着手する。

## Executive Translation

`insight_candidates.md` は技術ログの索引なので、そのまま提示しない。まず「事業・運用上の意味」に翻訳する。

- `CDP`, `Chrome`, `LaunchAgent`, `認証`, `manual_login`: 「自動化が人間のログイン状態に依存しており、放置すると止まるリスク」
- `failed`, `not_found`, `review_needed`, `dry_run_ready`: 「処理結果の状態定義が曖昧だと、再実行すべきか人が見るべきか判断できないリスク」
- `pytest`, `guardrail`, `RuntimeError`, `selector`: 「実機で見つかった失敗をテストと安全停止条件に戻せているか」
- `runbook`, `README`, `docs/services`: 「属人手順を運用手順に落とせているか」
- `Slack upload`, `UPSIDER`, `settlement`: 「証憑回収の最終成果物が業務フローに戻っているか」
- `MCP`, `invalid_grant`, `invalid YAML`, `ConnectError`: 「開発/運用環境のノイズが本質的な失敗発見を邪魔していないか」

改善候補は、次の経営判断軸で説明する。

- Business Impact: 証憑回収漏れ、手作業、月次締め遅延、運用ノイズのどれを減らすか
- Root Cause: 技術用語を避け、なぜ繰り返し起きるのかを 1 文で説明する
- Proposal: 何を作る/直す/文書化するかを 1 文で説明する
- Effort: `S/M/L` で概算する
- Confidence: `High/Medium/Low` とし、根拠ログの量と現行 repo との照合有無で決める
- Decision Needed: 今やる、TODO に積む、保留、repo 外対応のどれかを書く

避けること:

- source path と error_code だけを並べて終わらせない。
- `CDP preflight` などの用語だけで提案しない。必ず「ログイン状態を事前確認して、定期実行が空振りする前に止める」のように翻訳する。
- evidence を長く貼りすぎない。Slack permalink や業務情報は必要最小限にする。

## Helper Script

まず `loglm-decode` で ANSI を除去してから、分類スクリプトを実行する。

```sh
# Step 1: デコード（公式ツール）
loglm-decode logs/*.txt

# Step 2: 分類と候補抽出（この skill のスクリプト）
python ~/.ai-skills/loglm-repo-insight-review/scripts/clean_loglm_logs.py \
  logs \
  --output-dir /tmp/loglm-clean \
  --combined-output /tmp/loglm-clean/combined.clean.txt \
  --summary-output /tmp/loglm-clean/summary.md \
  --insights-output /tmp/loglm-clean/insight_candidates.md
```

候補抽出に関係する行だけ見たい場合:

```sh
python ~/.ai-skills/loglm-repo-insight-review/scripts/clean_loglm_logs.py \
  logs \
  --semantic-only \
  --combined-output /tmp/loglm-clean/combined.semantic.txt \
  --insights-output /tmp/loglm-clean/insight_candidates.md
```

コンテキスト行が必要な場合は `--context 2` を明示する。

## Output Contract

回答は次の順に短くまとめる。最初の 3 セクションは非エンジニアにも読める表現にする。

1. 社長向け要約
2. 優先度順の改善提案
3. 今すぐ決めるべきこと
4. 技術者向け根拠
5. 低信頼/保留候補
6. 秘匿情報の扱い

各 candidate は次の形にする。

```markdown
### 1. 提案名
- Business Impact:
- Root Cause:
- Proposal:
- Effort:
- Confidence:
- Decision Needed:
- Evidence:
```

`Evidence` には source log path と短い evidence 要約だけを書く。技術詳細を厚くしたい場合は、最後の `技術者向け根拠` に分離する。
