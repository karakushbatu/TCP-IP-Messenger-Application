"""Message compose form with validation."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from src.protocol.messages import MESSAGE_DEFINITIONS, RANK_LABELS
from src.protocol.validator import ValidationError, validate_message
from src.ui.theme import COLORS, FONT_BODY, FONT_SMALL
from src.utils.defaults import QUICK_FILL_MESSAGE_1, QUICK_FILL_MESSAGE_2


class ComposeForm(ctk.CTkFrame):
    """Dynamic form for composing Message 1 or Message 2."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_validation_change: Callable[[bool], None] | None = None,
    ) -> None:
        super().__init__(master, fg_color=COLORS["bg_secondary"], corner_radius=8)
        self._on_validation_change = on_validation_change
        self._message_id = 1
        self._fields: dict[str, ctk.CTkBaseClass] = {}
        self._error_labels: dict[str, ctk.CTkLabel] = {}
        self._byte_counters: dict[str, ctk.CTkLabel] = {}
        self._validation_errors: list[ValidationError] = []

        header = ctk.CTkLabel(
            self,
            text="Mesaj Oluştur",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["text_primary"],
        )
        header.pack(anchor="w", padx=12, pady=(10, 6))

        tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_frame.pack(fill="x", padx=12, pady=(0, 8))

        self._btn_msg1 = ctk.CTkButton(
            tab_frame,
            text="Mesaj 1",
            width=100,
            command=lambda: self._switch_type(1),
        )
        self._btn_msg1.pack(side="left", padx=(0, 4))

        self._btn_msg2 = ctk.CTkButton(
            tab_frame,
            text="Mesaj 2",
            width=100,
            fg_color=COLORS["bg_tertiary"],
            command=lambda: self._switch_type(2),
        )
        self._btn_msg2.pack(side="left")

        self._fields_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._fields_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=(0, 10))

        self._quick_fill_btn = ctk.CTkButton(
            btn_frame,
            text="Hızlı Doldur",
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["bg_hover"],
            command=self._quick_fill,
        )
        self._quick_fill_btn.pack(side="left", padx=(0, 8))

        self._send_btn = ctk.CTkButton(
            btn_frame,
            text="Gönder",
            fg_color=COLORS["accent_primary"],
            hover_color="#008F7A",
            state="disabled",
            command=lambda: None,
        )
        self._send_btn.pack(side="left")

        self._build_fields()
        self._quick_fill()
        self._validate()

    def set_send_callback(self, callback: Callable[[], None]) -> None:
        self._send_btn.configure(command=callback)

    def _switch_type(self, message_id: int) -> None:
        self._message_id = message_id
        if message_id == 1:
            self._btn_msg1.configure(fg_color=COLORS["accent_primary"])
            self._btn_msg2.configure(fg_color=COLORS["bg_tertiary"])
        else:
            self._btn_msg1.configure(fg_color=COLORS["bg_tertiary"])
            self._btn_msg2.configure(fg_color=COLORS["accent_primary"])
        self._build_fields()
        self._quick_fill()
        self._validate()

    def _build_fields(self) -> None:
        for child in self._fields_frame.winfo_children():
            child.destroy()
        self._fields.clear()
        self._error_labels.clear()
        self._byte_counters.clear()

        definitions = MESSAGE_DEFINITIONS[self._message_id]
        for field_def in definitions:
            row = ctk.CTkFrame(self._fields_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)

            label = ctk.CTkLabel(
                row,
                text=field_def.ui_label,
                font=FONT_BODY,
                text_color=COLORS["text_secondary"],
                width=220,
                anchor="w",
            )
            label.pack(side="left")

            if not field_def.editable:
                val = ctk.CTkLabel(
                    row,
                    text=str(field_def.fixed_value),
                    font=FONT_BODY,
                    text_color=COLORS["text_primary"],
                )
                val.pack(side="left")
                self._fields[field_def.internal_name] = val
            elif field_def.dropdown_options:
                options = [f"{k} — {v}" for k, v in field_def.dropdown_options.items()]
                combo = ctk.CTkComboBox(
                    row,
                    values=options,
                    width=200,
                    command=lambda _v: self._validate(),
                )
                combo.pack(side="left")
                self._fields[field_def.internal_name] = combo
            elif field_def.field_type == "bool":
                var = ctk.StringVar(value="1")
                toggle = ctk.CTkSwitch(
                    row,
                    text="Geçerli",
                    variable=var,
                    onvalue="1",
                    offvalue="0",
                    command=self._validate,
                )
                toggle.pack(side="left")
                self._fields[field_def.internal_name] = toggle
            else:
                entry = ctk.CTkEntry(row, width=200)
                entry.pack(side="left")
                entry.bind("<KeyRelease>", lambda _e: self._validate())
                self._fields[field_def.internal_name] = entry

                if field_def.field_type == "string":
                    counter = ctk.CTkLabel(
                        row,
                        text="0/25 byte",
                        font=FONT_SMALL,
                        text_color=COLORS["text_tertiary"],
                    )
                    counter.pack(side="left", padx=(8, 0))
                    self._byte_counters[field_def.internal_name] = counter

            err = ctk.CTkLabel(
                self._fields_frame,
                text="",
                font=FONT_SMALL,
                text_color=COLORS["error"],
                anchor="w",
            )
            err.pack(anchor="w", padx=(220, 0))
            self._error_labels[field_def.internal_name] = err

    def _get_field_value(self, name: str) -> object:
        widget = self._fields.get(name)
        if widget is None:
            return None
        if isinstance(widget, ctk.CTkLabel):
            return int(widget.cget("text"))
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
            if matching:
                err_label.configure(text=matching[0].message)
            else:
                err_label.configure(text="")

        for name, counter in self._byte_counters.items():
            widget = self._fields.get(name)
            if isinstance(widget, ctk.CTkEntry):
                byte_len = len(widget.get().encode("utf-8"))
                counter.configure(text=f"{byte_len}/25 byte")
                if byte_len > 25:
                    counter.configure(text_color=COLORS["error"])
                else:
                    counter.configure(text_color=COLORS["text_tertiary"])

        for name, widget in self._fields.items():
            if isinstance(widget, ctk.CTkEntry):
                if name in error_fields:
                    widget.configure(border_color=COLORS["error"])
                else:
                    widget.configure(border_color=COLORS["border"])

        is_valid = len(self._validation_errors) == 0
        self._send_btn.configure(state="normal" if is_valid else "disabled")
        if self._on_validation_change:
            self._on_validation_change(is_valid)
        return is_valid

    def is_valid(self) -> bool:
        return self._validate()
