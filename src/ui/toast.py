"""Toast notification system."""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import COLORS, FONT_BODY, FONT_SMALL

TOAST_COLORS = {
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "error": COLORS["error"],
    "info": COLORS["accent_secondary"],
}


class ToastManager:
    """Manages stacked toast notifications in the top-right corner."""

    def __init__(self, parent: ctk.CTk) -> None:
        self._parent = parent
        self._toasts: list[ctk.CTkFrame] = []
        self._container = ctk.CTkFrame(parent, fg_color="transparent")
        self._container.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=16)

    def show(self, message: str, toast_type: str = "info", duration_ms: int = 3000) -> None:
        """Show a toast notification."""
        color = TOAST_COLORS.get(toast_type, COLORS["accent_secondary"])
        toast = ctk.CTkFrame(
            self._container,
            fg_color=COLORS["bg_tertiary"],
            border_color=color,
            border_width=2,
            corner_radius=8,
        )
        inner = ctk.CTkFrame(toast, fg_color="transparent")
        inner.pack(padx=12, pady=8)

        label = ctk.CTkLabel(
            inner,
            text=message,
            font=FONT_BODY,
            text_color=COLORS["text_primary"],
            wraplength=280,
        )
        label.pack(side="left", padx=(0, 8))

        close_btn = ctk.CTkButton(
            inner,
            text="✕",
            width=24,
            height=24,
            font=FONT_SMALL,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            command=lambda: self._dismiss(toast),
        )
        close_btn.pack(side="right")

        toast.pack(pady=4, anchor="e")
        self._toasts.append(toast)
        self._parent.after(duration_ms, lambda: self._dismiss(toast))

    def _dismiss(self, toast: ctk.CTkFrame) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
            toast.destroy()
