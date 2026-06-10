"""Periodic message sending panel."""

from __future__ import annotations

import threading
import time
from typing import Callable

import customtkinter as ctk

from src.protocol.messages import Message
from src.protocol.validator import build_message
from src.ui.theme import COLORS, FONT_SMALL
from src.utils.defaults import QUICK_FILL_MESSAGE_1, QUICK_FILL_MESSAGE_2

EXPANDED_BODY_HEIGHT = 68


class PeriodicSender:
    """Background periodic message sender."""

    def __init__(
        self,
        message_id: int,
        get_form_data: Callable[[int], dict[str, object]],
        send_callback: Callable[[Message], bool],
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
                    if self._send_callback(msg):
                        self._sent_count += 1
                        if self._on_update:
                            self._on_update(
                                self._sent_count,
                                time.monotonic() - self._start_time,
                            )
                except Exception:
                    pass
            time.sleep(self._interval_ms / 1000.0)


class PeriodicPanel(ctk.CTkFrame):
    """Collapsible periodic controls — fixed height when expanded."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        get_form_data: Callable[[int], dict[str, object]],
        send_callback: Callable[[Message], bool],
        is_connected: Callable[[], bool],
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(master, fg_color=COLORS["bg_secondary"], corner_radius=8)
        self._get_form_data = get_form_data
        self._send_callback = send_callback
        self._is_connected = is_connected
        self._on_status = on_status
        self._expanded = False
        self._senders: dict[int, PeriodicSender] = {}
        self._indicators: dict[int, ctk.CTkLabel] = {}
        self._counters: dict[int, ctk.CTkLabel] = {}
        self._switches: dict[int, ctk.CTkSwitch] = {}
        self._interval_entries: dict[int, ctk.CTkEntry] = {}

        header_row = ctk.CTkFrame(self, fg_color="transparent", height=32)
        header_row.pack(fill="x", padx=8, pady=(4, 0))
        header_row.pack_propagate(False)

        self._toggle_btn = ctk.CTkButton(
            header_row,
            text="▶ Periodic Send",
            font=FONT_SMALL,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            anchor="w",
            command=self._toggle,
        )
        self._toggle_btn.pack(side="left", fill="y")

        ctk.CTkButton(
            header_row,
            text="Stop All",
            width=64,
            height=24,
            font=FONT_SMALL,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["bg_hover"],
            command=self.stop_all,
        ).pack(side="right", pady=4)

        self._body = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=EXPANDED_BODY_HEIGHT,
        )
        self._body.pack_propagate(False)

        inner = ctk.CTkFrame(self._body, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        for msg_id, default_ms in [(1, 100), (2, 500)]:
            self._build_row(inner, msg_id, default_ms)

    def _build_row(self, parent: ctk.CTkFrame, msg_id: int, default_ms: int) -> None:
        row = ctk.CTkFrame(parent, fg_color=COLORS["bg_tertiary"], corner_radius=4, height=28)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)

        indicator = ctk.CTkLabel(
            row, text="●", font=FONT_SMALL, text_color=COLORS["text_tertiary"], width=12
        )
        indicator.pack(side="left", padx=(6, 2))

        ctk.CTkLabel(
            row,
            text=f"M{msg_id}",
            font=FONT_SMALL,
            text_color=COLORS["text_primary"],
            width=24,
        ).pack(side="left")

        switch = ctk.CTkSwitch(
            row,
            text="",
            width=36,
            command=lambda mid=msg_id: self.after_idle(lambda: self._on_toggle(mid)),
        )
        switch.pack(side="left", padx=2)

        ctk.CTkLabel(
            row, text="ms", font=FONT_SMALL, text_color=COLORS["text_tertiary"], width=18
        ).pack(side="left")
        entry = ctk.CTkEntry(row, width=52, height=22)
        entry.insert(0, str(default_ms))
        entry.pack(side="left", padx=(0, 6))

        counter = ctk.CTkLabel(
            row, text="0 sent", font=FONT_SMALL, text_color=COLORS["text_secondary"]
        )
        counter.pack(side="left")

        sender = PeriodicSender(
            msg_id,
            self._get_form_data,
            self._send_callback,
            lambda: self._is_connected(),
        )
        sender.set_update_callback(
            lambda c, _e, mid=msg_id: self.after(0, lambda: counter.configure(text=f"{c} sent"))
        )

        self._senders[msg_id] = sender
        self._indicators[msg_id] = indicator
        self._counters[msg_id] = counter
        self._switches[msg_id] = switch
        self._interval_entries[msg_id] = entry

    def _on_toggle(self, msg_id: int) -> None:
        switch = self._switches[msg_id]
        sender = self._senders[msg_id]
        if int(switch.get()) == 1:
            if not self._is_connected():
                switch.deselect()
                if self._on_status:
                    self._on_status("Connect first to enable periodic sending")
                return
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
            self._body.pack(fill="x")
            self._toggle_btn.configure(text="▼ Periodic Send")
        else:
            self._body.pack_forget()
            self._toggle_btn.configure(text="▶ Periodic Send")
