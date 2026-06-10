"""Toast notification system."""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import COLORS, FONT_SMALL, RADIUS

TOAST_COLORS = {
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "error": COLORS["error"],
    "info": COLORS["info"],
}


class ToastManager:
    """Compact floating toasts — max 3 visible, deduplicated."""

    TOAST_WIDTH = 220
    TOAST_HEIGHT = 34
    TOAST_GAP = 4
    MARGIN = 12
    MAX_VISIBLE = 3
    DEFAULT_DURATION_MS = 2200

    def __init__(self, parent: ctk.CTk) -> None:
        self._parent = parent
        self._toasts: list[ctk.CTkToplevel] = []
        self._last_message = ""
        self._parent.bind("<Configure>", self._reposition_all, add="+")

    def show(self, message: str, toast_type: str = "info", duration_ms: int | None = None) -> None:
        """Show a compact toast; skip duplicate consecutive messages."""
        if message == self._last_message and self._toasts:
            return
        self._last_message = message

        while len(self._toasts) >= self.MAX_VISIBLE:
            self._dismiss(self._toasts[0])

        duration = duration_ms or self.DEFAULT_DURATION_MS
        color = TOAST_COLORS.get(toast_type, COLORS["info"])

        toast = ctk.CTkToplevel(self._parent)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(fg_color=COLORS["bg_elevated"])

        border = ctk.CTkFrame(
            toast,
            fg_color=COLORS["bg_elevated"],
            border_color=color,
            border_width=1,
            corner_radius=RADIUS["sm"],
        )
        border.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(border, fg_color="transparent")
        inner.pack(padx=8, pady=5)

        display = message if len(message) <= 42 else message[:39] + "…"
        ctk.CTkLabel(
            inner,
            text=display,
            font=FONT_SMALL,
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        ctk.CTkButton(
            inner,
            text="×",
            width=18,
            height=18,
            font=FONT_SMALL,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            command=lambda: self._dismiss(toast),
        ).pack(side="right", padx=(6, 0))

        self._toasts.append(toast)
        self._reposition_all()
        self._parent.after(duration, lambda: self._dismiss(toast))

    def _dismiss(self, toast: ctk.CTkToplevel) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
            try:
                toast.destroy()
            except Exception:
                pass
            self._reposition_all()

    def _reposition_all(self, _event: object | None = None) -> None:
        try:
            parent_w = self._parent.winfo_width()
            x_base = self._parent.winfo_x() + parent_w - self.TOAST_WIDTH - self.MARGIN
            y = self._parent.winfo_y() + self.MARGIN + 48
        except Exception:
            return
        for toast in self._toasts:
            try:
                toast.geometry(
                    f"{self.TOAST_WIDTH}x{self.TOAST_HEIGHT}+{x_base}+{y}"
                )
                y += self.TOAST_HEIGHT + self.TOAST_GAP
            except Exception:
                pass
