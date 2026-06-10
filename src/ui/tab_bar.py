"""Browser-style tab bar."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

import customtkinter as ctk

from src.ui.theme import COLORS, FONT_SMALL, RADIUS, style_button_secondary

TabSelectCallback = Callable[[str], None]
TabCloseCallback = Callable[[str], None]
NewTabCallback = Callable[[], None]


class TabBar(ctk.CTkFrame):
    """Horizontal tab strip with close buttons, right-click menu, and new-instance action."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_select: TabSelectCallback,
        on_close: TabCloseCallback,
        on_new_tab: NewTabCallback,
    ) -> None:
        super().__init__(master, fg_color=COLORS["bg_secondary"], height=40, corner_radius=0)
        self.pack_propagate(False)
        self._on_select = on_select
        self._on_close = on_close
        self._on_new_tab = on_new_tab
        self._tabs_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._tabs_frame.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=6)
        self._tab_buttons: dict[str, ctk.CTkButton] = {}
        self._active_id: str | None = None

        new_btn = ctk.CTkButton(self, text="+ Instance", width=90, command=self._on_new_tab)
        style_button_secondary(new_btn)
        new_btn.pack(side="right", padx=(4, 10), pady=6)

    def _bind_context_menu(self, widget: ctk.CTkBaseClass, tab_id: str, closable: bool) -> None:
        if not closable:
            return

        def show_menu(event: tk.Event) -> None:
            menu = tk.Menu(widget, tearoff=0)
            menu.add_command(label="Sekmeyi Kapat", command=lambda: self._on_close(tab_id))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        widget.bind("<Button-3>", show_menu)

    def set_tabs(self, tabs: list[tuple[str, str, bool]], active_id: str) -> None:
        """Update tab buttons. Each tab: (id, title, closable)."""
        for child in self._tabs_frame.winfo_children():
            child.destroy()
        self._tab_buttons.clear()
        self._active_id = active_id

        for tab_id, title, closable in tabs:
            wrap = ctk.CTkFrame(self._tabs_frame, fg_color="transparent")
            wrap.pack(side="left", padx=(0, 4))

            is_active = tab_id == active_id
            btn = ctk.CTkButton(
                wrap,
                text=f"  {title}  ",
                height=28,
                font=FONT_SMALL,
                fg_color=COLORS["bg_elevated"] if is_active else "transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["accent_primary"] if is_active else COLORS["text_secondary"],
                corner_radius=RADIUS["sm"],
                command=lambda tid=tab_id: self._on_select(tid),
            )
            btn.pack(side="left")
            self._tab_buttons[tab_id] = btn
            self._bind_context_menu(btn, tab_id, closable)
            self._bind_context_menu(wrap, tab_id, closable)

            if closable:
                close = ctk.CTkButton(
                    wrap,
                    text="×",
                    width=22,
                    height=22,
                    font=FONT_SMALL,
                    fg_color="transparent",
                    hover_color=COLORS["error"],
                    command=lambda tid=tab_id: self._on_close(tid),
                )
                close.pack(side="left", padx=(2, 0))
                self._bind_context_menu(close, tab_id, closable)
