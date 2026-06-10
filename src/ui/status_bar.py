"""Connection status indicator."""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import COLORS, FONT_BODY


class StatusBar(ctk.CTkFrame):
    """Shows connection status with colored indicator."""

    STATUS_COLORS = {
        "Bağlı": COLORS["success"],
        "Bağlantı bekleniyor...": COLORS["warning"],
        "Bağlanıyor...": COLORS["warning"],
        "Bağlantı yok": COLORS["error"],
    }

    def __init__(self, master: ctk.CTkBaseClass, title: str = "") -> None:
        super().__init__(master, fg_color="transparent")
        self._title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["text_primary"],
        )
        self._title_label.pack(side="left")

        self._dot = ctk.CTkLabel(self, text="●", font=("Segoe UI", 12), text_color=COLORS["error"])
        self._dot.pack(side="right", padx=(8, 4))

        self._status_label = ctk.CTkLabel(
            self,
            text="Bağlantı yok",
            font=FONT_BODY,
            text_color=COLORS["text_secondary"],
        )
        self._status_label.pack(side="right")

    def set_title(self, title: str) -> None:
        self._title_label.configure(text=title)

    def set_status(self, status: str) -> None:
        self._status_label.configure(text=status)
        color = self.STATUS_COLORS.get(status, COLORS["text_secondary"])
        self._dot.configure(text_color=color)
