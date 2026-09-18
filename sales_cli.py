"""CLI for NewtonX Sales Copilot connection management."""
from __future__ import annotations

import argparse
import getpass
import json

from newtonx_connection import NewtonXConnection


def main() -> int:
    parser = argparse.ArgumentParser(description="NewtonX Sales Copilot CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Show connection status")
    sub.add_parser("models", help="Fetch available NewtonX assistants")
    configure = sub.add_parser("configure", help="Update shared NewtonX ADK settings")
    configure.add_argument("--pat", help="Personal Access Token; omit to prompt securely")
    configure.add_argument("--model", help="Default assistant/model name")
    configure.add_argument("--api-base-url", help="NewtonX API base URL")
    args = parser.parse_args()

    if args.command == "status":
        print(json.dumps(NewtonXConnection().status(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "configure":
        pat = args.pat if args.pat is not None else getpass.getpass("NewtonX PAT (empty clears): ")
        NewtonXConnection().save_settings(pat=pat, model=args.model, api_base_url=args.api_base_url)
        print("NewtonX接続設定を保存しました。")
        return 0
    models = NewtonXConnection().models()
    if not models:
        print("利用可能なモデルがありません。")
        return 1
    for item in models:
        print(item.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
