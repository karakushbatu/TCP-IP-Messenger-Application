"""Per-instance main panel combining all UI components."""

from __future__ import annotations

import struct
from typing import Callable

import customtkinter as ctk

from src.network.handler import (
    NetworkEvent,
    ReceivedMessageInfo,
    SentMessageInfo,
)
from src.protocol.messages import Message
from src.protocol.serializer import frame_payload
from src.protocol.validator import build_message
from src.ui.compose_form import ComposeForm
from src.ui.message_log import LogEntry, MessageLog
from src.ui.periodic_panel import PeriodicPanel
from src.ui.status_bar import StatusBar
from src.ui.theme import COLORS, FONT_SMALL
from src.utils.timestamp import format_timestamp


class InstancePanel(ctk.CTkFrame):
    """Reusable per-instance UI panel for server or client."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        title: str = "Instance",
        on_log_select: Callable[[LogEntry], None] | None = None,
        on_toast: Callable[[str, str], None] | None = None,
    ) -> None:
        super().__init__(master, fg_color=COLORS["bg_primary"], corner_radius=0)
        self._on_log_select = on_log_select
        self._on_toast = on_toast
        self._send_fn: Callable[[Message, bool], bool] | None = None
        self._send_raw_fn: Callable[[bytes], bool] | None = None
        self._is_connected_fn: Callable[[], bool] = lambda: False
        self._auto_response_var = ctk.BooleanVar(value=True)

        self.status_bar = StatusBar(self, title=title)
        self.status_bar.pack(fill="x", padx=12, pady=(8, 4))

        conn_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=8)
        conn_frame.pack(fill="x", padx=12, pady=4)

        self._conn_inner = ctk.CTkFrame(conn_frame, fg_color="transparent")
        self._conn_inner.pack(fill="x", padx=12, pady=8)

        auto_frame = ctk.CTkFrame(self, fg_color="transparent")
        auto_frame.pack(fill="x", padx=12, pady=2)

        self._auto_switch = ctk.CTkSwitch(
            auto_frame,
            text="Otomatik Yanıt",
            variable=self._auto_response_var,
            command=self._on_auto_toggle,
        )
        self._auto_switch.pack(side="left")

        self.compose_form = ComposeForm(self)
        self.compose_form.pack(fill="x", padx=12, pady=4)
        self.compose_form.set_send_callback(self._on_send)

        self.message_log = MessageLog(self, on_select=self._on_select_log)
        self.message_log.pack(fill="both", expand=True, padx=12, pady=4)

        self.periodic_panel = PeriodicPanel(
            self,
            get_form_data=self._get_form_data_for_type,
            send_callback=lambda msg: self._send_message(msg, is_auto=False),
            is_connected=self._is_connected_fn,
        )
        self.periodic_panel.pack(fill="x", padx=12, pady=(0, 8))

        test_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=8)
        test_frame.pack(fill="x", padx=12, pady=(0, 8))

        test_header = ctk.CTkButton(
            test_frame,
            text="▶ Test Araçları",
            font=FONT_SMALL,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            anchor="w",
            command=self._toggle_test,
        )
        test_header.pack(anchor="w", padx=8, pady=4)

        self._test_content = ctk.CTkFrame(test_frame, fg_color="transparent")
        self._test_visible = False

        ctk.CTkButton(
            self._test_content,
            text="Tanımsız Mesaj Gönder",
            fg_color=COLORS["warning"],
            hover_color="#D97706",
            command=self._send_unknown,
        ).pack(side="left", padx=8, pady=8)

        ctk.CTkButton(
            self._test_content,
            text="Bozuk Mesaj Gönder",
            fg_color=COLORS["error"],
            hover_color="#DC2626",
            command=self._send_corrupt,
        ).pack(side="left", padx=8, pady=8)

    def set_title(self, title: str) -> None:
        self.status_bar.set_title(title)

    def set_status(self, status: str) -> None:
        self.status_bar.set_status(status)

    def set_send_callback(self, fn: Callable[[Message, bool], bool]) -> None:
        self._send_fn = fn

    def set_send_raw_callback(self, fn: Callable[[bytes], bool]) -> None:
        self._send_raw_fn = fn

    def set_connected_callback(self, fn: Callable[[], bool]) -> None:
        self._is_connected_fn = fn
        self.periodic_panel._is_connected = fn  # noqa: SLF001

    def set_auto_response_enabled(self, enabled: bool) -> None:
        self._auto_response_var.set(enabled)

    def get_auto_response_enabled(self) -> bool:
        return self._auto_response_var.get()

    def build_connection_controls(
        self,
        mode: str,
        on_start_server: Callable[[int], None] | None = None,
        on_stop_server: Callable[[], None] | None = None,
        on_connect: Callable[[str, int], None] | None = None,
        on_disconnect: Callable[[], None] | None = None,
    ) -> None:
        """Build connection control widgets based on server/client mode."""
        for child in self._conn_inner.winfo_children():
            child.destroy()

        if mode == "server":
            ctk.CTkLabel(
                self._conn_inner,
                text="Port:",
                text_color=COLORS["text_secondary"],
            ).pack(side="left", padx=(0, 4))
            port_entry = ctk.CTkEntry(self._conn_inner, width=80)
            port_entry.insert(0, "8080")
            port_entry.pack(side="left", padx=(0, 8))

            def start() -> None:
                try:
                    port = int(port_entry.get())
                    if on_start_server:
                        on_start_server(port)
                except ValueError:
                    if self._on_toast:
                        self._on_toast("Geçersiz port numarası", "error")

            ctk.CTkButton(
                self._conn_inner,
                text="Sunucuyu Başlat",
                fg_color=COLORS["accent_primary"],
                command=start,
            ).pack(side="left", padx=(0, 4))

            if on_stop_server:
                ctk.CTkButton(
                    self._conn_inner,
                    text="Durdur",
                    fg_color=COLORS["bg_tertiary"],
                    command=on_stop_server,
                ).pack(side="left")

        else:
            ctk.CTkLabel(
                self._conn_inner,
                text="IP:",
                text_color=COLORS["text_secondary"],
            ).pack(side="left", padx=(0, 4))
            ip_entry = ctk.CTkEntry(self._conn_inner, width=120)
            ip_entry.insert(0, "127.0.0.1")
            ip_entry.pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                self._conn_inner,
                text="Port:",
                text_color=COLORS["text_secondary"],
            ).pack(side="left", padx=(0, 4))
            port_entry = ctk.CTkEntry(self._conn_inner, width=80)
            port_entry.insert(0, "8080")
            port_entry.pack(side="left", padx=(0, 8))

            def connect() -> None:
                try:
                    port = int(port_entry.get())
                    if on_connect:
                        on_connect(ip_entry.get(), port)
                except ValueError:
                    if self._on_toast:
                        self._on_toast("Geçersiz port numarası", "error")

            ctk.CTkButton(
                self._conn_inner,
                text="Bağlan",
                fg_color=COLORS["accent_primary"],
                command=connect,
            ).pack(side="left", padx=(0, 4))

            if on_disconnect:
                ctk.CTkButton(
                    self._conn_inner,
                    text="Bağlantıyı Kes",
                    fg_color=COLORS["bg_tertiary"],
                    command=on_disconnect,
                ).pack(side="left")

    def handle_network_event(self, event: NetworkEvent) -> None:
        """Process a network event and update UI."""
        ts = format_timestamp(event.timestamp)

        if event.type == "connected":
            if self._on_toast:
                self._on_toast("Bağlantı kuruldu", "success")
        elif event.type == "disconnected":
            self.periodic_panel.on_disconnect()
            if self._on_toast:
                self._on_toast("Bağlantı kesildi", "warning")
        elif event.type == "message_sent":
            info = event.payload
            if isinstance(info, SentMessageInfo):
                self.message_log.add_entry(
                    LogEntry(
                        timestamp=ts,
                        direction="Transmit",
                        message_id=info.message.message_id,
                        is_auto=info.is_auto,
                        message=info.message,
                        raw_timestamp=event.timestamp,
                    )
                )
                if info.is_auto:
                    label = f"Mesaj {info.message.message_id}"
                    if self._on_toast:
                        self._on_toast(f"Otomatik yanıt gönderildi: {label}", "info")
                else:
                    if self._on_toast:
                        self._on_toast("Mesaj gönderildi", "success")
        elif event.type == "message_received":
            info = event.payload
            if isinstance(info, ReceivedMessageInfo) and info.message:
                self.message_log.add_entry(
                    LogEntry(
                        timestamp=ts,
                        direction="Receive",
                        message_id=info.message.message_id,
                        message=info.message,
                        raw_timestamp=event.timestamp,
                    )
                )
                if self._on_toast:
                    self._on_toast("Mesaj alındı", "info")
        elif event.type == "unknown_message":
            info = event.payload
            if isinstance(info, ReceivedMessageInfo):
                self.message_log.add_entry(
                    LogEntry(
                        timestamp=ts,
                        direction="Receive",
                        message_id=None,
                        is_warning=True,
                        unknown_id=info.unknown_id,
                        raw_timestamp=event.timestamp,
                    )
                )
                if self._on_toast:
                    self._on_toast("Tanımlı olmayan mesaj alındı", "warning")
        elif event.type == "protocol_error":
            info = event.payload
            if isinstance(info, ReceivedMessageInfo):
                self.message_log.add_entry(
                    LogEntry(
                        timestamp=ts,
                        direction="Receive",
                        message_id=None,
                        is_error=True,
                        error_text="Çözümlenemeyen mesaj",
                        raw_timestamp=event.timestamp,
                    )
                )
                if self._on_toast:
                    self._on_toast("Hatalı mesaj alındı — çözümlenemedi", "error")

    def _on_send(self) -> None:
        if not self.compose_form.is_valid():
            return
        data = self.compose_form.get_form_data()
        try:
            msg = build_message(self.compose_form.get_message_id(), data)
            self._send_message(msg, is_auto=False)
        except ValueError as exc:
            if self._on_toast:
                self._on_toast(str(exc), "error")

    def _send_message(self, message: Message, is_auto: bool = False) -> None:
        if self._send_fn:
            self._send_fn(message, is_auto)

    def _get_form_data_for_type(self, message_id: int) -> dict[str, object]:
        current = self.compose_form.get_message_id()
        if current == message_id:
            return self.compose_form.get_form_data()
        from src.utils.defaults import QUICK_FILL_MESSAGE_1, QUICK_FILL_MESSAGE_2

        return QUICK_FILL_MESSAGE_1 if message_id == 1 else QUICK_FILL_MESSAGE_2

    def _on_select_log(self, entry: LogEntry) -> None:
        if self._on_log_select:
            self._on_log_select(entry)

    def _on_auto_toggle(self) -> None:
        pass  # Handled by instance

    def _toggle_test(self) -> None:
        self._test_visible = not self._test_visible
        if self._test_visible:
            self._test_content.pack(fill="x")
        else:
            self._test_content.pack_forget()

    def _send_unknown(self) -> None:
        if not self._send_raw_fn:
            return
        payload = struct.pack("!i", 99)
        framed = frame_payload(payload)
        self._send_raw_fn(framed)

    def _send_corrupt(self) -> None:
        if not self._send_raw_fn:
            return
        payload = struct.pack("!i", 1)[:2]
        framed = frame_payload(payload)
        self._send_raw_fn(framed)
