from pathlib import Path
import json
import mimetypes
import sys
import os
import webbrowser
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

try:
    from newtonx_connection import NewtonXConnection
except ImportError:
    NewtonXConnection = None

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
HOST = "127.0.0.1"
PORT = 8000


def scenario_html(payload):
    purpose = escape(str(payload.get("purpose", "案件獲得")))
    return f'''<div class="output-title"><h3>商談シナリオ <span class="ai-badge">NewtonXADK生成</span></h3><button class="save-btn" data-save>↓ 履歴に保存</button></div><div class="scenario-columns"><div><p class="section-label">大枠シナリオ</p><div class="keyword-list"><span class="keyword">{purpose}</span><span class="keyword">課題の再定義</span><span class="keyword">来期計画</span><span class="keyword">次回提案</span></div><p class="section-label">今回のゴール</p><div class="goal-box">顧客の課題と意思決定プロセスを把握し、次回提案につながる合意を形成する。</div></div><div><p class="section-label">進行イメージ</p><div class="outline-item"><span class="outline-num">1</span><div><strong>現状確認</strong><p>前回からの変化と現在の課題を確認する。</p></div></div><div class="outline-item"><span class="outline-num">2</span><div><strong>課題と背景の深掘り</strong><p>優先度、制約条件、体制を質問で引き出す。</p></div></div><div class="outline-item"><span class="outline-num">3</span><div><strong>次回提案の合意</strong><p>提案内容、参加者、次回日程を決定する。</p></div></div><div class="talk-details"><p class="section-label">確認すべき質問例</p><p class="talk-summary">「成功をどのような指標で捉えていますか？」「最もボトルネックになっている工程はどこですか？」</p><div class="agenda"><span>目的・背景</span><span>体制・予算</span><span>スケジュール</span><span>意思決定者</span></div></div></div></div>'''


def ball_html(payload):
    return '''<div class="output-title"><h3>ボール管理レポート <span class="ai-badge blue-badge">NewtonXADK分析</span></h3><button class="save-btn" data-save>↓ 履歴に保存</button></div><div class="analysis-grid"><div class="metric"><small>商談フェーズ</small><strong>課題整理・提案前</strong></div><div class="metric"><small>ボール保有者</small><strong class="orange">顧客側（山田様）</strong></div><div class="metric"><small>案件確度</small><strong class="green">60%　↑</strong></div></div><div class="analysis-columns"><div class="analysis-block"><h4>顧客課題・未確認事項</h4><ul class="check-list"><li>既存システムの運用コストが増加</li><li>来期予算と意思決定スケジュール</li><li>移行後の運用体制・内製化方針</li></ul><h4 style="margin-top:22px">注意すべきリスク</h4><ul class="check-list risk"><li>競合ベンダーも同時に比較中</li><li>決裁者との接点がまだない</li></ul></div><div class="analysis-block"><h4>推奨する次回アクション</h4><ul class="check-list"><li>刷新ロードマップの叩き台を送付</li><li>決裁者を含む次回提案会を打診</li></ul><h4 style="margin-top:22px">推奨商材・関連資料</h4><div class="product-card"><div class="product-icon">◈</div><div><strong>Azure移行アセスメントサービス</strong><small>サービス紹介資料 ・ 導入事例 2件</small></div></div><div class="product-card"><div class="product-icon">▤</div><div><strong>基幹システム刷新 提案テンプレート</strong><small>提案書 ・ 価格表</small></div></div></div></div>'''


class AppHandler(BaseHTTPRequestHandler):
    def send_json(self, body, status=HTTPStatus.OK):
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_POST(self):
        route = urlparse(self.path).path
        if route == "/api/settings":
            try:
                size = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(size) or b"{}")
                if not isinstance(payload, dict):
                    raise ValueError("JSON object is required")
                if NewtonXConnection is None:
                    raise RuntimeError("NewtonX ADKが利用できません")
                connection = NewtonXConnection()
                connection.save_settings(pat=payload.get("pat"), model=payload.get("model"), api_base_url=payload.get("api_base_url"))
                self.send_json(connection.status())
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json({"error": f"Invalid JSON: {exc}"}, HTTPStatus.BAD_REQUEST)
            except (RuntimeError, OSError) as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.SERVICE_UNAVAILABLE)
            return
        if route not in ("/api/newtonxadk/scenario", "/api/newtonxadk/ball"):
            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size) or b"{}")
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json({"error": f"Invalid JSON: {exc}"}, HTTPStatus.BAD_REQUEST)
            return
        html = scenario_html(payload) if route.endswith("scenario") else ball_html(payload)
        self.send_json({"html": html, "model": payload.get("model", "newtonxadk-default")})

    def do_GET(self):
        requested = urlparse(self.path).path
        if requested == "/healthz":
            self.send_json({"status": "ok", "service": "newtonx-sales-copilot"})
            return
        if requested == "/api/settings/status":
            try:
                if NewtonXConnection is None:
                    raise RuntimeError("NewtonX ADKが利用できません")
                self.send_json(NewtonXConnection().status())
            except RuntimeError as exc:
                self.send_json({"configured": False, "adk_available": False, "error": str(exc)}, HTTPStatus.SERVICE_UNAVAILABLE)
            return
        if requested == "/api/settings/models":
            try:
                if NewtonXConnection is None:
                    raise RuntimeError("NewtonX ADKが利用できません")
                models = NewtonXConnection().models()
                self.send_json({"models": [{"name": item.name, "uid": item.uid, "description": item.description} for item in models]})
            except RuntimeError as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.SERVICE_UNAVAILABLE)
            return
        relative = "index.html" if requested in ("", "/") else requested.lstrip("/")
        target = (ROOT / relative).resolve()
        if ROOT not in target.parents and target != ROOT:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        print(f"[NewtonXADK] {format % args}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", str(PORT)))
    server = ThreadingHTTPServer((HOST, port), AppHandler)
    url = f"http://{HOST}:{port}"
    print(f"NewtonX Sales Copilot: {url}")
    if os.getenv("NEWTONX_NO_BROWSER") != "1":
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
