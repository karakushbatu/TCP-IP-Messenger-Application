"""Shared message detail panel."""

from __future__ import annotations

import sys

import customtkinter as ctk

from src.protocol.messages import Message, get_message_short_label, message_to_dict
from src.ui.theme import (
    COLORS,
    DETAIL_COLLAPSED_HEIGHT,
    DETAIL_PANEL_HEIGHT,
    FONT_BODY,
    FONT_HEADING,
    FONT_MONO,
    FONT_SMALL,
    RADIUS,
)


class DetailPanel(ctk.CTkFrame):
    """Collapsible bottom panel showing detailed message information."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        *,
        start_collapsed: bool | None = None,
    ) -> None:
        if start_collapsed is None:
            start_collapsed = sys.platform == "darwin"

        self._expanded = not start_collapsed
        initial_height = DETAIL_COLLAPSED_HEIGHT if start_collapsed else DETAIL_PANEL_HEIGHT

        super().__init__(
            master,
            fg_color=COLORS["bg_secondary"],
            corner_radius=RADIUS["lg"],
            border_color=COLORS["border_subtle"],
            border_width=1,
            height=initial_height,
        )
        self.grid_propagate(False)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(8, 0))

        self._toggle_btn = ctk.CTkButton(
            header,
            text="▼ Message Detail" if self._expanded else "▶ Message Detail",
            font=FONT_HEADING,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
            anchor="w",
            height=28,
            command=self.toggle,
        )
        self._toggle_btn.pack(side="left")

        ctk.CTkLabel(
            header,
            text="Click a log entry",
            font=FONT_SMALL,
            text_color=COLORS["text_tertiary"],
        ).pack(side="left", padx=(10, 0))

        self._content = ctk.CTkFrame(self, fg_color="transparent")

        self._meta_label = ctk.CTkLabel(
            self._content,
            text="No message selected",
            font=FONT_MONO,
            text_color=COLORS["text_tertiary"],
            anchor="w",
        )
        self._meta_label.pack(anchor="w", padx=14, pady=(4, 4))

        self._scroll = ctk.CTkScrollableFrame(
            self._content,
            fg_color=COLORS["bg_input"],
            corner_radius=RADIUS["sm"],
            height=72,
            scrollbar_button_color=COLORS["bg_elevated"],
        )
        self._scroll.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        if self._expanded:
            self._content.pack(fill="both", expand=True)

    def toggle(self) -> None:
        """Expand or collapse the detail body."""
        self._expanded = not self._expanded
        if self._expanded:
            self._content.pack(fill="both", expand=True)
            self.configure(height=DETAIL_PANEL_HEIGHT)
            self._toggle_btn.configure(text="▼ Message Detail")
        else:
            self._content.pack_forget()
            self.configure(height=DETAIL_COLLAPSED_HEIGHT)
            self._toggle_btn.configure(text="▶ Message Detail")

    def clear(self) -> None:
        self._meta_label.configure(text="No message selected")
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
        if not self._expanded:
            self.toggle()

        for child in self._scroll.winfo_children():
            child.destroy()

        auto_tag = " [Auto]" if is_auto else ""

        if unknown_id is not None:
            self._meta_label.configure(
                text=f"[{timestamp}] {direction} — Unknown Message ID: {unknown_id}"
            )
            ctk.CTkLabel(
                self._scroll,
                text="⚠ Unknown message received",
                font=FONT_BODY,
                text_color=COLORS["warning"],
                anchor="w",
            ).pack(anchor="w", pady=2, padx=4)
            return

        if error_text:
            self._meta_label.configure(text=f"[{timestamp}] {direction} — Error")
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
