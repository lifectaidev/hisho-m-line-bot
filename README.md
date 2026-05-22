# hisho-m-line-bot

秘書M — 昇悟さん専用AIエージェントのLINE bot

## 概要
LINEで話しかけると、Claudeが返答する。
Phase 1では以下の機能を実装しました。

- LINEでClaudeと会話
- Gmailの未読整理・要約
- Googleカレンダーの確認・登録
- タスク管理・優先順位付け
- 毎朝7時の自動ブリーフィング

## 技術スタック
| 領域 | 技術 |
|---|---|
| バックエンド | Python 3.11+ / FastAPI |
| AI | Claude API（claude-sonnet-4-6） |
| メッセージング | LINE Messaging API |
| DB | Supabase |
| デプロイ | Railway |

## セットアップ
```bash
git clone https://github.com/lifectai/hisho-m-line-bot.git
cd hisho-m-line-bot
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env.example .env
# .envを編集してAPIキーを設定
uvicorn main:app --reload
```

## 環境変数
`.env.example`を参照。

## ドキュメント
- GitHub運用ルール → `docs/github-workflow.md`
- 要件定義書 → `docs/requirements.md`

## 開発者

石破昇悟 / Lifect

- GitHub: https://github.com/lifectai
- Qiita: https://qiita.com/Lifect
- 開発記事: https://qiita.com/Lifect/items/a78081bd585bd6f2142f

## Phase 1 完成記事

詳しい設計・実装・失敗談はこちら：

[「言わなくても動く参謀」を目指して。自分専用AIエージェント「秘書M」をゼロから作った話（Phase 1: MVP編）](https://qiita.com/Lifect/items/a78081bd585bd6f2142f)