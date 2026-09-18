from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from newtonx_connection import NewtonXConnection


class SalesCopilotDesktop(tk.Tk):
    """Native Windows desktop application for the sales copilot."""

    def __init__(self) -> None:
        super().__init__()
        self.title("NewtonX Sales Copilot")
        self.geometry("1280x820")
        self.minsize(1050, 700)
        self.connection: NewtonXConnection | None = None
        self.models: list[str] = []
        self._build_style()
        self._build_ui()
        self._load_status()

    def _build_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Yu Gothic UI", 20, "bold"))
        style.configure("Heading.TLabel", font=("Yu Gothic UI", 13, "bold"))
        style.configure("Primary.TButton", font=("Yu Gothic UI", 10, "bold"))

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(20, 16))
        header.pack(fill="x")
        ttk.Label(header, text="NewtonX Sales Copilot", style="Title.TLabel").pack(side="left")
        self.status_label = ttk.Label(header, text="接続状態を確認中...")
        self.status_label.pack(side="left", padx=20)
        ttk.Button(header, text="接続設定", command=self._open_settings).pack(side="right")

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        knowledge = ttk.LabelFrame(body, text="商談ナレッジ", padding=10)
        body.add(knowledge, weight=1)
        self.tree = ttk.Treeview(knowledge, show="tree")
        self.tree.pack(fill="both", expand=True)
        self._populate_tree()

        right = ttk.Frame(body, padding=(14, 0, 0, 0))
        body.add(right, weight=3)
        tabs = ttk.Notebook(right)
        tabs.pack(fill="both", expand=True)
        self.scenario_tab = ttk.Frame(tabs, padding=14)
        self.ball_tab = ttk.Frame(tabs, padding=14)
        tabs.add(self.scenario_tab, text="商談シナリオ生成AI")
        tabs.add(self.ball_tab, text="ボール管理AI")
        self._build_scenario_tab()
        self._build_ball_tab()

    def _populate_tree(self) -> None:
        for company, person, role, deals in [
            ("株式会社アトラス", "山田 太郎", "情報システム部 部長", ["基幹システム刷新", "定例フォロー 06/12"]),
            ("ネクストソリューションズ", "佐藤 花子", "DX推進室", ["AI活用支援"]),
            ("グローバルテック", "鈴木 一郎", "開発部", ["人材提案"]),
        ]:
            company_id = self.tree.insert("", "end", text=company, open=True)
            person_id = self.tree.insert(company_id, "end", text=person, open=True)
            role_id = self.tree.insert(person_id, "end", text=role, open=True)
            for deal in deals:
                self.tree.insert(role_id, "end", text=deal)

    def _build_scenario_tab(self) -> None:
        ttk.Label(self.scenario_tab, text="商談前準備", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(self.scenario_tab, text="顧客情報・目的・商談状況を入力してシナリオを作成します。").pack(anchor="w", pady=(3, 12))
        form = ttk.Frame(self.scenario_tab)
        form.pack(fill="x")
        ttk.Label(form, text="商談目的").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        self.purpose = ttk.Combobox(form, values=["案件獲得", "要件確認", "人材提案", "単価交渉", "関係構築", "定例フォロー", "トラブルフォロー", "信頼回復", "ビジョン共有", "顧客課題整理", "取引拡大"], state="readonly")
        self.purpose.set("案件獲得")
        self.purpose.grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(form, text="商談状況").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.scenario_status = ttk.Entry(form)
        self.scenario_status.insert(0, "初回ヒアリング後・提案準備中")
        self.scenario_status.grid(row=1, column=1, sticky="ew", pady=4)
        form.columnconfigure(1, weight=1)
        ttk.Label(self.scenario_tab, text="顧客情報・補足").pack(anchor="w", pady=(12, 3))
        self.scenario_input = tk.Text(self.scenario_tab, height=6, wrap="word")
        self.scenario_input.pack(fill="x")
        ttk.Button(self.scenario_tab, text="商談シナリオを生成", style="Primary.TButton", command=self._generate_scenario).pack(anchor="e", pady=10)
        self.scenario_output = self._output(self.scenario_tab)

    def _build_ball_tab(self) -> None:
        ttk.Label(self.ball_tab, text="商談後の振り返り", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(self.ball_tab, text="議事録・商談メモ・文字起こしから次のアクションを整理します。").pack(anchor="w", pady=(3, 12))
        self.meeting_input = tk.Text(self.ball_tab, height=10, wrap="word")
        self.meeting_input.pack(fill="x")
        ttk.Button(self.ball_tab, text="商談を分析", style="Primary.TButton", command=self._analyze_meeting).pack(anchor="e", pady=10)
        self.ball_output = self._output(self.ball_tab)

    def _output(self, parent: ttk.Frame) -> tk.Text:
        output = tk.Text(parent, height=18, wrap="word", state="disabled", background="#f8fafc")
        output.pack(fill="both", expand=True)
        return output

    def _set_output(self, widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _run_background(self, task: Callable[[], str], output: tk.Text) -> None:
        self._set_output(output, "NewtonXで処理中です...")
        def worker() -> None:
            try:
                result = task()
            except Exception as error:
                result = f"エラー: {error}"
            self.after(0, lambda: self._set_output(output, result))
        threading.Thread(target=worker, daemon=True).start()

    def _ask_newtonx(self, prompt: str, title: str) -> str:
        connection = self.connection or NewtonXConnection()
        status = connection.status()
        if not status["configured"]:
            return "NewtonX未接続のためデモ結果を表示します。\n\n" + prompt
        client = connection.client()
        if not client.authenticate():
            raise RuntimeError("NewtonXの認証に失敗しました。接続設定を確認してください。")
        assistants = client.get_assistants()
        selected = next((item for item in assistants if item.get("name") == status.get("default_model")), None) or (assistants[0] if assistants else None)
        if not selected:
            raise RuntimeError("利用可能なNewtonXモデルがありません。")
        chat_uid = client.create_chat(assistant_uid=selected.get("uid") or selected.get("uuid"), title=title)
        if not chat_uid:
            raise RuntimeError("NewtonXチャットを作成できませんでした。")
        return client.send_message(chat_uid, prompt, web_search=False, knowledge_search=False) or "NewtonXから回答がありませんでした。"

    def _generate_scenario(self) -> None:
        prompt = f"IT営業の商談シナリオを作成してください。目的: {self.purpose.get()}、状況: {self.scenario_status.get()}、顧客情報: {self.scenario_input.get('1.0', 'end').strip()}。目的、ゴール、確認事項、質問例、着地点、アジェンダの順で日本語で整理してください。"
        self._run_background(lambda: self._ask_newtonx(prompt, "営業商談シナリオ"), self.scenario_output)

    def _analyze_meeting(self) -> None:
        prompt = f"IT営業の商談を分析してください。議事録: {self.meeting_input.get('1.0', 'end').strip()}。フェーズ、ボール保有者、未確認事項、リスク、次アクション、顧客課題、推奨商材、次回提案候補、関連資料を日本語で整理してください。"
        self._run_background(lambda: self._ask_newtonx(prompt, "商談分析"), self.ball_output)

    def _load_status(self) -> None:
        try:
            self.connection = NewtonXConnection()
            status = self.connection.status()
            self.status_label.configure(text=f"接続済み: {status.get('default_model')}" if status["configured"] else "PAT未設定")
        except Exception as error:
            self.status_label.configure(text=f"ADK未接続: {error}")

    def _open_settings(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("NewtonX接続設定")
        dialog.geometry("560x330")
        dialog.transient(self)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="APIベースURL").pack(anchor="w")
        url = ttk.Entry(frame)
        url.pack(fill="x", pady=(2, 10))
        ttk.Label(frame, text="アクセストークン（PAT）").pack(anchor="w")
        pat = ttk.Entry(frame, show="*")
        pat.pack(fill="x", pady=(2, 10))
        ttk.Label(frame, text="AIモデル").pack(anchor="w")
        model = ttk.Combobox(frame, state="readonly")
        model.pack(fill="x", pady=(2, 8))
        try:
            current = self.connection or NewtonXConnection()
            status = current.status()
            url.insert(0, status.get("api_base_url") or "https://seraku.newton-x.net/api")
            model.set(status.get("default_model") or "")
        except Exception:
            url.insert(0, "https://seraku.newton-x.net/api")
        def load_models() -> None:
            try:
                connection = NewtonXConnection()
                options = connection.models()
                self.models = [item.name for item in options]
                model["values"] = self.models
                if self.models and not model.get():
                    model.set(self.models[0])
                messagebox.showinfo("モデル一覧", f"{len(self.models)}件のモデルを取得しました。", parent=dialog)
            except Exception as error:
                messagebox.showerror("取得エラー", str(error), parent=dialog)
        ttk.Button(frame, text="NewtonXモデル一覧を取得", command=load_models).pack(anchor="w", pady=(0, 16))
        actions = ttk.Frame(frame)
        actions.pack(fill="x", side="bottom")
        def save() -> None:
            try:
                connection = NewtonXConnection()
                connection.save_settings(pat=pat.get(), model=model.get(), api_base_url=url.get())
                self.connection = connection
                self._load_status()
                dialog.destroy()
            except Exception as error:
                messagebox.showerror("保存エラー", str(error), parent=dialog)
        ttk.Button(actions, text="キャンセル", command=dialog.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(actions, text="設定を保存", style="Primary.TButton", command=save).pack(side="right")


if __name__ == "__main__":
    SalesCopilotDesktop().mainloop()
