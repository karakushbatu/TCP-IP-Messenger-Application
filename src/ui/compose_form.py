"""Message compose form with validation."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from src.protocol.messages import MESSAGE_DEFINITIONS, RANK_LABELS
from src.protocol.validator import ValidationError, validate_message
from src.ui.components import Card, SegmentedControl
from src.ui.theme import (
    COLORS,
    FONT_SMALL,
    RADIUS,
    style_button_primary,
    style_button_secondary,
    style_entry,
)
from src.utils.defaults import QUICK_FILL_MESSAGE_1, QUICK_FILL_MESSAGE_2


class ComposeForm(Card):
    """Compact aligned form for composing Message 1 or Message 2."""

    SCROLL_HEIGHT = 132
    LABEL_WIDTH = 138
    FIELD_WIDTH = 148

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_validation_change: Callable[[bool], None] | None = None,
    ) -> None:
        super().__init__(master, title="Mesaj Oluştur", subtitle="Binary mesaj derleme")
        self.body.pack_configure(padx=10, pady=(2, 8))
        self._on_validation_change = on_validation_change
        self._message_id = 1
        self._fields: dict[str, ctk.CTkBaseClass] = {}
        self._error_labels: dict[str, ctk.CTkLabel] = {}
        self._byte_counters: dict[str, ctk.CTkLabel] = {}
        self._validation_errors: list[ValidationError] = []

        self._segment = SegmentedControl(
            self.body,
            options=[("Mesaj 1", 1), ("Mesaj 2", 2)],
            on_change=self._switch_type,
            initial=1,
        )
        self._segment.pack(anchor="w", pady=(0, 6))

        self._scroll = ctk.CTkScrollableFrame(
            self.body,
            fg_color=COLORS["bg_input"],
            height=self.SCROLL_HEIGHT,
            corner_radius=RADIUS["sm"],
            scrollbar_button_color=COLORS["bg_elevated"],
            scrollbar_button_hover_color=COLORS["bg_hover"],
        )
        self._scroll.pack(fill="x", pady=(0, 6))
        self._fields_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self._fields_frame.pack(fill="x", padx=6, pady=4)

        btn_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        btn_frame.pack(fill="x")

        self._quick_fill_btn = ctk.CTkButton(
            btn_frame,
            text="Hızlı Doldur",
            height=28,
            command=self._quick_fill,
        )
        style_button_secondary(self._quick_fill_btn)
        self._quick_fill_btn.pack(side="left", padx=(0, 8))

        self._send_btn = ctk.CTkButton(
            btn_frame,
            text="Gönder",
            height=28,
            state="disabled",
            command=lambda: None,
        )
        style_button_primary(self._send_btn)
        self._send_btn.pack(side="left")

        self._build_fields()
        self._quick_fill()
        self._validate()

    def set_send_callback(self, callback: Callable[[], None]) -> None:
        self._send_btn.configure(command=callback)

    def _switch_type(self, message_id: int) -> None:
        self._message_id = message_id
        self._build_fields()
        self._quick_fill()
        self._validate()

    def _readonly_box(self, parent: ctk.CTkFrame, value: str) -> ctk.CTkFrame:
        box = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_tertiary"],
            corner_radius=RADIUS["sm"],
            border_color=COLORS["border_subtle"],
            border_width=1,
            width=self.FIELD_WIDTH,
            height=26,
        )
        box.pack_propagate(False)
        ctk.CTkLabel(
            box,
            text=value,
            font=FONT_SMALL,
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(side="left", padx=8)
        return box

    def _build_fields(self) -> None:
        for child in self._fields_frame.winfo_children():
            child.destroy()
        self._fields.clear()
        self._error_labels.clear()
        self._byte_counters.clear()

        for field_def in MESSAGE_DEFINITIONS[self._message_id]:
            block = ctk.CTkFrame(self._fields_frame, fg_color="transparent")
            block.pack(fill="x", pady=2)

            row = ctk.CTkFrame(block, fg_color="transparent")
            row.pack(fill="x")

            ctk.CTkLabel(
                row,
                text=field_def.ui_label,
                font=FONT_SMALL,
                text_color=COLORS["text_secondary"],
                anchor="w",
                width=self.LABEL_WIDTH,
            ).pack(side="left")

            input_wrap = ctk.CTkFrame(row, fg_color="transparent")
            input_wrap.pack(side="left")

            if not field_def.editable:
                box = self._readonly_box(input_wrap, str(field_def.fixed_value))
                box.pack(side="left")
                self._fields[field_def.internal_name] = box
            elif field_def.dropdown_options:
                options = [f"{k} — {v}" for k, v in field_def.dropdown_options.items()]
                combo = ctk.CTkComboBox(
                    input_wrap,
                    values=options,
                    width=self.FIELD_WIDTH,
                    height=26,
                    command=lambda _v: self._validate(),
                )
                combo.pack(side="left")
                self._fields[field_def.internal_name] = combo
            elif field_def.field_type == "bool":
                toggle = ctk.CTkSwitch(
                    input_wrap,
                    text="Geçerli",
                    onvalue="1",
                    offvalue="0",
                    command=self._validate,
                )
                toggle.pack(side="left")
                self._fields[field_def.internal_name] = toggle
            else:
                entry = ctk.CTkEntry(input_wrap, width=self.FIELD_WIDTH, height=26)
                style_entry(entry)
                entry.pack(side="left")
                entry.bind("<KeyRelease>", lambda _e: self._validate())
                self._fields[field_def.internal_name] = entry

                if field_def.field_type == "string":
                    counter = ctk.CTkLabel(
                        input_wrap,
                        text="0/25",
                        font=FONT_SMALL,
                        text_color=COLORS["text_tertiary"],
                        width=38,
                    )
                    counter.pack(side="left", padx=(6, 0))
                    self._byte_counters[field_def.internal_name] = counter

            err = ctk.CTkLabel(
                block,
                text="",
                font=FONT_SMALL,
                text_color=COLORS["error"],
                anchor="w",
            )
            err.pack(anchor="w", padx=(self.LABEL_WIDTH, 0))
            self._error_labels[field_def.internal_name] = err

    def _get_field_value(self, name: str) -> object:
        widget = self._fields.get(name)
        if widget is None:
            return None
        if isinstance(widget, ctk.CTkFrame):
            label = widget.winfo_children()[0]
            if isinstance(label, ctk.CTkLabel):
                return int(label.cget("text"))
        if isinstance(widget, ctk.CTkComboBox):
            text = widget.get()
            return int(text.split(" — ")[0])
        if isinstance(widget, ctk.CTkSwitch):
            return int(widget.get())
        if isinstance(widget, ctk.CTkEntry):
            text = widget.get().strip()
            field_defs = {f.internal_name: f for f in MESSAGE_DEFINITIONS[self._message_id]}
            fdef = field_defs.get(name)
            if fdef and fdef.field_type in ("int", "uint", "short", "long"):
                try:
                    return int(text) if text else 0
                except ValueError:
                    return text
            return text
        return None

    def get_form_data(self) -> dict[str, object]:
        """Return current form values as a dict."""
        data: dict[str, object] = {"message_id": self._message_id}
        for name in self._fields:
            if name != "message_id":
                data[name] = self._get_field_value(name)
        return data

    def get_message_id(self) -> int:
        return self._message_id

    def _quick_fill(self) -> None:
        defaults = QUICK_FILL_MESSAGE_1 if self._message_id == 1 else QUICK_FILL_MESSAGE_2
        for name, value in defaults.items():
            widget = self._fields.get(name)
            if widget is None:
                continue
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                widget.insert(0, str(value))
            elif isinstance(widget, ctk.CTkComboBox):
                if isinstance(value, int):
                    widget.set(f"{value} — {RANK_LABELS.get(value, '')}")
            elif isinstance(widget, ctk.CTkSwitch):
                widget.select() if value else widget.deselect()
        self._validate()

    def _validate(self) -> bool:
        data = self.get_form_data()
        self._validation_errors = validate_message(self._message_id, data)

        error_fields = {e.field for e in self._validation_errors}
        for name, err_label in self._error_labels.items():
            matching = [e for e in self._validation_errors if e.field == name]
            err_label.configure(text=matching[0].message if matching else "")

        for name, counter in self._byte_counters.items():
            widget = self._fields.get(name)
            if isinstance(widget, ctk.CTkEntry):
                byte_len = len(widget.get().encode("utf-8"))
                counter.configure(text=f"{byte_len}/25")
                counter.configure(
                    text_color=COLORS["error"] if byte_len > 25 else COLORS["text_tertiary"]
                )

        for name, widget in self._fields.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.configure(
                    border_color=COLORS["error"]
                    if name in error_fields
                    else COLORS["border"]
                )

        is_valid = len(self._validation_errors) == 0
        self._send_btn.configure(state="normal" if is_valid else "disabled")
        if self._on_validation_change:
            self._on_validation_change(is_valid)
        return is_valid

    def is_valid(self) -> bool:
        return self._validate()
