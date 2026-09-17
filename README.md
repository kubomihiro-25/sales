# NewtonX Sales Copilot

NewtonXADK と連携する IT 営業商談アシスタントの Python アプリです。Python 標準ライブラリだけで動作し、API が未接続の状態でもデモ結果を表示できます。

## 起動

```powershell
python app.py
```

ブラウザで http://127.0.0.1:8000 を開いてください。

## NewtonXADK API 契約

Python アプリは次のエンドポイントを提供します。

- `POST /api/newtonxadk/scenario`
  - `{ "purpose": string, "status": string, "context": string }`
- `POST /api/newtonxadk/ball`
  - `{ "transcript": string }`

レスポンスは `{ "html": string }` です。NewtonXADK の実装に差し替える場合は、`app.py` の `scenario_html` / `ball_html` で受信データをプロンプト処理へ渡し、同じレスポンス形式を返してください。
