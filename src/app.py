"""Application shell."""

from __future__ import annotations

import customtkinter as ctk

from src.app_info import APP_NAME
from src.ui.split_view import SplitView
from src.ui.theme import COLORS, apply_theme


class AppShell:
    """Single-window application with in-app tabs."""

    def __init__(self) -> None:
        apply_theme()
        self.root = ctk.CTk()
        self.root.title(APP_NAME)
        self._fit_window_geometry()
        self.root.configure(fg_color=COLORS["bg_primary"])

        self._split_view = SplitView(self.root)
        self._split_view.pack(fill="both", expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _fit_window_geometry(self) -> None:
        """Size window to the display — avoids clipped panels on MacBook screens."""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        width = min(1280, max(960, int(screen_w * 0.92)))
        height = min(820, max(620, int(screen_h * 0.88)))
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(min(880, width), min(560, height))

    def _on_close(self) -> None:
        self._split_view.shutdown()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()
