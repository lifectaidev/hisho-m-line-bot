# GitHub運用ルール

このプロジェクトは、安全に開発できるように、
必ずIssueとPull Request（PR）ベースで進めます。

## 基本ルール
- mainブランチへ直接pushしない
- 作業前に必ずIssueを作成する
- Issueに書かれていない作業を勝手に広げない
- 作業ごとにブランチを作る
- 変更は小さく分ける
- PRには対応するIssueを必ず紐付ける
- PRを作ってから内容を確認する
- 動作確認せずにPRを出さない
- .envやAPIキーをcommitしない

## Issue作成
作業を始める前に、必ずIssueを作成します。

Issueに書くこと：
- 何をしたいか
- なぜ必要か
- 完了条件
- 確認方法
- 不明点や相談したいこと

Issueの例：
やりたいこと
LINEでメッセージを送るとClaudeが返答する状態にする。
なぜ必要か
秘書Mの全機能の入口になるため。
これが動いて初めてGmail・Calendar・タスクの操作が可能になる。
完了条件

LINEでメッセージを送ると返答が返ってくる
Railwayにデプロイされている

確認方法

LINEで「テスト」と送って返答が返ってくることを確認

相談事項

なし


## ブランチ名ルール
| 種別 | 用途 | 例 |
|---|---|---|
| feature/ | 新機能追加 | feature/1-line-webhook |
| fix/ | バグ修正 | fix/3-webhook-error |
| docs/ | ドキュメント修正 | docs/2-update-readme |
| refactor/ | 挙動を変えない整理 | refactor/4-main-cleanup |

## 作業開始の流れ
```bash
git checkout main
git pull origin main
git checkout -b feature/Issue番号-作業名
source venv/bin/activate
```

作業前に必ずIssueを作成し、最新のmainを取り込みます。

## コミット
コミットは「何をしたか」がわかる単位で作ります。

よい例：
```bash
git add main.py
git commit -m "LINE WebhookでClaudeの返答を返す処理を追加"
```

避ける例：
```bash
git commit -m "修正"
git commit -m "いろいろ変更"
git commit -m "途中"
```

## PR作成前チェック

 不要なファイル（.DS_Store, .env, venv/）が入っていない
 対応するIssueがある
 PRに「Closes #番号」を書いた
 ローカルで動作確認した
 変更内容を自分の言葉で説明できる


## PRの書き方
Closes #番号
変更内容

（何をしたか）

動作確認

uvicorn main:app --reload で起動
（確認した内容）

相談事項

（あれば）


## マージ後
```bash
git checkout main
git pull origin main
git branch -d ブランチ名
```

## やってはいけないこと
- mainへ直接pushする
- Issueを作らずに作業を始める
- .envやAPIキーをcommitする
- よくわからないまま `git reset --hard` や `git push --force` を使う
- 動作確認せずにPRを出す

## 困ったとき
以下を共有して相談します。
```bash
git status
git branch
git log --oneline -5
```
エラーが出ている場合は、エラーメッセージ全文と
「何をしようとしたか」を一緒に共有してください。