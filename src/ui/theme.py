"""Design tokens and theme configuration."""

import customtkinter as ctk

COLORS = {
    "bg_primary": "#0F1419",
    "bg_secondary": "#1A2332",
    "bg_tertiary": "#243042",
    "bg_hover": "#2D3B4E",
    "accent_primary": "#00A88E",
    "accent_secondary": "#3B82F6",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_tertiary": "#64748B",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "border": "#334155",
    "transmit_bg": "#1E293B",
    "receive_bg": "#0F2922",
}

FONT_HEADING = ("Segoe UI", 16, "bold")
FONT_SUBHEADING = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 13)
FONT_SMALL = ("Segoe UI", 12)
FONT_MONO = ("Consolas", 12)


def apply_theme() -> None:
    """Apply global CustomTkinter theme settings."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
