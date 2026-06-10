"""Split view with browser-style tabs."""

from __future__ import annotations

from dataclasses import dataclass

import customtkinter as ctk

from src.instance import Instance
from src.instance_manager import DemoMode, InstanceManager
from src.ui.detail_panel import DetailPanel
from src.ui.message_log import LogEntry
from src.ui.tab_bar import TabBar
from src.ui.theme import COLORS, FONT_SMALL, RADIUS
from src.ui.toast import ToastManager
from src.ui.welcome_screen import WelcomeScreen

HOME_TAB_ID = "home"
HOME_TAB_TITLE = "Home"


@dataclass
class AppTab:
    tab_id: str
    title: str
    is_home: bool
    container: ctk.CTkFrame
    manager: InstanceManager | None = None
    mode: DemoMode | None = None
    detail_panel: DetailPanel | None = None
    panels_container: ctk.CTkFrame | None = None


class SplitView(ctk.CTkFrame):
    """Tabbed application shell."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self._master = master
        self._toast = ToastManager(master)
        self._tabs: dict[str, AppTab] = {}
        self._active_tab_id = HOME_TAB_ID
        self._tab_counter = 0

        self._tab_bar = TabBar(
            self,
            on_select=self._switch_tab,
            on_close=self._close_tab,
            on_new_tab=self._add_instance_tab,
        )
        self._tab_bar.pack(fill="x")

        self._body = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        self._body.pack(fill="both", expand=True)

        self._add_home_tab(tab_id=HOME_TAB_ID, title=HOME_TAB_TITLE)
        self._poll_events()

    def _new_tab_id(self) -> str:
        self._tab_counter += 1
        return f"tab-{self._tab_counter}"

    def _add_home_tab(self, tab_id: str, title: str = HOME_TAB_TITLE) -> str:
        container = ctk.CTkFrame(self._body, fg_color=COLORS["bg_primary"])
        welcome = WelcomeScreen(
            container, on_select=lambda m, t=tab_id: self._start_demo(t, m)
        )
        welcome.pack(fill="both", expand=True)

        self._tabs[tab_id] = AppTab(
            tab_id=tab_id,
            title=title,
            is_home=True,
            container=container,
        )
        self._switch_tab(tab_id)
        return tab_id

    def _add_instance_tab(self) -> None:
        """Open a new instance picker tab (same tab converts to workspace on mode select)."""
        tid = self._new_tab_id()
        container = ctk.CTkFrame(self._body, fg_color=COLORS["bg_primary"])
        welcome = WelcomeScreen(
            container, on_select=lambda m, t=tid: self._start_demo(t, m)
        )
        welcome.pack(fill="both", expand=True)

        self._tabs[tid] = AppTab(
            tab_id=tid,
            title="Instance",
            is_home=True,
            container=container,
        )
        self._switch_tab(tid)

    def _populate_workspace(
        self, container: ctk.CTkFrame, tab_id: str, mode: DemoMode
    ) -> AppTab:
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        manager = InstanceManager(
            on_log_select=lambda e, t=tab_id: self._on_log_select(t, e)
        )

        header = ctk.CTkFrame(container, fg_color=COLORS["bg_secondary"], height=40)
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 0))
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text=f"  {self._mode_label(mode)}  ",
            font=FONT_SMALL,
            text_color=COLORS["accent_primary"],
            fg_color=COLORS["accent_glow"],
            corner_radius=RADIUS["sm"],
        ).pack(side="left", padx=10, pady=6)

        ctk.CTkLabel(
            header,
            text=self._mode_hint_text(mode),
            font=FONT_SMALL,
            text_color=COLORS["text_tertiary"],
        ).pack(side="left", padx=6)

        panels = ctk.CTkFrame(container, fg_color=COLORS["bg_primary"])
        panels.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        panels.grid_rowconfigure(0, weight=1)
        panels.grid_columnconfigure(0, weight=1)
        panels.grid_columnconfigure(2, weight=1)

        detail = DetailPanel(container)
        detail.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))

        tab = AppTab(
            tab_id=tab_id,
            title=self._mode_tab_title(mode),
            is_home=False,
            container=container,
            manager=manager,
            mode=mode,
            detail_panel=detail,
            panels_container=panels,
        )

        server, client = manager.setup_demo(
            mode,
            parent=panels,
            on_toast=self._show_toast,
            on_auto_connect=(
                lambda s, c, t=tab: self._auto_connect(t, s, c)
                if mode == "auto"
                else None
            ),
        )

        if client:
            server.panel.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
            ctk.CTkFrame(panels, width=2, fg_color=COLORS["border_subtle"]).grid(
                row=0, column=1, sticky="ns"
            )
            client.panel.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
        else:
            server.panel.grid(row=0, column=0, columnspan=3, sticky="nsew")

        return tab

    def _start_demo(self, tab_id: str, mode: DemoMode) -> None:
        """Convert the current picker tab into a workspace — no extra tab."""
        tab = self._tabs.get(tab_id)
        if not tab or not tab.is_home:
            return

        for child in tab.container.winfo_children():
            child.destroy()

        workspace = self._populate_workspace(tab.container, tab_id, mode)
        tab.title = workspace.title
        tab.is_home = False
        tab.manager = workspace.manager
        tab.mode = workspace.mode
        tab.detail_panel = workspace.detail_panel
        tab.panels_container = workspace.panels_container
        self._refresh_tab_bar()

    def _switch_tab(self, tab_id: str) -> None:
        if tab_id not in self._tabs:
            return
        for tid, tab in self._tabs.items():
            if tid == tab_id:
                tab.container.pack(fill="both", expand=True)
            else:
                tab.container.pack_forget()
        self._active_tab_id = tab_id
        self._refresh_tab_bar()

    def _close_tab(self, tab_id: str) -> None:
        if tab_id not in self._tabs:
            return

        tab = self._tabs[tab_id]

        if tab_id == HOME_TAB_ID:
            if tab.is_home:
                return
            self._reset_home_tab()
            return

        if tab.manager:
            tab.manager.stop_all()
        tab.container.destroy()
        del self._tabs[tab_id]
        if self._active_tab_id == tab_id:
            self._switch_tab(HOME_TAB_ID)
        self._refresh_tab_bar()

    def _reset_home_tab(self) -> None:
        """Return Home tab to initial welcome screen."""
        tab = self._tabs[HOME_TAB_ID]
        if tab.manager:
            tab.manager.stop_all()
        for child in tab.container.winfo_children():
            child.destroy()

        welcome = WelcomeScreen(
            tab.container,
            on_select=lambda m, t=HOME_TAB_ID: self._start_demo(t, m),
        )
        welcome.pack(fill="both", expand=True)

        tab.title = HOME_TAB_TITLE
        tab.is_home = True
        tab.manager = None
        tab.mode = None
        tab.detail_panel = None
        tab.panels_container = None
        self._switch_tab(HOME_TAB_ID)
        self._refresh_tab_bar()

    def _refresh_tab_bar(self) -> None:
        items = [
            (tid, t.title, not (tid == HOME_TAB_ID and t.is_home))
            for tid, t in self._tabs.items()
        ]
        self._tab_bar.set_tabs(items, self._active_tab_id)

    def _mode_tab_title(self, mode: DemoMode) -> str:
        return {
            "auto": "Auto Connect",
            "manual": "Manual Connect",
            "server_only": "Server Instance",
            "client_only": "Client Instance",
        }.get(mode, mode)

    def _mode_label(self, mode: DemoMode) -> str:
        return {
            "auto": "Auto",
            "manual": "Manual",
            "server_only": "Server",
            "client_only": "Client",
        }.get(mode, mode)

    def _mode_hint_text(self, mode: DemoMode) -> str:
        return {
            "auto": "Server and client start and connect automatically",
            "manual": "Start the server, then connect from the client",
            "server_only": "Server listens only",
            "client_only": "Client connects only",
        }.get(mode, "")

    def _on_log_select(self, tab_id: str, entry: LogEntry) -> None:
        tab = self._tabs.get(tab_id)
        if not tab or not tab.detail_panel:
            return
        if entry.is_warning:
            tab.detail_panel.show_entry(
                entry.timestamp, entry.direction, unknown_id=entry.unknown_id
            )
        elif entry.is_error:
            tab.detail_panel.show_entry(
                entry.timestamp, entry.direction, error_text=entry.error_text
            )
        else:
            tab.detail_panel.show_entry(
                entry.timestamp,
                entry.direction,
                message=entry.message,
                is_auto=entry.is_auto,
            )

    def _auto_connect(self, tab: AppTab, server: Instance, client: Instance) -> None:
        server.start_server(8080)
        self._show_toast("Server started", "success")

        def try_connect() -> None:
            if client.connect("127.0.0.1", 8080):
                pass
            else:
                self._show_toast("Connection failed", "error")

        self._master.after(300, try_connect)

    def _show_toast(self, message: str, toast_type: str = "info") -> None:
        self._toast.show(message, toast_type)

    def _poll_events(self) -> None:
        for tab in self._tabs.values():
            if tab.manager:
                tab.manager.process_all_events()
        self._master.after(50, self._poll_events)

    def shutdown(self) -> None:
        for tab in self._tabs.values():
            if tab.manager:
                tab.manager.stop_all()
