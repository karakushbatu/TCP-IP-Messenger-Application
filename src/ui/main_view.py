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
from src.ui.components import Card
from src.ui.compose_form import ComposeForm
from src.ui.message_log import LogEntry, MessageLog
from src.ui.periodic_panel import PeriodicPanel
from src.ui.status_bar import StatusBar
from src.ui.theme import (
    COLORS,
    FONT_SMALL,
    RADIUS,
    style_button_primary,
    style_button_secondary,
    style_entry,
)
from src.ui.tooltip import ToolTip
from src.utils.timestamp import format_timestamp

AUTO_REPLY_TOOLTIP = (
    "Protocol demo: incoming Message 1 triggers automatic Message 2, "
    "and Message 2 triggers Message 1. Disable for manual testing; "
    "loop protection prevents ping-pong cycles."
)

TOOLS_FOOTER_HEIGHT = 168


class InstancePanel(ctk.CTkFrame):
    """Reusable per-instance UI panel for server or client."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        title: str = "Instance",
        on_log_select: Callable[[LogEntry], None] | None = None,
        on_toast: Callable[[str, str], None] | None = None,
    ) -> None:
        super().__init__(
            master,
            fg_color=COLORS["bg_primary"],
            corner_radius=RADIUS["lg"],
            border_color=COLORS["border_subtle"],
            border_width=1,
        )
        self.grid_rowconfigure(2, weight=1, minsize=200)
        self.grid_columnconfigure(0, weight=1)
        self._on_log_select = on_log_select
        self._on_toast = on_toast
        self._send_fn: Callable[[Message, bool], bool] | None = None
        self._send_raw_fn: Callable[[bytes], bool] | None = None
        self._is_connected_fn: Callable[[], bool] = lambda: False
        self._is_listening_fn: Callable[[], bool] = lambda: False
        self._connection_mode: str | None = None
        self._auto_response_var = ctk.BooleanVar(value=True)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 0))

        self.status_bar = StatusBar(top, title=title)
        self.status_bar.pack(fill="x")

        self._conn_card = Card(top, title="Connection Settings")
        self._conn_card.pack(fill="x", pady=(6, 0))
        self._conn_inner = self._conn_card.body

        auto_row = ctk.CTkFrame(self._conn_card.body, fg_color="transparent")
        auto_row.pack(fill="x", pady=(0, 4))
        self._auto_switch = ctk.CTkSwitch(
            auto_row,
            text="Auto Reply",
            variable=self._auto_response_var,
            command=self._on_auto_toggle,
            progress_color=COLORS["accent_primary"],
            button_color=COLORS["text_secondary"],
            button_hover_color=COLORS["text_primary"],
        )
        self._auto_switch.pack(side="left")
        ToolTip(self._auto_switch, AUTO_REPLY_TOOLTIP)
        info_icon = ctk.CTkLabel(
            auto_row,
            text="ⓘ",
            font=FONT_SMALL,
            text_color=COLORS["text_tertiary"],
            width=16,
            cursor="hand2",
        )
        info_icon.pack(side="left", padx=(4, 0))
        ToolTip(info_icon, AUTO_REPLY_TOOLTIP)

        compose_wrap = ctk.CTkFrame(self, fg_color="transparent")
        compose_wrap.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        self.compose_form = ComposeForm(compose_wrap)
        self.compose_form.pack(fill="x")
        self.compose_form.set_send_callback(self._on_send)

        self.message_log = MessageLog(self, on_select=self._on_select_log)
        self.message_log.grid(row=2, column=0, sticky="nsew", padx=4, pady=4)

        self._tools_footer = ctk.CTkFrame(self, fg_color="transparent", height=TOOLS_FOOTER_HEIGHT)
        self._tools_footer.grid(row=3, column=0, sticky="ew", padx=4, pady=(0, 8))
        self._tools_footer.grid_propagate(False)
        self._tools_footer.grid_columnconfigure(0, weight=1)

        self.periodic_panel = PeriodicPanel(
            self._tools_footer,
            get_form_data=self._get_form_data_for_type,
            send_callback=self._send_periodic_message,
            is_connected=self._is_connected_fn,
            on_status=lambda msg: self._on_toast(msg, "warning") if self._on_toast else None,
        )
        self.periodic_panel.pack(fill="x", pady=(0, 2))

        self._test_frame = ctk.CTkFrame(
            self._tools_footer, fg_color=COLORS["bg_secondary"], corner_radius=8
        )
        self._test_frame.pack(fill="x")
        self._test_expanded = False

        test_header = ctk.CTkFrame(self._test_frame, fg_color="transparent", height=30)
        test_header.pack(fill="x", padx=8, pady=(4, 0))
        test_header.pack_propagate(False)
        self._test_toggle = ctk.CTkButton(
            test_header,
            text="▶ Test Tools",
            font=FONT_SMALL,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            anchor="w",
            command=self._toggle_test,
        )
        self._test_toggle.pack(side="left")

        self._test_body = ctk.CTkFrame(self._test_frame, fg_color="transparent")
        test_row = ctk.CTkFrame(self._test_body, fg_color="transparent")
        test_row.pack(fill="x", padx=8, pady=(0, 8))

        unknown_btn = ctk.CTkButton(
            test_row,
            text="Unknown Message",
            fg_color=COLORS["warning"],
            hover_color="#D97706",
            text_color=COLORS["bg_primary"],
            corner_radius=RADIUS["md"],
            height=28,
            command=self._send_unknown,
        )
        unknown_btn.pack(side="left", padx=(0, 8))

        corrupt_btn = ctk.CTkButton(
            test_row,
            text="Corrupt Message",
            fg_color=COLORS["error"],
            hover_color="#DC2626",
            text_color=COLORS["bg_primary"],
            corner_radius=RADIUS["md"],
            height=28,
            command=self._send_corrupt,
        )
        corrupt_btn.pack(side="left")
        ToolTip(unknown_btn, "Sends undefined message ID 99")
        ToolTip(corrupt_btn, "Sends truncated/corrupt binary packet")
        ToolTip(self._test_toggle, "Protocol error scenario tests")

    def _toggle_test(self) -> None:
        self._test_expanded = not self._test_expanded
        if self._test_expanded:
            self._test_body.pack(fill="x")
            self._test_toggle.configure(text="▼ Test Tools")
        else:
            self._test_body.pack_forget()
            self._test_toggle.configure(text="▶ Test Tools")

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

    def set_listening_callback(self, fn: Callable[[], bool]) -> None:
        self._is_listening_fn = fn

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
        self._connection_mode = mode
        for child in self._conn_inner.winfo_children():
            if child is not self._auto_switch.master:
                child.destroy()

        grid = ctk.CTkFrame(self._conn_inner, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 2))
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        if mode == "server":
            port_lbl = ctk.CTkLabel(
                grid, text="Port", font=FONT_SMALL, text_color=COLORS["text_tertiary"]
            )
            port_lbl.grid(row=0, column=0, sticky="w", padx=(0, 8), pady=2)
            port_entry = ctk.CTkEntry(grid, width=100, height=28)
            style_entry(port_entry)
            port_entry.insert(0, "8080")
            port_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=2)

            btn_row = ctk.CTkFrame(grid, fg_color="transparent")
            btn_row.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(6, 0))

            def start() -> None:
                try:
                    port = int(port_entry.get())
                    if on_start_server:
                        on_start_server(port)
                except ValueError:
                    if self._on_toast:
                        self._on_toast("Invalid port number", "error")

            start_btn = ctk.CTkButton(btn_row, text="Start Server", height=28, command=start)
            style_button_primary(start_btn)
            start_btn.pack(side="left", padx=(0, 8))

            if on_stop_server:
                stop_btn = ctk.CTkButton(
                    btn_row, text="Stop Server", height=28, command=on_stop_server
                )
                style_button_secondary(stop_btn)
                stop_btn.pack(side="left")
        else:
            ctk.CTkLabel(grid, text="IP", font=FONT_SMALL, text_color=COLORS["text_tertiary"]).grid(
                row=0, column=0, sticky="w", padx=(0, 8), pady=2
            )
            ip_entry = ctk.CTkEntry(grid, width=120, height=28)
            style_entry(ip_entry)
            ip_entry.insert(0, "127.0.0.1")
            ip_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=2)

            port_lbl = ctk.CTkLabel(
                grid, text="Port", font=FONT_SMALL, text_color=COLORS["text_tertiary"]
            )
            port_lbl.grid(row=0, column=2, sticky="w", padx=(0, 8), pady=2)
            port_entry = ctk.CTkEntry(grid, width=80, height=28)
            style_entry(port_entry)
            port_entry.insert(0, "8080")
            port_entry.grid(row=0, column=3, sticky="ew", pady=2)

            btn_row = ctk.CTkFrame(grid, fg_color="transparent")
            btn_row.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(6, 0))

            def connect() -> None:
                try:
                    port = int(port_entry.get())
                    if on_connect:
                        on_connect(ip_entry.get(), port)
                except ValueError:
                    if self._on_toast:
                        self._on_toast("Invalid port number", "error")

            connect_btn = ctk.CTkButton(btn_row, text="Connect", height=28, command=connect)
            style_button_primary(connect_btn)
            connect_btn.pack(side="left", padx=(0, 8))

            if on_disconnect:
                disconnect_btn = ctk.CTkButton(
                    btn_row, text="Disconnect", height=28, command=on_disconnect
                )
                style_button_secondary(disconnect_btn)
                disconnect_btn.pack(side="left")

    def handle_network_event(self, event: NetworkEvent) -> None:
        """Process a network event and update UI."""
        ts = format_timestamp(event.timestamp)

        if event.type == "connected":
            self.set_status("Connected")
            if self._on_toast:
                self._on_toast("Connected", "success")
        elif event.type == "disconnected":
            if self._connection_mode == "server" and self._is_listening_fn():
                self.set_status("Waiting for connection...")
            else:
                self.set_status("Not connected")
            self.periodic_panel.on_disconnect()
            if self._on_toast:
                self._on_toast("Disconnected", "warning")
        elif event.type == "message_sent":
            info = event.payload
            if isinstance(info, SentMessageInfo):
                self.message_log.add_entry(
                    LogEntry(
                        timestamp=ts,
                        direction="Transmit",
                        message_id=info.message.message_id,
                        is_auto=info.is_auto,
                        is_periodic=info.is_periodic,
                        message=info.message,
                        raw_timestamp=event.timestamp,
                    )
                )
                if not info.is_auto and not info.is_periodic and self._on_toast:
                    self._on_toast("Message sent", "success")
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
                    self._on_toast("Unknown message received", "warning")
        elif event.type == "protocol_error":
            info = event.payload
            if isinstance(info, ReceivedMessageInfo):
                self.message_log.add_entry(
                    LogEntry(
                        timestamp=ts,
                        direction="Receive",
                        message_id=None,
                        is_error=True,
                        error_text="Unparseable message",
                        raw_timestamp=event.timestamp,
                    )
                )
                if self._on_toast:
                    self._on_toast("Invalid message received", "error")

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

    def _send_periodic_message(self, message: Message) -> bool:
        if self._send_fn:
            return self._send_fn(message, is_auto=False, is_periodic=True)
        return False

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
        pass

    def _send_unknown(self) -> None:
        if not self._send_raw_fn:
            return
        payload = struct.pack("!i", 99)
        self._send_raw_fn(frame_payload(payload))

    def _send_corrupt(self) -> None:
        if not self._send_raw_fn:
            return
        payload = struct.pack("!i", 1)[:2]
        self._send_raw_fn(frame_payload(payload))
