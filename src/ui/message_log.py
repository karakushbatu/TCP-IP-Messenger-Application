"""Scrollable message history log."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

import customtkinter as ctk

from src.protocol.messages import Message, get_message_short_label
from src.ui.theme import COLORS, FONT_MONO


@dataclass
class LogEntry:
    timestamp: str
    direction: str  # "Transmit" or "Receive"
    message_id: int | None
    is_auto: bool = False
    is_warning: bool = False
    is_error: bool = False
    error_text: str | None = None
    unknown_id: int | None = None
    message: Message | None = None
    raw_timestamp: datetime | None = None


class MessageLog(ctk.CTkFrame):
    """Scrollable message history with click-to-detail."""

    MAX_ENTRIES = 500

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_select: Callable[[LogEntry], None] | None = None,
    ) -> None:
        super().__init__(master, fg_color=COLORS["bg_secondary"], corner_radius=8)
        self._on_select = on_select
        self._entries: list[LogEntry] = []
        self._auto_scroll = True

        header = ctk.CTkLabel(
            self,
            text="Mesaj Geçmişi",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["text_primary"],
        )
        header.pack(anchor="w", padx=12, pady=(10, 4))

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_primary"], corner_radius=6)
        self._scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._scroll.bind("<MouseWheel>", self._on_scroll)

    def _on_scroll(self, _event: object) -> None:
        self._auto_scroll = False

    def add_entry(self, entry: LogEntry) -> None:
        """Add a log entry to the history."""
        self._entries.append(entry)
        if len(self._entries) > self.MAX_ENTRIES:
            self._entries = self._entries[-self.MAX_ENTRIES :]
            for child in self._scroll.winfo_children():
                child.destroy()
            for e in self._entries:
                self._render_entry(e)
        else:
            self._render_entry(entry)

        if self._auto_scroll:
            self._scroll._parent_canvas.yview_moveto(1.0)  # noqa: SLF001

    def _render_entry(self, entry: LogEntry) -> None:
        if entry.is_warning:
            text = f"[{entry.timestamp}] Uyarı Tanımsız Mesaj ID: {entry.unknown_id}"
            color = COLORS["warning"]
            bg = COLORS["bg_tertiary"]
        elif entry.is_error:
            text = f"[{entry.timestamp}] Hata {entry.error_text or 'Çözümlenemeyen mesaj'}"
            color = COLORS["error"]
            bg = COLORS["bg_tertiary"]
        else:
            auto_tag = " [Otomatik]" if entry.is_auto else ""
            msg_label = get_message_short_label(entry.message_id or 0)
            text = f"[{entry.timestamp}] {entry.direction} {msg_label}{auto_tag}"
            if entry.direction == "Transmit":
                color = COLORS["accent_secondary"]
                bg = COLORS["transmit_bg"]
            else:
                color = COLORS["success"]
                bg = COLORS["receive_bg"]

        btn = ctk.CTkButton(
            self._scroll,
            text=text,
            font=FONT_MONO,
            fg_color=bg,
            hover_color=COLORS["bg_hover"],
            text_color=color,
            anchor="w",
            height=28,
            corner_radius=4,
            command=lambda e=entry: self._select(e),
        )
        btn.pack(fill="x", pady=1, padx=2)

    def _select(self, entry: LogEntry) -> None:
        if self._on_select:
            self._on_select(entry)

    def clear(self) -> None:
        self._entries.clear()
        for child in self._scroll.winfo_children():
            child.destroy()
