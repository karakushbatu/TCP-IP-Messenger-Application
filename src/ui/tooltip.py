"""Hover tooltips for CustomTkinter widgets."""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import COLORS, FONT_SMALL, RADIUS


class ToolTip:
    """Small floating hint shown after mouse hover."""

    def __init__(
        self,
        widget: ctk.CTkBaseClass,
        text: str,
        delay_ms: int = 450,
    ) -> None:
        self._widget = widget
        self._text = text
        self._delay_ms = delay_ms
        self._tip: ctk.CTkToplevel | None = None
        self._after_id: str | None = None
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")

    def update_text(self, text: str) -> None:
        self._text = text

    def _on_enter(self, _event: object) -> None:
        self._cancel()
        self._after_id = self._widget.after(self._delay_ms, self._show)

    def _on_leave(self, _event: object) -> None:
        self._cancel()
        self._hide()

    def _cancel(self) -> None:
        if self._after_id is not None:
            try:
                self._widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self) -> None:
        self._after_id = None
        if not self._text.strip():
            return
        self._hide()
        x = self._widget.winfo_rootx() + 12
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 6

        tip = ctk.CTkToplevel(self._widget)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{x}+{y}")
        tip.attributes("-topmost", True)

        frame = ctk.CTkFrame(
            tip,
            fg_color=COLORS["bg_elevated"],
            border_color=COLORS["border_subtle"],
            border_width=1,
            corner_radius=RADIUS["sm"],
        )
        frame.pack()

        ctk.CTkLabel(
            frame,
            text=self._text,
            font=FONT_SMALL,
            text_color=COLORS["text_primary"],
            wraplength=300,
            justify="left",
        ).pack(padx=10, pady=8)

        self._tip = tip

    def _hide(self) -> None:
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None
