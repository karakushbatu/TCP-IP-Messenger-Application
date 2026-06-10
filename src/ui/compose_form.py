"""Message compose form with validation."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from src.protocol.messages import (
    MESSAGE_DEFINITIONS,
    RANK_LABELS,
    FieldDefinition,
    field_range_hint,
)
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
from src.ui.tooltip import ToolTip
from src.utils.defaults import QUICK_FILL_MESSAGE_1, QUICK_FILL_MESSAGE_2


class ComposeForm(Card):
    """Two-column compose form — all fields visible without scroll."""

    LABEL_WIDTH = 118
    FIELD_WIDTH = 112
    COL_GAP = 16

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_validation_change: Callable[[bool], None] | None = None,
    ) -> None:
        super().__init__(master, title="Compose Message", subtitle="Binary message builder")
        self.body.pack_configure(padx=10, pady=(2, 8))
        self._on_validation_change = on_validation_change
        self._message_id = 1
        self._fields: dict[str, ctk.CTkBaseClass] = {}
        self._error_labels: dict[str, ctk.CTkLabel] = {}
        self._byte_counters: dict[str, ctk.CTkLabel] = {}
        self._validation_errors: list[ValidationError] = []
        self._tooltips: list[ToolTip] = []

        self._segment = SegmentedControl(
            self.body,
            options=[("Message 1", 1), ("Message 2", 2)],
            on_change=self._switch_type,
            initial=1,
        )
        self._segment.pack(anchor="w", pady=(0, 6))

        self._grid_wrap = ctk.CTkFrame(
            self.body,
            fg_color=COLORS["bg_input"],
            corner_radius=RADIUS["sm"],
        )
        self._grid_wrap.pack(fill="x", pady=(0, 6))
        self._fields_frame = ctk.CTkFrame(self._grid_wrap, fg_color="transparent")
        self._fields_frame.pack(fill="x", padx=8, pady=8)

        btn_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        btn_frame.pack(fill="x")

        self._quick_fill_btn = ctk.CTkButton(
            btn_frame, text="Quick Fill", height=28, command=self._quick_fill
        )
        style_button_secondary(self._quick_fill_btn)
        self._quick_fill_btn.pack(side="left", padx=(0, 8))

        self._send_btn = ctk.CTkButton(
            btn_frame, text="Send", height=28, state="disabled", command=lambda: None
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

    def _bind_hint(self, widget: ctk.CTkBaseClass, field_def: FieldDefinition) -> None:
        hint = field_range_hint(field_def)
        if hint:
            self._tooltips.append(ToolTip(widget, hint))

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

    def _place_field(
        self,
        parent: ctk.CTkFrame,
        field_def: FieldDefinition,
        row_index: int,
    ) -> None:
        label_row = row_index * 2
        error_row = label_row + 1

        lbl = ctk.CTkLabel(
            parent,
            text=field_def.ui_label,
            font=FONT_SMALL,
            text_color=COLORS["text_secondary"],
            anchor="w",
            width=self.LABEL_WIDTH,
        )
        lbl.grid(row=label_row, column=0, sticky="w", padx=(0, 6), pady=(2, 0))
        self._bind_hint(lbl, field_def)

        input_cell = ctk.CTkFrame(parent, fg_color="transparent")
        input_cell.grid(row=label_row, column=1, sticky="w", pady=(2, 0))

        if not field_def.editable:
            box = self._readonly_box(input_cell, str(field_def.fixed_value))
            box.pack(side="left")
            self._fields[field_def.internal_name] = box
            self._bind_hint(box, field_def)
        elif field_def.dropdown_options:
            options = [f"{k} — {v}" for k, v in field_def.dropdown_options.items()]
            combo = ctk.CTkComboBox(
                input_cell,
                values=options,
                width=self.FIELD_WIDTH,
                height=26,
                command=lambda _v: self._validate(),
            )
            combo.pack(side="left")
            self._fields[field_def.internal_name] = combo
            self._bind_hint(combo, field_def)
        elif field_def.field_type == "bool":
            toggle = ctk.CTkSwitch(
                input_cell,
                text="Valid",
                onvalue="1",
                offvalue="0",
                command=self._validate,
            )
            toggle.pack(side="left")
            self._fields[field_def.internal_name] = toggle
            self._bind_hint(toggle, field_def)
        else:
            entry = ctk.CTkEntry(input_cell, width=self.FIELD_WIDTH, height=26)
            style_entry(entry)
            entry.pack(side="left")
            entry.bind("<KeyRelease>", lambda _e: self._validate())
            self._fields[field_def.internal_name] = entry
            self._bind_hint(entry, field_def)

            if field_def.field_type == "string":
                counter = ctk.CTkLabel(
                    input_cell,
                    text="0/25",
                    font=FONT_SMALL,
                    text_color=COLORS["text_tertiary"],
                    width=34,
                )
                counter.pack(side="left", padx=(4, 0))
                self._byte_counters[field_def.internal_name] = counter

        err = ctk.CTkLabel(
            parent,
            text="",
            font=FONT_SMALL,
            text_color=COLORS["error"],
            anchor="w",
        )
        err.grid(row=error_row, column=0, columnspan=2, sticky="w", padx=(0, 0), pady=(0, 2))
        self._error_labels[field_def.internal_name] = err

    def _build_fields(self) -> None:
        for child in self._fields_frame.winfo_children():
            child.destroy()
        self._fields.clear()
        self._error_labels.clear()
        self._byte_counters.clear()
        self._tooltips.clear()

        definitions = MESSAGE_DEFINITIONS[self._message_id]
        half = (len(definitions) + 1) // 2

        left = ctk.CTkFrame(self._fields_frame, fg_color="transparent")
        left.pack(side="left", fill="y", padx=(0, self.COL_GAP))
        left.grid_columnconfigure(1, weight=0)

        right = ctk.CTkFrame(self._fields_frame, fg_color="transparent")
        right.pack(side="left", fill="y")
        right.grid_columnconfigure(1, weight=0)

        for idx, field_def in enumerate(definitions):
            col_frame = left if idx < half else right
            row = idx if idx < half else idx - half
            self._place_field(col_frame, field_def, row)

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
