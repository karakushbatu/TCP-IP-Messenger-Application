"""Periodic message sending panel."""

from __future__ import annotations

import threading
import time
from typing import Callable

import customtkinter as ctk

from src.protocol.messages import Message
from src.protocol.validator import build_message
from src.ui.theme import COLORS, FONT_BODY, FONT_SMALL
from src.utils.defaults import QUICK_FILL_MESSAGE_1, QUICK_FILL_MESSAGE_2


class PeriodicSender:
    """Background periodic message sender."""

    def __init__(
        self,
        message_id: int,
        get_form_data: Callable[[int], dict[str, object]],
        send_callback: Callable[[Message], None],
        is_connected: Callable[[], bool],
    ) -> None:
        self.message_id = message_id
        self._get_form_data = get_form_data
        self._send_callback = send_callback
        self._is_connected = is_connected
        self._interval_ms = 100 if message_id == 1 else 500
        self._running = False
        self._thread: threading.Thread | None = None
        self._sent_count = 0
        self._start_time: float = 0.0
        self._on_update: Callable[[int, float], None] | None = None

    def set_update_callback(self, callback: Callable[[int, float], None]) -> None:
        self._on_update = callback

    @property
    def sent_count(self) -> int:
        return self._sent_count

    @property
    def elapsed(self) -> float:
        if self._start_time == 0:
            return 0.0
        return time.monotonic() - self._start_time

    def start(self, interval_ms: int) -> None:
        self._interval_ms = max(50, min(10000, interval_ms))
        if self._running:
            return
        self._running = True
        self._start_time = time.monotonic()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            if self._is_connected():
                try:
                    data = self._get_form_data(self.message_id)
                    try:
                        msg = build_message(self.message_id, data)
                    except ValueError:
                        defaults = (
                            QUICK_FILL_MESSAGE_1
                            if self.message_id == 1
                            else QUICK_FILL_MESSAGE_2
                        )
                        msg = build_message(self.message_id, defaults)
                    self._send_callback(msg)
                    self._sent_count += 1
                    if self._on_update:
                        self._on_update(self._sent_count, self.elapsed)
                except Exception:
                    pass
            time.sleep(self._interval_ms / 1000.0)


class PeriodicPanel(ctk.CTkFrame):
    """Collapsible periodic sending controls."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        get_form_data: Callable[[int], dict[str, object]],
        send_callback: Callable[[Message], None],
        is_connected: Callable[[], bool],
    ) -> None:
        super().__init__(master, fg_color=COLORS["bg_secondary"], corner_radius=8)
        self._get_form_data = get_form_data
        self._send_callback = send_callback
        self._is_connected = is_connected
        self._expanded = True
        self._senders: dict[int, PeriodicSender] = {}
        self._indicators: dict[int, ctk.CTkLabel] = {}
        self._counters: dict[int, ctk.CTkLabel] = {}
        self._elapsed_labels: dict[int, ctk.CTkLabel] = {}
        self._switches: dict[int, ctk.CTkSwitch] = {}
        self._interval_entries: dict[int, ctk.CTkEntry] = {}

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(8, 4))

        self._toggle_btn = ctk.CTkButton(
            header_row,
            text="▼ Periyodik Gönderim",
            font=("Segoe UI", 14, "bold"),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            anchor="w",
            command=self._toggle,
        )
        self._toggle_btn.pack(side="left")

        stop_all = ctk.CTkButton(
            header_row,
            text="Tümünü Durdur",
            width=120,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["bg_hover"],
            command=self.stop_all,
        )
        stop_all.pack(side="right")

        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="x", padx=12, pady=(0, 8))

        for msg_id, default_ms in [(1, 100), (2, 500)]:
            self._build_row(msg_id, default_ms)

    def _build_row(self, msg_id: int, default_ms: int) -> None:
        row = ctk.CTkFrame(self._content, fg_color=COLORS["bg_tertiary"], corner_radius=6)
        row.pack(fill="x", pady=3)

        indicator = ctk.CTkLabel(row, text="●", font=FONT_BODY, text_color=COLORS["text_tertiary"])
        indicator.pack(side="left", padx=(8, 4))

        ctk.CTkLabel(
            row,
            text=f"Mesaj {msg_id}",
            font=FONT_BODY,
            text_color=COLORS["text_primary"],
            width=70,
        ).pack(side="left")

        switch = ctk.CTkSwitch(
            row,
            text="",
            width=40,
            command=lambda mid=msg_id: self._on_toggle(mid),
        )
        switch.pack(side="left", padx=4)

        ctk.CTkLabel(
            row,
            text="Aralık (ms):",
            font=FONT_SMALL,
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(8, 2))
        entry = ctk.CTkEntry(row, width=70)
        entry.insert(0, str(default_ms))
        entry.pack(side="left")

        counter = ctk.CTkLabel(
            row, text="Gönderilen: 0", font=FONT_SMALL, text_color=COLORS["text_secondary"]
        )
        counter.pack(side="left", padx=(12, 4))

        elapsed = ctk.CTkLabel(
            row, text="Süre: 0.0s", font=FONT_SMALL, text_color=COLORS["text_tertiary"]
        )
        elapsed.pack(side="left")

        sender = PeriodicSender(
            msg_id, self._get_form_data, self._send_callback, self._is_connected
        )

        def update(count: int, elapsed_s: float, mid: int = msg_id) -> None:
            self.after(0, lambda: self._update_ui(mid, count, elapsed_s))

        sender.set_update_callback(update)

        self._senders[msg_id] = sender
        self._indicators[msg_id] = indicator
        self._counters[msg_id] = counter
        self._elapsed_labels[msg_id] = elapsed
        self._switches[msg_id] = switch
        self._interval_entries[msg_id] = entry

    def _update_ui(self, msg_id: int, count: int, elapsed_s: float) -> None:
        self._counters[msg_id].configure(text=f"Gönderilen: {count}")
        self._elapsed_labels[msg_id].configure(text=f"Süre: {elapsed_s:.1f}s")

    def _on_toggle(self, msg_id: int) -> None:
        switch = self._switches[msg_id]
        sender = self._senders[msg_id]
        if switch.get():
            try:
                interval = int(self._interval_entries[msg_id].get())
            except ValueError:
                interval = 100 if msg_id == 1 else 500
            sender.start(interval)
            self._indicators[msg_id].configure(text_color=COLORS["accent_primary"])
        else:
            sender.stop()
            self._indicators[msg_id].configure(text_color=COLORS["text_tertiary"])

    def stop_all(self) -> None:
        for msg_id, sender in self._senders.items():
            sender.stop()
            self._switches[msg_id].deselect()
            self._indicators[msg_id].configure(text_color=COLORS["text_tertiary"])

    def on_disconnect(self) -> None:
        self.stop_all()

    def _toggle(self) -> None:
        self._expanded = not self._expanded
        if self._expanded:
            self._content.pack(fill="x", padx=12, pady=(0, 8))
            self._toggle_btn.configure(text="▼ Periyodik Gönderim")
        else:
            self._content.pack_forget()
            self._toggle_btn.configure(text="▶ Periyodik Gönderim")
