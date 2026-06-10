"""Welcome screen with quick-start demo options."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from src.instance_manager import DemoMode
from src.ui.theme import COLORS, FONT_BODY, FONT_HEADING

DemoCallback = Callable[[DemoMode], None]


class WelcomeScreen(ctk.CTkFrame):
    """Initial welcome screen with demo mode selection."""

    def __init__(self, master: ctk.CTkBaseClass, on_select: DemoCallback) -> None:
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self._on_select = on_select

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container,
            text="TCP Tactical Messenger",
            font=("Segoe UI", 28, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            container,
            text=(
                "TCP/IP üzerinden ikili mesajlaşma, otomatik yanıt "
                "ve periyodik gönderim demo aracı"
            ),
            font=FONT_BODY,
            text_color=COLORS["text_secondary"],
            wraplength=600,
        ).pack(pady=(0, 32))

        cards_frame = ctk.CTkFrame(container, fg_color="transparent")
        cards_frame.pack()

        demos: list[tuple[str, str, DemoMode]] = [
            (
                "Sunucu + İstemci (Otomatik Bağlan)",
                "Sunucu ve istemciyi otomatik olarak başlatır ve bağlar",
                "auto",
            ),
            (
                "Sunucu + İstemci (Manuel)",
                "Sunucu ve istemci panellerini manuel bağlantı için açar",
                "manual",
            ),
            ("Tek Sunucu", "Yalnızca sunucu modunda başlat", "server_only"),
            ("Tek İstemci", "Yalnızca istemci modunda başlat", "client_only"),
        ]

        for i, (title, desc, mode) in enumerate(demos):
            card = self._create_card(cards_frame, title, desc, mode, highlight=(i == 0))
            card.grid(row=i // 2, column=i % 2, padx=12, pady=12, sticky="nsew")

    def _create_card(
        self,
        parent: ctk.CTkFrame,
        title: str,
        description: str,
        mode: DemoMode,
        highlight: bool = False,
    ) -> ctk.CTkFrame:
        border_color = COLORS["accent_primary"] if highlight else COLORS["border"]
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_secondary"],
            border_color=border_color,
            border_width=2 if highlight else 1,
            corner_radius=12,
            width=320,
            height=140,
        )
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=FONT_HEADING,
            text_color=COLORS["accent_primary"] if highlight else COLORS["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        ctk.CTkLabel(
            card,
            text=description,
            font=FONT_BODY,
            text_color=COLORS["text_secondary"],
            wraplength=280,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 12))

        btn_color = COLORS["accent_primary"] if highlight else COLORS["bg_tertiary"]
        ctk.CTkButton(
            card,
            text="Başlat",
            fg_color=btn_color,
            hover_color=COLORS["bg_hover"] if not highlight else "#008F7A",
            command=lambda m=mode: self._on_select(m),
        ).pack(anchor="w", padx=16, pady=(0, 12))

        return card
