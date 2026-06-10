"""Shared message detail panel."""

from __future__ import annotations

import customtkinter as ctk

from src.protocol.messages import Message, get_message_short_label, message_to_dict
from src.ui.theme import COLORS, FONT_BODY, FONT_HEADING, FONT_MONO, FONT_SMALL, RADIUS

DETAIL_PANEL_HEIGHT = 160


class DetailPanel(ctk.CTkFrame):
    """Compact bottom panel showing detailed message information."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(
            master,
            fg_color=COLORS["bg_secondary"],
            corner_radius=RADIUS["lg"],
            border_color=COLORS["border_subtle"],
            border_width=1,
            height=DETAIL_PANEL_HEIGHT,
        )
        self.grid_propagate(False)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            header,
            text="Mesaj Detayı",
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="Log satırına tıklayın",
            font=FONT_SMALL,
            text_color=COLORS["text_tertiary"],
        ).pack(side="left", padx=(10, 0))

        self._meta_label = ctk.CTkLabel(
            self,
            text="Henüz seçili mesaj yok",
            font=FONT_MONO,
            text_color=COLORS["text_tertiary"],
            anchor="w",
        )
        self._meta_label.pack(anchor="w", padx=14, pady=(0, 4))

        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_input"],
            corner_radius=RADIUS["sm"],
            height=80,
            scrollbar_button_color=COLORS["bg_elevated"],
        )
        self._scroll.pack(fill="both", expand=True, padx=14, pady=(0, 10))

    def clear(self) -> None:
        self._meta_label.configure(text="Henüz seçili mesaj yok")
        for child in self._scroll.winfo_children():
            child.destroy()

    def show_entry(
        self,
        timestamp: str,
        direction: str,
        message: Message | None = None,
        is_auto: bool = False,
        error_text: str | None = None,
        unknown_id: int | None = None,
    ) -> None:
        """Display detail for a log entry."""
        for child in self._scroll.winfo_children():
            child.destroy()

        auto_tag = " [Otomatik]" if is_auto else ""

        if unknown_id is not None:
            self._meta_label.configure(
                text=f"[{timestamp}] {direction} — Tanımsız Mesaj ID: {unknown_id}"
            )
            ctk.CTkLabel(
                self._scroll,
                text="⚠ Tanımlı olmayan mesaj alındı",
                font=FONT_BODY,
                text_color=COLORS["warning"],
                anchor="w",
            ).pack(anchor="w", pady=2, padx=4)
            return

        if error_text:
            self._meta_label.configure(text=f"[{timestamp}] {direction} — Hata")
            ctk.CTkLabel(
                self._scroll,
                text=f"✕ {error_text}",
                font=FONT_BODY,
                text_color=COLORS["error"],
                anchor="w",
            ).pack(anchor="w", pady=2, padx=4)
            return

        if message is None:
            self.clear()
            return

        msg_label = get_message_short_label(message.message_id)
        self._meta_label.configure(
            text=f"[{timestamp}] {direction} {msg_label}{auto_tag}"
        )

        for label, value in message_to_dict(message).items():
            row = ctk.CTkFrame(self._scroll, fg_color="transparent")
            row.pack(fill="x", pady=1, padx=4)
            ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=FONT_BODY,
                text_color=COLORS["text_secondary"],
                width=260,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=str(value),
                font=FONT_MONO,
                text_color=COLORS["text_primary"],
                anchor="w",
            ).pack(side="left", padx=(6, 0))
