from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from newtonx_connection import NewtonXConnection


COLORS = {
    "navy": "#17243a",
    "ink": "#1d293d",
    "muted": "#738096",
    "line": "#e7ebf2",
    "bg": "#f7f9fc",
    "purple": "#6652d8",
    "purple_light": "#f0edff",
    "blue": "#2878d8",
    "blue_light": "#edf5ff",
    "green": "#159466",
    "white": "#ffffff",
}


class SalesCopilotDesktop(tk.Tk):
    """Native desktop UI styled to match the NewtonX Sales Copilot web UI."""

    def __init__(self) -> None:
        super().__init__()
        self.title("NewtonX Sales Copilot")
        self.geometry("1440x900")
        self.minsize(1120, 720)
        self.configure(background=COLORS["bg"])
        self.connection: NewtonXConnection | None = None
        self.models: list[str] = []
        self._configure_style()
        self._build_shell()
        self._load_status()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Copilot.TEntry", padding=9, fieldbackground="white")
        style.configure("Copilot.TCombobox", padding=7)
        style.configure("Copilot.Treeview", background="white", fieldbackground="white", foreground=COLORS["ink"], rowheight=30, borderwidth=0)
        style.configure("Copilot.Treeview.Heading", background="white", foreground=COLORS["muted"], font=("Yu Gothic UI", 9, "bold"))
        style.map("Copilot.Treeview", background=[("selected", COLORS["purple_light"])], foreground=[("selected", COLORS["purple"])])

    def _label(self, parent: tk.Misc, text: str, **kwargs: object) -> tk.Label:
        return tk.Label(parent, text=text, bg=kwargs.pop("bg", parent.cget("bg")), fg=kwargs.pop("fg", COLORS["ink"]), font=kwargs.pop("font", ("Yu Gothic UI", 10)), **kwargs)

    def _button(self, parent: tk.Misc, text: str, command: Callable[[], None], color: str = "white", fg: str = COLORS["muted"], **kwargs: object) -> tk.Button:
        return tk.Button(parent, text=text, command=command, bg=color, fg=fg, activebackground=color, activeforeground=fg, relief="flat", bd=0, cursor="hand2", font=("Yu Gothic UI", 10, "bold"), padx=kwargs.pop("padx", 14), pady=kwargs.pop("pady", 8), **kwargs)

    def _build_shell(self) -> None:
        self.sidebar = tk.Frame(self, bg=COLORS["white"], width=270, highlightbackground=COLORS["line"], highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        self.main = tk.Frame(self, bg=COLORS["bg"])
        self.main.pack(side="left", fill="both", expand=True)
        self._build_main()

    def _build_sidebar(self) -> None:
        brand = tk.Frame(self.sidebar, bg=COLORS["white"])
        brand.pack(fill="x", padx=20, pady=(23, 28))
        tk.Label(brand, text="N", bg="#725de7", fg="white", font=("Yu Gothic UI", 17, "bold"), width=2, height=1).pack(side="left", padx=(0, 9))
        brand_text = tk.Frame(brand, bg="white")
        brand_text.pack(side="left")
        self._label(brand_text, "NewtonX", font=("Yu Gothic UI", 15, "bold")).pack(anchor="w")
        self._label(brand_text, "Sales Copilot", fg="#99a2b4", font=("Yu Gothic UI", 9)).pack(anchor="w")

        self._label(self.sidebar, "WORKSPACE", fg="#a0a9ba", font=("Yu Gothic UI", 9, "bold")).pack(anchor="w", padx=25)
        workspace = tk.Frame(self.sidebar, bg="white", highlightbackground=COLORS["line"], highlightthickness=1)
        workspace.pack(fill="x", padx=20, pady=(6, 20))
        self._label(workspace, "営業本部", font=("Yu Gothic UI", 10, "bold")).pack(side="left", padx=11, pady=9)
        self._label(workspace, "⋮", fg="#99a2b4", font=("Yu Gothic UI", 14)).pack(side="right", padx=10)

        nav = tk.Frame(self.sidebar, bg="white")
        nav.pack(fill="x", padx=14, pady=(0, 18))
        self._nav_button(nav, "▦  商談ワークスペース", True)
        self._nav_button(nav, "▤  商材ライブラリ                 24", False, self._library_message)
        self._nav_button(nav, "◷  アクティビティ", False)

        heading = tk.Frame(self.sidebar, bg="white")
        heading.pack(fill="x", padx=20, pady=(0, 8))
        self._label(heading, "商談ナレッジ", fg="#a0a9ba", font=("Yu Gothic UI", 9, "bold")).pack(side="left")
        self._button(heading, "＋", self._add_company, color=COLORS["purple_light"], fg=COLORS["purple"], padx=7, pady=2).pack(side="right")

        tree_frame = tk.Frame(self.sidebar, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=14)
        self.tree = ttk.Treeview(tree_frame, show="tree", style="Copilot.Treeview")
        self.tree.pack(fill="both", expand=True)
        self._populate_tree()

        footer = tk.Frame(self.sidebar, bg="white", highlightbackground=COLORS["line"], highlightthickness=1)
        footer.pack(fill="x", side="bottom", padx=14, pady=(12, 0))
        self._label(footer, "●  NewtonXADK 接続中", fg=COLORS["green"], font=("Yu Gothic UI", 9)).pack(anchor="w", padx=8, pady=11)
        user = tk.Frame(footer, bg="white")
        user.pack(fill="x", padx=4, pady=(0, 10))
        tk.Label(user, text="田", bg="#ffe1d5", fg="#a65438", font=("Yu Gothic UI", 10), width=2, height=1).pack(side="left")
        self._label(user, "田中 恒一", font=("Yu Gothic UI", 9, "bold")).pack(side="left", padx=8)
        self._label(user, "営業マネージャー", fg="#98a2b2", font=("Yu Gothic UI", 8)).pack(side="left")

    def _nav_button(self, parent: tk.Frame, text: str, active: bool, command: Callable[[], None] | None = None) -> None:
        self._button(parent, text, command or (lambda: None), color=COLORS["purple_light"] if active else "white", fg=COLORS["purple"] if active else "#7a8699", padx=11, pady=9, anchor="w").pack(fill="x", pady=2)

    def _populate_tree(self) -> None:
        records = [
            ("株式会社アトラス", "山田 太郎", "情報システム部 部長", ["基幹システム刷新", "定例フォロー 06/12"]),
            ("ネクストソリューションズ", "佐藤 花子", "DX推進室", ["AI活用支援"]),
            ("グローバルテック", "鈴木 一郎", "開発部", ["人材提案"]),
        ]
        for company, person, role, deals in records:
            company_id = self.tree.insert("", "end", text=f"▣  {company}", open=True)
            person_id = self.tree.insert(company_id, "end", text=f"♙  {person}", open=True)
            role_id = self.tree.insert(person_id, "end", text=f"◆  {role}", open=True)
            for deal in deals:
                self.tree.insert(role_id, "end", text=f"▤  {deal}")

    def _build_main(self) -> None:
        topbar = tk.Frame(self.main, bg=COLORS["white"], height=64, highlightbackground=COLORS["line"], highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        self._label(topbar, "商談ワークスペース   /   ", fg="#8c98aa", font=("Yu Gothic UI", 10)).pack(side="left", padx=38)
        self._label(topbar, "株式会社アトラス", fg="#46546a", font=("Yu Gothic UI", 10)).place(x=160, y=23)
        actions = tk.Frame(topbar, bg="white")
        actions.pack(side="right", padx=28)
        self.status_label = self._label(topbar, "接続状態を確認中...", fg="#159466", font=("Yu Gothic UI", 9))
        self.status_label.place(x=380, y=24)
        self._button(actions, "⌕", lambda: None, color="white", fg="#758198", padx=5, pady=5).pack(side="left")
        self._button(actions, "♧", lambda: None, color="white", fg="#758198", padx=5, pady=5).pack(side="left")
        self._button(actions, "⚙ 接続設定", self._open_settings, color="white", fg="#53627a", padx=10, pady=6).pack(side="left", padx=8)
        self._button(actions, "?", lambda: None, color="white", fg="#758198", padx=5, pady=4).pack(side="left")

        content = tk.Frame(self.main, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=42, pady=34)
        heading = tk.Frame(content, bg=COLORS["bg"])
        heading.pack(fill="x", pady=(0, 25))
        left = tk.Frame(heading, bg=COLORS["bg"])
        left.pack(side="left")
        self._label(left, "CUSTOMER ACCOUNT", fg="#9ca7b7", font=("Yu Gothic UI", 9, "bold")).pack(anchor="w")
        self.company_label = self._label(left, "株式会社アトラス", font=("Yu Gothic UI", 23, "bold"))
        self.company_label.pack(anchor="w", pady=(4, 7))
        self._label(left, "▣ 東京都渋谷区    ", fg="#8792a4", font=("Yu Gothic UI", 9)).pack(side="left")
        self._label(left, "● 取引中    最終接触 2024/06/12", fg=COLORS["green"], font=("Yu Gothic UI", 9)).pack(side="left")
        self._button(heading, "▤  商材ライブラリ", self._library_message, color="white", fg="#53627a", padx=13, pady=9).pack(side="right", anchor="s")

        self.tabs = tk.Frame(content, bg=COLORS["bg"])
        self.tabs.pack(fill="x", pady=(0, 22))
        self.scenario_tab_button = self._tab_button(self.tabs, "✦", "商談シナリオ生成AI", "商談前の準備をアシスト", True, self._show_scenario)
        self.scenario_tab_button.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.ball_tab_button = self._tab_button(self.tabs, "◌", "ボール管理AI", "商談後の分析と次回提案", False, self._show_ball)
        self.ball_tab_button.pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.panel_host = tk.Frame(content, bg=COLORS["bg"])
        self.panel_host.pack(fill="both", expand=True)
        self._build_scenario_panel()

    def _tab_button(self, parent: tk.Frame, icon: str, title: str, subtitle: str, active: bool, command: Callable[[], None]) -> tk.Frame:
        frame = tk.Frame(parent, bg=COLORS["purple_light"] if active else "white", highlightbackground="#bdb5fa" if active else COLORS["line"], highlightthickness=1, cursor="hand2")
        tk.Label(frame, text=icon, bg=COLORS["purple_light"] if active else COLORS["blue_light"], fg=COLORS["purple"] if active else COLORS["blue"], font=("Yu Gothic UI", 18), width=3).pack(side="left", padx=12, pady=12)
        text = tk.Frame(frame, bg=frame.cget("bg"))
        text.pack(side="left", anchor="w")
        self._label(text, title, bg=frame.cget("bg"), font=("Yu Gothic UI", 10, "bold")).pack(anchor="w")
        self._label(text, subtitle, bg=frame.cget("bg"), fg="#929daf", font=("Yu Gothic UI", 9)).pack(anchor="w", pady=(3, 0))
        self._label(frame, "→", bg=frame.cget("bg"), fg="#a5afbd", font=("Yu Gothic UI", 16)).pack(side="right", padx=15)
        for widget in (frame, *frame.winfo_children()):
            widget.bind("<Button-1>", lambda _event: command())
        return frame

    def _card(self, parent: tk.Frame) -> tk.Frame:
        return tk.Frame(parent, bg="white", highlightbackground=COLORS["line"], highlightthickness=1)

    def _build_scenario_panel(self) -> None:
        self._clear_panel()
        intro = tk.Frame(self.panel_host, bg=COLORS["bg"])
        intro.pack(fill="x", pady=(0, 12))
        self._label(intro, "商談シナリオを作成", font=("Yu Gothic UI", 15, "bold")).pack(anchor="w")
        self._label(intro, "顧客情報と商談の目的から、成果につながる会話の道筋を設計します。", fg="#8490a3", font=("Yu Gothic UI", 9)).pack(anchor="w", pady=(4, 0))
        self._label(intro, "✦ NewtonXADK AI", bg=COLORS["purple_light"], fg=COLORS["purple"], font=("Yu Gothic UI", 9, "bold")).pack(anchor="e", pady=(0, 2))

        card = self._card(self.panel_host)
        card.pack(fill="x", pady=(0, 14))
        form = tk.Frame(card, bg="white")
        form.pack(fill="x", padx=24, pady=22)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)
        self._label(form, "商談目的", bg="white", fg="#53627a", font=("Yu Gothic UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.purpose = ttk.Combobox(form, values=["案件獲得", "要件確認", "人材提案", "単価交渉", "関係構築", "定例フォロー", "トラブルフォロー", "信頼回復", "ビジョン共有", "顧客課題整理", "取引拡大"], state="readonly", style="Copilot.TCombobox")
        self.purpose.set("案件獲得")
        self.purpose.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 18), pady=(6, 16))
        self._label(form, "商談状況", bg="white", fg="#53627a", font=("Yu Gothic UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.scenario_status = ttk.Combobox(form, values=["初回商談・課題ヒアリング前", "提案内容を検討中", "社内稟議・決裁待ち", "既存顧客への定例フォロー"], state="readonly", style="Copilot.TCombobox")
        self.scenario_status.set("初回商談・課題ヒアリング前")
        self.scenario_status.grid(row=1, column=2, columnspan=2, sticky="ew", pady=(6, 16))
        self._label(form, "今回の商談で確認したいこと", bg="white", fg="#53627a", font=("Yu Gothic UI", 9, "bold")).grid(row=2, column=0, columnspan=4, sticky="w")
        self.scenario_input = tk.Text(form, height=4, wrap="word", bg="white", fg=COLORS["ink"], relief="solid", bd=1, highlightthickness=1, highlightbackground="#dbe2ec", font=("Yu Gothic UI", 10))
        self.scenario_input.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(6, 0))
        footer = tk.Frame(form, bg="white")
        footer.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(14, 0))
        self._label(footer, "顧客の過去の商談履歴も自動で参照します", bg="white", fg="#a0a9b7", font=("Yu Gothic UI", 8)).pack(side="left")
        self._button(footer, "✦  シナリオを生成", self._generate_scenario, color=COLORS["purple"], fg="white", padx=15, pady=9).pack(side="right")
        self.scenario_output = self._output_card(self.panel_host)

    def _build_ball_panel(self) -> None:
        self._clear_panel()
        intro = tk.Frame(self.panel_host, bg=COLORS["bg"])
        intro.pack(fill="x", pady=(0, 12))
        self._label(intro, "商談を振り返り、次の一手へ", font=("Yu Gothic UI", 15, "bold")).pack(anchor="w")
        self._label(intro, "議事録やメモを貼り付けるだけで、案件の現在地と次回提案を整理します。", fg="#8490a3", font=("Yu Gothic UI", 9)).pack(anchor="w", pady=(4, 0))
        self._label(intro, "✦ NewtonXADK AI", bg=COLORS["blue_light"], fg=COLORS["blue"], font=("Yu Gothic UI", 9, "bold")).pack(anchor="e", pady=(0, 2))
        card = self._card(self.panel_host)
        card.pack(fill="x", pady=(0, 14))
        inner = tk.Frame(card, bg="white")
        inner.pack(fill="x", padx=24, pady=22)
        self._label(inner, "議事録・商談メモ", bg="white", fg="#53627a", font=("Yu Gothic UI", 9, "bold")).pack(anchor="w")
        self.meeting_input = tk.Text(inner, height=7, wrap="word", bg="white", fg=COLORS["ink"], relief="solid", bd=1, highlightthickness=1, highlightbackground="#dbe2ec", font=("Yu Gothic UI", 10))
        self.meeting_input.pack(fill="x", pady=(6, 0))
        footer = tk.Frame(inner, bg="white")
        footer.pack(fill="x", pady=(14, 0))
        self._label(footer, "入力内容はこのワークスペースに保存されます", bg="white", fg="#a0a9b7", font=("Yu Gothic UI", 8)).pack(side="left")
        self._button(footer, "◌  商談を分析", self._analyze_meeting, color=COLORS["blue"], fg="white", padx=15, pady=9).pack(side="right")
        self.ball_output = self._output_card(self.panel_host)

    def _output_card(self, parent: tk.Frame) -> tk.Text:
        card = self._card(parent)
        card.pack(fill="both", expand=True)
        output = tk.Text(card, height=12, wrap="word", state="disabled", background="white", foreground=COLORS["ink"], relief="flat", padx=22, pady=18, font=("Yu Gothic UI", 10))
        output.pack(fill="both", expand=True)
        return output

    def _clear_panel(self) -> None:
        for child in self.panel_host.winfo_children():
            child.destroy()

    def _show_scenario(self) -> None:
        self.scenario_tab_button.configure(bg=COLORS["purple_light"])
        self.ball_tab_button.configure(bg="white")
        self._build_scenario_panel()

    def _show_ball(self) -> None:
        self.scenario_tab_button.configure(bg="white")
        self.ball_tab_button.configure(bg=COLORS["blue_light"])
        self._build_ball_panel()

    def _output_text(self, widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _run_background(self, task: Callable[[], str], output: tk.Text) -> None:
        self._output_text(output, "NewtonXで処理中です...")
        def worker() -> None:
            try:
                result = task()
            except Exception as error:
                result = f"エラー: {error}"
            self.after(0, lambda: self._output_text(output, result))
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

    def _library_message(self) -> None:
        messagebox.showinfo("商材ライブラリ", "商材ライブラリ（24件）を開きました。", parent=self)

    def _add_company(self) -> None:
        messagebox.showinfo("商談ナレッジ", "顧客情報を追加するにはNewtonXADKへ接続してください。", parent=self)

    def _load_status(self) -> None:
        try:
            self.connection = NewtonXConnection()
            status = self.connection.status()
            if hasattr(self, "status_label"):
                self.status_label.configure(text=f"● {status.get('default_model')}" if status["configured"] else "● PAT未設定", fg=COLORS["green"] if status["configured"] else COLORS["muted"])
        except Exception:
            if hasattr(self, "status_label"):
                self.status_label.configure(text="● ADK未接続", fg="#c47532")

    def _open_settings(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("NewtonXADK 接続設定")
        dialog.geometry("560x360")
        dialog.configure(background=COLORS["bg"])
        dialog.transient(self)
        dialog.grab_set()
        frame = tk.Frame(dialog, bg="white", padx=22, pady=20)
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        self._label(frame, "INTEGRATION", bg="white", fg="#9ca7b7", font=("Yu Gothic UI", 9, "bold")).pack(anchor="w")
        self._label(frame, "NewtonXADK 接続設定", bg="white", font=("Yu Gothic UI", 16, "bold")).pack(anchor="w", pady=(3, 14))
        self._label(frame, "APIベースURL", bg="white", fg="#53627a", font=("Yu Gothic UI", 9, "bold")).pack(anchor="w")
        url = ttk.Entry(frame, style="Copilot.TEntry")
        url.pack(fill="x", pady=(4, 10))
        self._label(frame, "アクセストークン（PAT）", bg="white", fg="#53627a", font=("Yu Gothic UI", 9, "bold")).pack(anchor="w")
        pat = ttk.Entry(frame, show="*", style="Copilot.TEntry")
        pat.pack(fill="x", pady=(4, 10))
        self._label(frame, "AIモデル", bg="white", fg="#53627a", font=("Yu Gothic UI", 9, "bold")).pack(anchor="w")
        model = ttk.Combobox(frame, state="readonly", style="Copilot.TCombobox")
        model.pack(fill="x", pady=(4, 9))
        try:
            current = self.connection or NewtonXConnection()
            status = current.status()
            url.insert(0, status.get("api_base_url") or "https://seraku.newton-x.net/api")
            model.set(status.get("default_model") or "")
        except Exception:
            url.insert(0, "https://seraku.newton-x.net/api")
        def load_models() -> None:
            try:
                options = NewtonXConnection().models()
                self.models = [item.name for item in options]
                model["values"] = self.models
                if self.models and not model.get():
                    model.set(self.models[0])
                messagebox.showinfo("モデル一覧", f"{len(self.models)}件のモデルを取得しました。", parent=dialog)
            except Exception as error:
                messagebox.showerror("取得エラー", str(error), parent=dialog)
        self._button(frame, "NewtonXモデル一覧を取得", load_models, color=COLORS["purple_light"], fg=COLORS["purple"], padx=10, pady=6).pack(anchor="w")
        actions = tk.Frame(frame, bg="white")
        actions.pack(fill="x", side="bottom", pady=(15, 0))
        self._button(actions, "キャンセル", dialog.destroy, color="white", fg="#53627a").pack(side="right", padx=(8, 0))
        def save() -> None:
            try:
                connection = NewtonXConnection()
                connection.save_settings(pat=pat.get(), model=model.get(), api_base_url=url.get())
                self.connection = connection
                dialog.destroy()
                messagebox.showinfo("接続設定", "NewtonX接続設定を保存しました。", parent=self)
            except Exception as error:
                messagebox.showerror("保存エラー", str(error), parent=dialog)
        self._button(actions, "設定を保存", save, color=COLORS["purple"], fg="white").pack(side="right")


if __name__ == "__main__":
    SalesCopilotDesktop().mainloop()
