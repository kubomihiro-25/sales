"""Production WSGI entrypoint for NewtonX Sales Copilot."""
from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from app import ball_html, scenario_html
from newtonx_connection import NewtonXConnection

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_REQUEST_BYTES", "1048576"))


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; script-src 'self'; connect-src 'self' https:")
    return response


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "service": "newtonx-sales-copilot"})


@app.get("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.get("/api/settings/status")
def settings_status():
    try:
        return jsonify(NewtonXConnection().status())
    except RuntimeError as error:
        return jsonify({"configured": False, "adk_available": False, "error": str(error)}), 503


@app.get("/api/settings/models")
def settings_models():
    try:
        models = NewtonXConnection().models()
        return jsonify({"models": [{"name": item.name, "uid": item.uid, "description": item.description} for item in models]})
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503


@app.post("/api/settings")
def update_settings():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400
    try:
        connection = NewtonXConnection()
        connection.save_settings(
            pat=payload.get("pat") if "pat" in payload else None,
            model=payload.get("model") if "model" in payload else None,
            api_base_url=payload.get("api_base_url") if "api_base_url" in payload else None,
        )
        return jsonify(connection.status())
    except (RuntimeError, ValueError) as error:
        return jsonify({"error": str(error)}), 503


@app.post("/api/newtonxadk/<kind>")
def newtonxadk(kind):
    if kind not in {"scenario", "ball"}:
        return jsonify({"error": "Not found"}), 404
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400
    html = scenario_html(payload) if kind == "scenario" else ball_html(payload)
    return jsonify({"html": html, "model": payload.get("model", "newtonxadk-default")})


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({"error": "Request body is too large"}), 413


@app.errorhandler(500)
def internal_error(_error):
    app.logger.exception("Unhandled application error")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
