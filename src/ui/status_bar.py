"""Connection status indicator."""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import COLORS, FONT_BODY, FONT_SUBHEADING


class StatusBar(ctk.CTkFrame):
    """Shows connection status with colored indicator."""

    STATUS_COLORS = {
        "Connected": COLORS["success"],
        "Waiting for connection...": COLORS["warning"],
        "Connecting...": COLORS["warning"],
        "Not connected": COLORS["text_tertiary"],
    }

    def __init__(self, master: ctk.CTkBaseClass, title: str = "") -> None:
        super().__init__(master, fg_color="transparent")
        self._title_label = ctk.CTkLabel(
            self,
            text=title,
            font=FONT_SUBHEADING,
            text_color=COLORS["text_primary"],
        )
        self._title_label.pack(side="left")

        status_wrap = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_input"],
            corner_radius=20,
            border_color=COLORS["border_subtle"],
            border_width=1,
        )
        status_wrap.pack(side="right")

        inner = ctk.CTkFrame(status_wrap, fg_color="transparent")
        inner.pack(padx=10, pady=4)

        self._dot = ctk.CTkLabel(
            inner, text="●", font=("Segoe UI", 10), text_color=COLORS["text_tertiary"]
        )
        self._dot.pack(side="left", padx=(0, 6))

        self._status_label = ctk.CTkLabel(
            inner,
            text="Not connected",
            font=FONT_BODY,
            text_color=COLORS["text_secondary"],
        )
        self._status_label.pack(side="left")

    def set_title(self, title: str) -> None:
        self._title_label.configure(text=title)

    def set_status(self, status: str) -> None:
        self._status_label.configure(text=status)
        color = self.STATUS_COLORS.get(status, COLORS["text_tertiary"])
        self._dot.configure(text_color=color)
