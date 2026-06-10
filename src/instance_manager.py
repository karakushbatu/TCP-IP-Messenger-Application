"""Manages multiple application instances."""

from __future__ import annotations

from typing import Callable, Literal

from src.instance import Instance, InstanceMode
from src.ui.main_view import InstancePanel
from src.ui.message_log import LogEntry

DemoMode = Literal["auto", "manual", "server_only", "client_only"]


class InstanceManager:
    """Creates and manages server/client instances."""

    def __init__(self, on_log_select: Callable[[LogEntry], None] | None = None) -> None:
        self._instances: list[Instance] = []
        self._on_log_select = on_log_select

    @property
    def instances(self) -> list[Instance]:
        return list(self._instances)

    def create_instance(
        self,
        mode: InstanceMode,
        parent_panel_factory: Callable[[], InstancePanel],
        on_toast: Callable[[str, str], None] | None = None,
    ) -> Instance:
        panel = parent_panel_factory()
        panel._on_toast = on_toast  # noqa: SLF001
        panel._on_log_select = self._on_log_select  # noqa: SLF001

        instance = Instance(Instance.create_id(), mode, panel)
        self._instances.append(instance)
        return instance

    def setup_demo(
        self,
        mode: DemoMode,
        parent: object,
        on_toast: Callable[[str, str], None] | None = None,
        on_auto_connect: Callable[[Instance, Instance], None] | None = None,
    ) -> tuple[Instance, Instance | None]:
        """Set up demo instances based on mode."""
        if mode == "server_only":
            server = self._create_server_panel(parent, on_toast)
            return server, None

        if mode == "client_only":
            client = self._create_client_panel(parent, on_toast)
            return client, None

        server = self._create_server_panel(parent, on_toast)
        client = self._create_client_panel(parent, on_toast)

        if mode == "auto" and on_auto_connect:
            on_auto_connect(server, client)  # server starts, client connects after delay

        return server, client

    def _create_server_panel(
        self, parent: object, on_toast: Callable[[str, str], None] | None
    ) -> Instance:
        from src.ui.main_view import InstancePanel

        panel = InstancePanel(parent)  # type: ignore[arg-type]
        panel._on_toast = on_toast  # noqa: SLF001
        panel._on_log_select = self._on_log_select  # noqa: SLF001
        instance = Instance(Instance.create_id(), "server", panel)
        self._instances.append(instance)
        return instance

    def _create_client_panel(
        self, parent: object, on_toast: Callable[[str, str], None] | None
    ) -> Instance:
        from src.ui.main_view import InstancePanel

        panel = InstancePanel(parent)  # type: ignore[arg-type]
        panel._on_toast = on_toast  # noqa: SLF001
        panel._on_log_select = self._on_log_select  # noqa: SLF001
        instance = Instance(Instance.create_id(), "client", panel)
        self._instances.append(instance)
        return instance

    def process_all_events(self) -> None:
        for instance in self._instances:
            instance.process_events()

    def stop_all(self) -> None:
        for instance in self._instances:
            instance.stop()

    def clear(self) -> None:
        self.stop_all()
        self._instances.clear()
