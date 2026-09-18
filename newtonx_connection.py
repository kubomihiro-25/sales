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
