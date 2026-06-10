"""Shared message detail panel."""

from __future__ import annotations

import customtkinter as ctk

from src.protocol.messages import Message, get_message_short_label, message_to_dict
from src.ui.theme import COLORS, FONT_BODY, FONT_HEADING, FONT_MONO


class DetailPanel(ctk.CTkFrame):
    """Bottom panel showing detailed message information."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color=COLORS["bg_secondary"], corner_radius=8)
        self._title = ctk.CTkLabel(
            self,
            text="Mesaj Detayı",
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
        )
        self._title.pack(anchor="w", padx=16, pady=(12, 4))

        self._meta_label = ctk.CTkLabel(
            self,
            text="Bir mesaj seçin",
            font=FONT_MONO,
            text_color=COLORS["text_tertiary"],
            anchor="w",
        )
        self._meta_label.pack(anchor="w", padx=16, pady=(0, 4))

        self._fields_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._fields_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    def clear(self) -> None:
        self._meta_label.configure(text="Bir mesaj seçin")
        for child in self._fields_frame.winfo_children():
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
        for child in self._fields_frame.winfo_children():
            child.destroy()

        auto_tag = " [Otomatik]" if is_auto else ""
        if unknown_id is not None:
            self._meta_label.configure(
                text=f"[{timestamp}] {direction} — Tanımsız Mesaj ID: {unknown_id}"
            )
            warn = ctk.CTkLabel(
                self._fields_frame,
                text="⚠ Tanımlı olmayan mesaj alındı",
                font=FONT_BODY,
                text_color=COLORS["warning"],
                anchor="w",
            )
            warn.pack(anchor="w", pady=2)
            return

        if error_text:
            self._meta_label.configure(text=f"[{timestamp}] {direction} — Hata")
            err = ctk.CTkLabel(
                self._fields_frame,
                text=f"✕ {error_text}",
                font=FONT_BODY,
                text_color=COLORS["error"],
                anchor="w",
            )
            err.pack(anchor="w", pady=2)
            return

        if message is None:
            self.clear()
            return

        msg_label = get_message_short_label(message.message_id)
        self._meta_label.configure(
            text=f"[{timestamp}] {direction} {msg_label}{auto_tag}"
        )

        for label, value in message_to_dict(message).items():
            row = ctk.CTkFrame(self._fields_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=FONT_BODY,
                text_color=COLORS["text_secondary"],
                width=280,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=str(value),
                font=FONT_MONO,
                text_color=COLORS["text_primary"],
                anchor="w",
            ).pack(side="left", padx=(8, 0))
