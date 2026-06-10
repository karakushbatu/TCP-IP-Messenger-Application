"""Split view layout for multiple instances."""

from __future__ import annotations

import customtkinter as ctk

from src.instance import Instance
from src.instance_manager import DemoMode, InstanceManager
from src.ui.detail_panel import DetailPanel
from src.ui.message_log import LogEntry
from src.ui.theme import COLORS, FONT_HEADING
from src.ui.toast import ToastManager
from src.ui.welcome_screen import WelcomeScreen


class SplitView(ctk.CTkFrame):
    """Main application layout with split panels and shared detail view."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self._master = master
        self._toast = ToastManager(master)
        self._manager = InstanceManager(on_log_select=self._on_log_select)
        self._current_mode: DemoMode | None = None

        self._header = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=48)
        self._header.pack(fill="x")
        self._header.pack_propagate(False)

        ctk.CTkLabel(
            self._header,
            text="TCP Tactical Messenger",
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=16, pady=8)

        ctk.CTkButton(
            self._header,
            text="+ Yeni Instance",
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["bg_hover"],
            command=self._show_welcome,
        ).pack(side="right", padx=16, pady=8)

        self._content = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        self._content.pack(fill="both", expand=True)

        self._welcome = WelcomeScreen(self._content, on_select=self._start_demo)
        self._welcome.pack(fill="both", expand=True)

        self._split_frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg_primary"])

        self._panels_container = ctk.CTkFrame(self._split_frame, fg_color=COLORS["bg_primary"])
        self._panels_container.pack(fill="both", expand=True, padx=8, pady=8)

        self._detail_panel = DetailPanel(self)
        self._detail_panel.pack(fill="x", padx=8, pady=(0, 8))

        self._poll_events()

    def _show_welcome(self) -> None:
        self._manager.stop_all()
        self._split_frame.pack_forget()
        self._welcome.pack(fill="both", expand=True)

    def _start_demo(self, mode: DemoMode) -> None:
        self._current_mode = mode
        self._welcome.pack_forget()
        self._split_frame.pack(fill="both", expand=True)

        for child in self._panels_container.winfo_children():
            child.destroy()

        server, client = self._manager.setup_demo(
            mode,
            parent=self._panels_container,
            on_toast=self._show_toast,
            on_auto_connect=self._auto_connect,
        )

        if client:
            server.panel.pack(side="left", fill="both", expand=True, padx=(0, 4))
            client.panel.pack(side="right", fill="both", expand=True, padx=(4, 0))
        else:
            server.panel.pack(fill="both", expand=True)

    def _on_log_select(self, entry: LogEntry) -> None:
        if entry.is_warning:
            self._detail_panel.show_entry(
                entry.timestamp,
                entry.direction,
                unknown_id=entry.unknown_id,
            )
        elif entry.is_error:
            self._detail_panel.show_entry(
                entry.timestamp,
                entry.direction,
                error_text=entry.error_text,
            )
        else:
            self._detail_panel.show_entry(
                entry.timestamp,
                entry.direction,
                message=entry.message,
                is_auto=entry.is_auto,
            )

    def _auto_connect(self, server: Instance, client: Instance) -> None:
        server.start_server(8080)
        self._show_toast("Sunucu başlatıldı", "success")

        def try_connect() -> None:
            if not client.connect("127.0.0.1", 8080):
                self._show_toast("Bağlantı kurulamadı", "error")

        self._master.after(300, try_connect)

    def _show_toast(self, message: str, toast_type: str = "info") -> None:
        self._toast.show(message, toast_type)

    def _poll_events(self) -> None:
        self._manager.process_all_events()
        self._master.after(50, self._poll_events)

    def shutdown(self) -> None:
        self._manager.stop_all()
