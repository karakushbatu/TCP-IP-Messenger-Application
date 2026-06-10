# TCP Tactical Messenger

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

TCP Tactical Messenger is a native Python desktop application that demonstrates TCP/IP communication, binary message serialization, automatic response logic, and periodic transmission through a polished Turkish user interface.

![Screenshot placeholder](assets/icon.png)

## Features

- TCP server and client modes in a single application
- Two predefined binary message types (Personnel, Unit Position)
- Length-prefixed TCP framing with `struct` serialization
- Automatic cross-response (Message 1 ↔ Message 2)
- Loop-safe auto-response with suppression guard
- Periodic message sending (100 ms / 500 ms defaults)
- Multi-instance split-view demo (server + client side by side)
- Turkish UI with dark professional theme
- Field validation with byte-length counters
- Unknown and corrupt message handling
- Toast notifications and shared message detail panel

## Demo Flow

1. Launch the application
2. Click **Sunucu + İstemci (Otomatik Bağlan)** on the welcome screen
3. Server starts on port 8080, client connects to `127.0.0.1:8080`
4. Send Message 1 from either panel and observe auto-response
5. Enable periodic sending to demonstrate continuous transmission

## Message Protocol

### Message 1 — Personnel (64 bytes)

| Field | Type | Constraint |
|---|---|---|
| Mesaj ID | int32 | `1` |
| Birlik Referans Numarası | int32 | `-1000` to `9999` |
| Adı | string(25) | UTF-8, null-padded |
| Unit No | uint32 | `0` to `4294967295` |
| Soyadı | string(25) | UTF-8, null-padded |
| Rütbe | int16 | `0–2` |

### Message 2 — Unit Position (29 bytes)

| Field | Type | Constraint |
|---|---|---|
| Mesaj ID | int32 | `2` |
| Birlik Referans Numarası | int32 | `1` to `9999` |
| Geçerlilik | byte | `0/1` |
| Enlem | int64 | `-32400000` to `32400000` |
| Boylam | int64 | `-64800000` to `64800000` |
| Yükseklik | int32 | `0` to `10000` |

See [docs/PROTOCOL.md](docs/PROTOCOL.md) for full specification.

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running the App

```bash
python -m src.main
```

## Running Tests

```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

## Building Standalone Executables

PyInstaller creates platform-specific distributables:

| Platform | Output | Archive |
|---|---|---|
| Windows | `dist/TCP Tactical Messenger.exe` | `dist/TCP-Tactical-Messenger-Windows.zip` |
| macOS | `dist/TCP Tactical Messenger.app` | `dist/TCP-Tactical-Messenger-macOS.zip` |

```bash
# Install build dependencies first
pip install -r requirements-dev.txt

# Windows
build\build_windows.bat

# macOS / Linux (macOS bundle only on macOS)
bash build/build_macos.sh
```

## GitHub Release

Releases are automated via GitHub Actions. Pushing a version tag triggers:

1. Ruff lint + pytest (90% protocol coverage)
2. Windows `.exe` build
3. macOS `.app` build
4. GitHub Release with both ZIP artifacts

```bash
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

Or create a release from the GitHub UI — the workflow runs on any `v*` tag push.

## Architecture

```
main.py → AppShell → SplitView → InstanceManager → Instance (server/client)
                                                      ├── Protocol (messages, serializer, validator)
                                                      ├── Network (server, client, handler)
                                                      └── UI (compose, log, periodic, detail)
```

## Tech Stack

- Python 3.11+
- CustomTkinter (GUI)
- `socket` + `threading` + `queue` (networking)
- `struct` (binary serialization)
- pytest + Ruff + PyInstaller

## License

MIT
