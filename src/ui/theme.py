"""Design tokens and theme configuration."""

import sys

import customtkinter as ctk

COLORS = {
    # Surfaces
    "bg_primary": "#090C10",
    "bg_secondary": "#111820",
    "bg_tertiary": "#1A2330",
    "bg_elevated": "#1E2938",
    "bg_hover": "#263244",
    "bg_input": "#0F1520",
    # Accents
    "accent_primary": "#22D3EE",
    "accent_primary_dim": "#0891B2",
    "accent_secondary": "#818CF8",
    "accent_glow": "#164E63",
    # Text
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_tertiary": "#64748B",
    "text_muted": "#475569",
    # Semantic
    "success": "#34D399",
    "warning": "#FBBF24",
    "error": "#F87171",
    "info": "#60A5FA",
    # Borders & logs
    "border": "#2A3544",
    "border_subtle": "#1F2937",
    "transmit_bg": "#172554",
    "receive_bg": "#052E16",
    "card_shadow": "#000000",
}

RADIUS = {
    "sm": 6,
    "md": 10,
    "lg": 14,
    "xl": 18,
}

FONT_DISPLAY = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 15, "bold")
FONT_SUBHEADING = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 13)
FONT_SMALL = ("Segoe UI", 11)
FONT_MONO = ("Cascadia Mono", 12)
FONT_MONO_SMALL = ("Cascadia Mono", 11)

# Layout tokens tuned for MacBook Retina viewports (dual-panel workspace).
DETAIL_PANEL_HEIGHT = 120 if sys.platform == "darwin" else 140
DETAIL_COLLAPSED_HEIGHT = 34
MESSAGE_LOG_HEIGHT = 110 if sys.platform == "darwin" else 140
COMPACT_WIDTH = 520


def platform_ui_scale() -> float:
    """CustomTkinter defaults to 2.0 on Retina Mac — too large for laptop layouts."""
    if sys.platform == "darwin":
        return 0.88
    return 1.0


def apply_theme() -> None:
    """Apply global CustomTkinter theme settings."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    scale = platform_ui_scale()
    ctk.set_widget_scaling(scale)
    ctk.set_window_scaling(scale)


def style_button_primary(button: ctk.CTkButton) -> None:
    button.configure(
        fg_color=COLORS["accent_primary_dim"],
        hover_color=COLORS["accent_primary"],
        text_color=COLORS["bg_primary"],
        corner_radius=RADIUS["md"],
        height=34,
        font=FONT_SUBHEADING,
    )


def style_button_secondary(button: ctk.CTkButton) -> None:
    button.configure(
        fg_color=COLORS["bg_elevated"],
        hover_color=COLORS["bg_hover"],
        border_color=COLORS["border"],
        border_width=1,
        text_color=COLORS["text_primary"],
        corner_radius=RADIUS["md"],
        height=34,
        font=FONT_BODY,
    )


def style_button_ghost(button: ctk.CTkButton) -> None:
    button.configure(
        fg_color="transparent",
        hover_color=COLORS["bg_hover"],
        text_color=COLORS["text_secondary"],
        corner_radius=RADIUS["sm"],
        height=32,
        font=FONT_BODY,
    )


def style_entry(entry: ctk.CTkEntry) -> None:
    entry.configure(
        fg_color=COLORS["bg_input"],
        border_color=COLORS["border"],
        text_color=COLORS["text_primary"],
        corner_radius=RADIUS["sm"],
        height=34,
        font=FONT_BODY,
    )


def style_card(frame: ctk.CTkFrame) -> None:
    frame.configure(
        fg_color=COLORS["bg_secondary"],
        border_color=COLORS["border_subtle"],
        border_width=1,
        corner_radius=RADIUS["lg"],
    )
