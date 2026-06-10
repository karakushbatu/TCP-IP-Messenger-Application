"""Application shell."""

from __future__ import annotations

import customtkinter as ctk

from src.ui.split_view import SplitView
from src.ui.theme import COLORS, apply_theme


class AppShell:
    """Main application window."""

    def __init__(self) -> None:
        apply_theme()
        self.root = ctk.CTk()
        self.root.title("TCP Tactical Messenger")
        self.root.minsize(1100, 720)
        self.root.geometry("1400x820")
        self.root.configure(fg_color=COLORS["bg_primary"])

        self._split_view = SplitView(self.root)
        self._split_view.pack(fill="both", expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        self._split_view.shutdown()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()
