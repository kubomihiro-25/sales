# NewtonX Sales Copilot

IT営業商談アシスタント。配布用のWindowsネイティブデスクトップアプリと、サーバー運用向けのFlask/Gunicorn構成を提供します。

## Windowsデスクトップアプリ

`build_exe.ps1`で、Webブラウザーを使わないTkinterネイティブGUIをビルドできます。画面はWeb版と同じ配色・カード・タブ構成で、商談ナレッジを左側、商談シナリオ生成AIとボール管理AIを右側に配置しています。

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1 -OutputDirectory .\NewtonXSalesCopilot
.\NewtonXSalesCopilot\NewtonXSalesCopilot.exe
```

配布先にPythonは不要です。起動後、「接続設定」から利用者ごとのPATとNewtonXモデルを設定してください。

## ローカル

```powershell
py -m pip install -r requirements.txt
py server.py
```

- UI: http://127.0.0.1:8000/
- Health: http://127.0.0.1:8000/healthz

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

本番では `compose.production.yaml` の `image` を公開済みイメージへ変更し、`.env` はGitにコミットしないでください。PATやNewtonXADKの秘密情報はSecret Managerまたは環境変数で管理します。

## GUI設定

画面右上の「接続設定」からAPI URL、PAT、AIモデルを変更できます。PATはブラウザのlocalStorageに保存され、`Authorization: Bearer <PAT>`で送信されます。共有端末・本番の高いセキュリティ要件では、サーバー側の認証プロキシとSecret Managerを利用してください。

## API

- `GET /healthz`
- `POST /api/newtonxadk/scenario`
- `POST /api/newtonxadk/ball`

本番WSGI起動:

```powershell
gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 4 --timeout 60 server:app
```

## NewtonX ADK接続の共通設計

CLIとGUIは、`newtonx_connection.py`を共通の接続層として利用します。`othello_py`と同じNewtonX ADKの`ConfigManager`を使うため、PAT・API URL・既定モデルは同じ `~/.newtonx/config.json` に保存されます。

### CLI

```powershell
# 接続状態（PATそのものは表示しません）
py sales_cli.py status

# PATを安全に入力して保存。空入力でPATを削除
py sales_cli.py configure --model "NewtonXのアシスタント名"

# NewtonXから利用可能なアシスタント一覧を取得
py sales_cli.py models
```

`models`はNewtonX ADKの`NewtonXClient.authenticate()`と`get_assistants()`を使用します。GUIの「NewtonXからモデル一覧を取得」も同じ処理をサーバー経由で呼び出します。

### GUI

GUIの接続設定でPAT、APIベースURL、既定モデルを保存できます。PATはブラウザのlocalStorageには保存せず、SalesサーバーからADKの`ConfigManager`へ保存します。ブラウザはSalesサーバーの同一オリジンAPIだけを呼び出すため、PATが外部NewtonX APIへ直接送られることはありません。

本番環境ではSalesサーバーをHTTPS化し、`.newtonx/config.json`を実行ユーザー専用の安全なストレージまたはSecret Managerへ移してください。

### ADKのインストール

NewtonX ADKが社内wheelで配布される場合は、デプロイ環境で次を実行します。

```powershell
py -m pip install "C:\path\to\newtonx_adk-0.10.5-py3-none-any.whl"
```

未インストールの場合、画面はデモ結果を表示しますが、モデル一覧取得・PAT接続は503になります。
