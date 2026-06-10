"""Reusable modern UI components."""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import COLORS, FONT_HEADING, FONT_SMALL, RADIUS, style_card


class Card(ctk.CTkFrame):
    """Elevated card container with optional title."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        title: str | None = None,
        subtitle: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, **kwargs)
        style_card(self)

        if title:
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.pack(fill="x", padx=16, pady=(14, 4))
            ctk.CTkLabel(
                header,
                text=title,
                font=FONT_HEADING,
                text_color=COLORS["text_primary"],
                anchor="w",
            ).pack(side="left")
            if subtitle:
                ctk.CTkLabel(
                    header,
                    text=subtitle,
                    font=FONT_SMALL,
                    text_color=COLORS["text_tertiary"],
                    anchor="w",
                ).pack(side="left", padx=(10, 0))

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=16, pady=(4, 14))


class SegmentedControl(ctk.CTkFrame):
    """Two-option segmented selector."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        options: list[tuple[str, int]],
        on_change: object,
        initial: int = 1,
    ) -> None:
        super().__init__(master, fg_color=COLORS["bg_input"], corner_radius=RADIUS["md"])
        self._buttons: dict[int, ctk.CTkButton] = {}
        self._selected = initial
        self._on_change = on_change

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=3, pady=3)

        for label, value in options:
            btn = ctk.CTkButton(
                inner,
                text=label,
                width=110,
                height=30,
                corner_radius=RADIUS["sm"],
                fg_color=COLORS["accent_primary_dim"] if value == initial else "transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["bg_primary"] if value == initial else COLORS["text_secondary"],
                command=lambda v=value: self.select(v),
            )
            btn.pack(side="left", padx=2)
            self._buttons[value] = btn

    def select(self, value: int) -> None:
        self._selected = value
        for v, btn in self._buttons.items():
            active = v == value
            btn.configure(
                fg_color=COLORS["accent_primary_dim"] if active else "transparent",
                text_color=COLORS["bg_primary"] if active else COLORS["text_secondary"],
            )
        if self._on_change:
            self._on_change(value)

    @property
    def selected(self) -> int:
        return self._selected
