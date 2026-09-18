"""Shared NewtonX ADK connection layer for CLI and web GUI."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

try:
    from newtonx_adk import ConfigManager, NewtonXClient
except ImportError:  # Optional for demo-only installs.
    ConfigManager = None
    NewtonXClient = None


@dataclass(frozen=True)
class ModelOption:
    name: str
    uid: str | None = None
    description: str | None = None


class NewtonXConnection:
    """Use the same ADK config and model discovery path as othello_py."""

    CHAT_URL = "https://seraku.newton-x.net/aichat/chat"

    def __init__(self) -> None:
        if ConfigManager is None or NewtonXClient is None:
            raise RuntimeError("NewtonX ADKがインストールされていません。wheelをインストールしてください。")
        self.config_manager = ConfigManager()

    def config(self) -> Any:
        return self.config_manager.get_config()

    def save_settings(self, *, pat: str | None = None, model: str | None = None, api_base_url: str | None = None) -> None:
        updates: dict[str, str] = {}
        if pat is not None:
            updates["personal_access_token"] = pat.strip()
        if model is not None:
            updates["default_assistant"] = model.strip() or None
        if api_base_url is not None:
            updates["api_base_url"] = api_base_url.strip()
        if updates:
            self.config_manager.update_config(**updates)

    def models(self) -> list[ModelOption]:
        client = NewtonXClient(self.config_manager)
        if not client.authenticate():
            raise RuntimeError("NewtonXの認証に失敗しました。PATを確認してください。")
        assistants = client.get_assistants()
        result: list[ModelOption] = []
        for item in assistants:
            name = str(item.get("name", "")).strip()
            if name:
                result.append(ModelOption(name=name, uid=item.get("uid") or item.get("uuid"), description=item.get("description")))
        return result

    def model_names(self) -> list[str]:
        return [item.name for item in self.models()]

    def status(self) -> dict[str, Any]:
        config = self.config()
        return {
            "configured": bool(str(getattr(config, "personal_access_token", "")).strip()),
            "default_model": getattr(config, "default_assistant", None),
            "api_base_url": getattr(config, "api_base_url", ""),
        }

    def client(self) -> Any:
        return NewtonXClient(self.config_manager)

    def account_info(self) -> dict[str, str]:
        """Fetch the authenticated NewtonX account for display in the desktop app."""
        client = self.client()
        if not client.authenticate():
            raise RuntimeError("NewtonXの認証に失敗しました。PATを確認してください。")
        payload = client.get_user_info() or {}
        if not isinstance(payload, dict):
            raise RuntimeError("NewtonXからアカウント情報を取得できませんでした。")
        departments = payload.get("departments") or []
        department_names = [
            str(item.get("name") or "").strip()
            for item in departments
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]
        return {
            "name": str(payload.get("displayName") or payload.get("name") or payload.get("userName") or payload.get("username") or "").strip(),
            "organization": str(payload.get("department") or payload.get("companyName") or payload.get("organization") or (department_names[0] if department_names else "") or payload.get("jobTitle") or "").strip(),
            "email": str(payload.get("mail") or payload.get("email") or " ").strip(),
        }

    def company_workspaces(self) -> list[dict[str, str]]:
        """Return real NewtonX folders; no placeholder knowledge is generated."""
        client = self.client()
        if not client.authenticate():
            raise RuntimeError("NewtonXの認証に失敗しました。PATを確認してください。")
        folders = client.get_folders()
        return [
            {
                "uid": str(item.get("uid") or item.get("id") or item.get("uuid") or ""),
                "name": str(item.get("name") or "").strip(),
            }
            for item in folders
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]

    def create_company_workspace(self, name: str) -> dict[str, str]:
        """Create a company folder through the NewtonX chat/folder API."""
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("企業名を入力してください。")
        client = self.client()
        if not client.authenticate():
            raise RuntimeError("NewtonXの認証に失敗しました。PATを確認してください。")
        uid = client.create_folder(clean_name)
        if not uid:
            raise RuntimeError("NewtonXに企業ワークスペースを作成できませんでした。")
        return {"uid": str(uid), "name": clean_name}
