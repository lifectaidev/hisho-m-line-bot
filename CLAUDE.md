# 秘書M（hisho-m-line-bot）— プロジェクトルール

## このプロジェクトについて
昇悟さん専用AIエージェント「秘書M」のLINE bot実装。
FastAPI + Claude API + LINE Messaging APIで構成。
コンセプト：「言わなくても動く参謀」

## 絶対に守ること
- mainブランチへの直接pushは禁止
- Issueを作らずに作業を始めない
- Issueに書かれていない作業を勝手に広げない
- .envやAPIキーをcommitしない
- 動作確認せずにPRを出さない
- よくわからないまま `git reset --hard` や `git push --force` を使わない
- ルール逸脱しそうな場合は必ずストップをかける

## 開発の流れ
Issue作成 → ブランチ作成 → 作業 → Push → PR → マージ

## ブランチ名ルール
| 種別 | 用途 | 例 |
|---|---|---|
| feature/ | 新機能追加 | feature/1-line-webhook |
| fix/ | バグ修正 | fix/3-webhook-error |
| docs/ | ドキュメント修正 | docs/2-update-readme |
| refactor/ | 挙動を変えない整理 | refactor/4-main-cleanup |

## 作業開始前チェック
1. 対応するIssueがGitHubに存在するか確認する
2. Issue番号を控える（例: #1）
3. mainを最新にしてからブランチを切る

```bash
git checkout main
git pull origin main
git checkout -b feature/Issue番号-作業名
source venv/bin/activate
```

## 開発中の動作確認コマンド
```bash
source venv/bin/activate
uvicorn main:app --reload
```
ブラウザで http://127.0.0.1:8000 を開く。

## PR作成前チェック
- [ ] 不要なファイル（.DS_Store, .env, venv/）が入っていない
- [ ] 対応するIssueがある
- [ ] PRに `Closes #番号` を書いた
- [ ] ローカルで動作確認した
- [ ] 変更内容を自分の言葉で説明できる

## PRの書き方テンプレート
Closes #番号
変更内容

（何をしたか）

動作確認

uvicorn main:app --reload で起動
（確認した内容）

相談事項

（あれば）


## 技術スタック
| 領域 | 技術 |
|---|---|
| バックエンド | Python 3.11+ / FastAPI |
| AI | Claude API（claude-sonnet-4-6） |
| メッセージング | LINE Messaging API |
| メール | Gmail API |
| カレンダー | Google Calendar API |
| DB | Supabase |
| デプロイ | Railway |
| 定期実行 | APScheduler |

## 参照ドキュメント
- GitHub運用ルール → `docs/github-workflow.md`
- 要件定義書 → `docs/requirements.md`

## 理解の原則
- 実装したコードの役割を昇悟さんが自分の言葉で説明できることを確認してから次に進む
- 文法の暗記は不要。そのコードがアプリ全体の中で何の役割を持っているかを説明できること
- わからない専門用語が出たら都度説明する
- 理解確認が必要な場面ではClaudeが答えを言うのではなく昇悟さんに説明させる
- 昇悟さんが自分の言葉で説明できた場合のみ次に進む

## Claudeへの指示
- なぜその作業をするのか、必ず理由を説明してから進める
- コードを書いた後は必ず「このコードがアプリ全体で何の役割を持つか」を昇悟さんが自分の言葉で説明できるまで解説する
- 昇悟さんが理解できていない場合は次のステップに進まない
- ルール逸脱しそうな場合は必ずストップをかける

## 新しいチャットを開始するときの引き継ぎ方法
必ず以下を最初に伝えること。
- 今取り組んでいるIssue番号
- 作業のどのステップまで完了しているか
- 現在のブランチ名

例：
「Issue #1の作業中です。
ブランチ：feature/1-line-webhook
LINE Webhookの実装まで完了しています。
次の作業を一緒に進めてください。」

## PR作成前の必須確認（順番通りに実施）
PR作成ボタンを押す前に必ず以下を順番に確認すること。

1. Issueの完了条件を一つずつチェック
2. Issueの確認方法に沿って動作確認
3. PR作成前チェックリストを全てチェック
4. 上記が全て完了してからPR作成ボタンを押す

この確認を怠った場合はClaudeが必ずストップをかける。

## 困ったときに共有する情報
```bash
git status
git branch
git log --oneline -5
```
エラーが出た場合はエラーメッセージ全文と「何をしようとしたか」を一緒に共有する。