"""Welcome screen with quick-start demo options."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from src.app_info import APP_NAME, APP_TAGLINE
from src.instance_manager import DemoMode
from src.ui.theme import (
    COLORS,
    FONT_BODY,
    FONT_DISPLAY,
    FONT_HEADING,
    FONT_SMALL,
    RADIUS,
    style_button_primary,
    style_button_secondary,
)

DemoCallback = Callable[[DemoMode], None]


class WelcomeScreen(ctk.CTkScrollableFrame):
    """Initial welcome screen."""

    def __init__(self, master: ctk.CTkBaseClass, on_select: DemoCallback) -> None:
        super().__init__(
            master,
            fg_color=COLORS["bg_primary"],
            scrollbar_button_color=COLORS["bg_elevated"],
            scrollbar_button_hover_color=COLORS["bg_hover"],
        )
        self._on_select = on_select

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(
            inner,
            text=APP_NAME,
            font=FONT_DISPLAY,
            text_color=COLORS["text_primary"],
        ).pack(pady=(12, 4))

        ctk.CTkLabel(
            inner,
            text=APP_TAGLINE,
            font=FONT_SMALL,
            text_color=COLORS["accent_primary"],
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            inner,
            text=(
                "Binary messaging over TCP/IP with auto-response "
                "and periodic transmission demo."
            ),
            font=FONT_BODY,
            text_color=COLORS["text_secondary"],
            wraplength=640,
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            inner,
            text=(
                "Pick a mode to begin. Server + Client opens two side-by-side panels; "
                "single-side modes show one panel only."
            ),
            font=FONT_SMALL,
            text_color=COLORS["text_tertiary"],
            wraplength=640,
        ).pack(pady=(0, 24))

        cards = ctk.CTkFrame(inner, fg_color="transparent")
        cards.pack()
        cards.grid_columnconfigure(0, weight=1)
        cards.grid_columnconfigure(1, weight=1)

        demos: list[tuple[str, str, str, DemoMode, str]] = [
            (
                "Server + Client (Auto Connect)",
                "Recommended demo",
                "Server starts on :8080 and the client connects automatically. "
                "Start sending messages immediately.",
                "auto",
                "Recommended",
            ),
            (
                "Server + Client (Manual)",
                "Step-by-step connection",
                "Both panels open without a connection. Start the server on the left, "
                "then click Connect on the right.",
                "manual",
                "Manual",
            ),
            (
                "Server Only",
                "Listen only",
                "Another app or instance tab connects to this server.",
                "server_only",
                "Server",
            ),
            (
                "Client Only",
                "Connect only",
                "Connect to an external server by IP and port.",
                "client_only",
                "Client",
            ),
        ]

        for i, (title, subtitle, desc, mode, badge) in enumerate(demos):
            card = self._create_card(cards, title, subtitle, desc, mode, badge, highlight=(i == 0))
            card.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")

    def _create_card(
        self,
        parent: ctk.CTkFrame,
        title: str,
        subtitle: str,
        description: str,
        mode: DemoMode,
        badge: str,
        highlight: bool = False,
    ) -> ctk.CTkFrame:
        border_color = COLORS["accent_primary_dim"] if highlight else COLORS["border_subtle"]
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_secondary"],
            border_color=border_color,
            border_width=2 if highlight else 1,
            corner_radius=RADIUS["xl"],
            width=360,
            height=220,
        )
        card.pack_propagate(False)
        card.grid_propagate(False)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 4))

        ctk.CTkLabel(
            top,
            text=f"  {badge}  ",
            font=FONT_SMALL,
            text_color=COLORS["accent_primary"] if highlight else COLORS["text_tertiary"],
            fg_color=COLORS["accent_glow"] if highlight else COLORS["bg_input"],
            corner_radius=RADIUS["sm"],
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=subtitle,
            font=FONT_SMALL,
            text_color=COLORS["text_tertiary"],
        ).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            card,
            text=title,
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w", padx=18, pady=(4, 4))

        ctk.CTkLabel(
            card,
            text=description,
            font=FONT_BODY,
            text_color=COLORS["text_secondary"],
            wraplength=320,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 12))

        btn = ctk.CTkButton(
            card,
            text="Start →",
            width=120,
            command=lambda m=mode: self._on_select(m),
        )
        if highlight:
            style_button_primary(btn)
        else:
            style_button_secondary(btn)
        btn.pack(anchor="w", padx=18, pady=(0, 16))

        return card
