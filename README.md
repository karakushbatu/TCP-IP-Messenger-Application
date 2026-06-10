# Protocol Bridge

**TCP Binary Messaging Platform**

Desktop application demonstrating TCP/IP binary messaging. Server/client modes, auto-response, periodic sending, and multi-instance tabs in one app.

## Features

- **Instance tabs** — Home tab + `+ Instance` for multiple server/client sessions
- **Four startup modes** — Auto, Manual, Server Only, Client Only
- **Binary protocol** — Message 1 (Personnel, 64 B) and Message 2 (Position, 29 B), length-prefixed TCP framing
- **Auto reply** — Message 1 ↔ Message 2 cross-response (hover tooltip explains behavior)
- **Periodic send** — Default 100 ms / 500 ms intervals (no toast spam)
- **Field hints** — Hover tooltips show valid value ranges
- **Validation** — Field bounds, byte counter, disabled Send on invalid data
- **Test tools** — Unknown ID and corrupt packet injection
- **Message history & detail** — Click a log row for full content in the bottom panel

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python -m src.main
```

On launch, the **Home** tab appears. Selecting a mode converts the tab into a workspace; closing it returns to the welcome screen.

## Build

```bash
# Windows → dist/Protocol Bridge.exe
build\build_windows.bat

# macOS → dist/Protocol-Bridge-macOS.dmg
bash build/build_macos.sh
```

## Protocol & Testing

- Specification: [docs/PROTOCOL.md](docs/PROTOCOL.md)
- Manual test plan: [docs/TEST_PLAN.md](docs/TEST_PLAN.md)

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```
