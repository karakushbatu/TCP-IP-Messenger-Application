# Cursor Starter Prompt — TCP/IP Tactical Messenger Desktop App

You are an expert Python desktop application engineer. Build a complete, polished, presentation-ready desktop application named:

**TCP Tactical Messenger**

The project is a TCP/IP-based messaging application that can operate as both server and client. It sends and receives two predefined binary message types over TCP. The application must have a strong, modern, professional Turkish UI and must be suitable for a technical case-study demo.

IMPORTANT:
- Implement the requirements exactly.
- Do not add irrelevant features.
- Do not use ASELSAN branding, logos, names, or any official defense-company branding.
- All UI text must be in Turkish.
- Code comments and docstrings should be in English.
- Use clean architecture, type hints, tests, and readable structure.
- Prioritize correctness of TCP communication, binary serialization, validation, auto-response, periodic sending, and polished UI.

---

## 1. Tech Stack

Use:

- Python 3.11+
- CustomTkinter for the desktop GUI
- Python standard library `socket` for TCP communication
- Python standard library `threading` for networking/background work
- Python standard library `queue` for safe UI event transfer
- Python standard library `struct` for binary serialization/deserialization
- `dataclasses` for message models
- pytest + pytest-cov for tests
- Ruff for linting
- PyInstaller for distributable builds

Do NOT use:

- Electron
- Web frameworks
- asyncio
- Database
- External networking libraries
- Large unnecessary dependencies

Runtime dependency should be minimal:

```txt
customtkinter>=5.2.0
```

Dev dependencies:

```txt
ruff>=0.4.0
pytest>=8.0.0
pytest-cov>=5.0.0
pyinstaller>=6.0.0
```

---

## 2. Core Functional Requirement Summary

The application must:

1. Work as either a TCP server or TCP client.
2. Allow the user to enter port/IP settings.
3. Send and receive predefined binary messages over TCP/IP.
4. Show transmitted messages with the label `Transmit`.
5. Show received messages with the label `Receive`.
6. Display all sent/received message fields in a detailed view.
7. Automatically respond:
   - When Message 1 is received, send Message 2 as a response.
   - When Message 2 is received, send Message 1 as a response.
8. Warn the user when an undefined/unknown message is received.
9. Support periodic automatic sending:
   - Message 1 every 100 ms
   - Message 2 every 500 ms
10. Support multiple app instances in one window for an excellent demo:
    - Left panel: server
    - Right panel: client
    - Both visible simultaneously
11. Have a polished, dark, professional UI suitable for a technical presentation.

CRITICAL AUTO-RESPONSE SAFETY:
Do not create infinite auto-response loops.
When an auto-response is received, the other side should not endlessly auto-respond back again. Implement one of these safe strategies:

Preferred:
- Add metadata inside the local log object indicating whether a message was manually sent or auto-sent.
- Auto-response should only trigger for received messages that are not marked as auto-response when possible.
- Since metadata is not part of the wire protocol, include an application-level setting:
  - `auto_response_enabled`
  - `prevent_auto_response_loop`
- Default: ON.
- If a received message arrives immediately after this instance's own auto-response, avoid ping-pong by using a short suppression window or a response-depth guard.

The protocol payload itself must not be polluted with non-specified fields.

---

## 3. Binary Protocol Specification

Every TCP message must use this wire format:

```text
[4-byte length header][binary message payload]
```

Length header:
- Struct format: `!I`
- Network byte order, big-endian
- Length means payload length only, not including the 4-byte header.

All message payloads must use network byte order with `!` prefix in struct format.

---

## 4. Message Type 1 — Personnel Message

Turkish UI name: `Mesaj 1 — Personel Bilgisi`

Fields:

| Field UI Label | Internal Name | Type | Size | Constraint |
|---|---|---:|---:|---|
| Mesaj ID | message_id | int | 4 bytes | fixed value `1` |
| Birlik Referans Numarası | unit_reference_no | int | 4 bytes | `-1000` to `9999` |
| Adı | first_name | string | 25 bytes | UTF-8, max 25 bytes, null-padded |
| Unit No | unit_no | uint32 | 4 bytes | `0` to `4294967295` |
| Soyadı | last_name | string | 25 bytes | UTF-8, max 25 bytes, null-padded |
| Rütbe | rank | short | 2 bytes | `0=Üsteğmen`, `1=Teğmen`, `2=Asteğmen` |

Struct format:

```python
MESSAGE_1_FORMAT = "!ii25sI25sh"
```

Expected payload size:

```python
64 bytes
```

Rank mapping:

```python
RANK_LABELS = {
    0: "Üsteğmen",
    1: "Teğmen",
    2: "Asteğmen",
}
```

---

## 5. Message Type 2 — Unit Position Message

Turkish UI name: `Mesaj 2 — Birlik Konum Bilgisi`

Fields:

| Field UI Label | Internal Name | Type | Size | Constraint |
|---|---|---:|---:|---|
| Mesaj ID | message_id | int | 4 bytes | fixed value `2` |
| Birlik Referans Numarası | unit_reference_no | int | 4 bytes | `1` to `9999` |
| Birlik Konum Bilgisi Geçerliliği | position_validity | byte | 1 byte | `1=True`, `0=False` |
| Enlem | latitude | long/int64 | 8 bytes | `-32400000` to `32400000` |
| Boylam | longitude | long/int64 | 8 bytes | `-64800000` to `64800000` |
| Yükseklik | altitude | int | 4 bytes | `0` to `10000` |

Struct format:

```python
MESSAGE_2_FORMAT = "!iibqqi"
```

Expected payload size:

```python
29 bytes
```

---

## 6. Serialization Rules

Implement `src/protocol/serializer.py`.

Required behavior:

- Use `struct.pack` and `struct.unpack`.
- Use network byte order.
- Encode strings as UTF-8.
- String fields must be exactly 25 bytes:
  - If shorter, right-pad with `\x00`.
  - If longer than 25 bytes, reject through validation before serialization.
- Decode strings by stripping trailing `\x00` and decoding UTF-8.
- Add a 4-byte length header before sending.
- Read exactly the required number of bytes when receiving.
- Support partial TCP reads correctly.
- TCP is stream-based, so never assume `recv()` returns one full message.

Implement helpers:

```python
def encode_fixed_string(value: str, size: int = 25) -> bytes: ...
def decode_fixed_string(value: bytes) -> str: ...
def pack_message(message: Message1 | Message2) -> bytes: ...
def unpack_payload(payload: bytes) -> Message1 | Message2: ...
def frame_payload(payload: bytes) -> bytes: ...
def read_exact(sock: socket.socket, size: int) -> bytes: ...
def receive_framed_message(sock: socket.socket) -> bytes: ...
```

Unknown message handling:
- If message ID is not `1` or `2`, raise/return a specific `UnknownMessageError`.
- If payload size is corrupt/truncated, raise/return a specific `ProtocolError`.

---

## 7. Validation Rules

Implement `src/protocol/validator.py`.

Validation must be strict and user-friendly.

For every field:
- Validate type.
- Validate range.
- Validate fixed message ID.
- Validate UTF-8 byte length for strings, not only character count.
- Return structured validation errors, not just strings.

Example:

```python
@dataclass
class ValidationError:
    field: str
    message: str
    min_value: int | None = None
    max_value: int | None = None
```

The UI must:
- Disable the Send button when validation fails.
- Show red border for invalid fields.
- Show helpful Turkish error text.
- Show string byte counter for `Adı` and `Soyadı`: `12/25 byte`.

---

## 8. Message Models

Implement `src/protocol/messages.py`.

Use dataclasses.

```python
@dataclass(frozen=True)
class Message1:
    message_id: int
    unit_reference_no: int
    first_name: str
    unit_no: int
    last_name: str
    rank: int

@dataclass(frozen=True)
class Message2:
    message_id: int
    unit_reference_no: int
    position_validity: int
    latitude: int
    longitude: int
    altitude: int
```

Also define:

```python
Message = Message1 | Message2
```

Create metadata structures for form generation:

```python
MESSAGE_DEFINITIONS = {
    1: [...],
    2: [...],
}
```

Each field metadata should include:
- UI label
- internal name
- type
- min/max where applicable
- whether editable
- dropdown options if applicable
- byte length if string

---

## 9. Auto-Response Logic

Implement `src/protocol/auto_response.py`.

Rules:

- If received Message 1:
  - Create and send Message 2.
- If received Message 2:
  - Create and send Message 1.
- If unknown message:
  - Do not auto-respond.
- If corrupt message:
  - Do not auto-respond.
- Auto-response must be toggleable from the UI.
- Auto-response messages must be tagged as `[Otomatik]` in logs.

Default auto-response payloads:

For Message 1:

```python
Message1(
    message_id=1,
    unit_reference_no=1001,
    first_name="Ali",
    unit_no=42,
    last_name="Yılmaz",
    rank=0,
)
```

For Message 2:

```python
Message2(
    message_id=2,
    unit_reference_no=2001,
    position_validity=1,
    latitude=23456789,
    longitude=17654321,
    altitude=1500,
)
```

---

## 10. Networking Layer

Create:

```text
src/network/server.py
src/network/client.py
src/network/handler.py
```

Server requirements:
- User enters port.
- Server binds and listens.
- Accept one active connection at a time.
- Show status:
  - `Bağlantı bekleniyor...`
  - `Bağlı`
  - `Bağlantı yok`
- Handle disconnect gracefully.
- Allow stopping server.

Client requirements:
- User enters IP and port.
- Client connects to server.
- Show status:
  - `Bağlanıyor...`
  - `Bağlı`
  - `Bağlantı yok`
- Handle failed connection with toast.
- Handle disconnect gracefully.

Shared handler:
- Send framed messages.
- Receive framed messages.
- Use a background thread for receiving.
- Use `queue.Queue` to communicate received events to the UI.
- Never directly modify UI from a network thread.
- Use locks where needed.
- Cleanly close sockets on app exit.

Event types:

```python
@dataclass
class NetworkEvent:
    type: Literal[
        "connected",
        "disconnected",
        "message_received",
        "message_sent",
        "unknown_message",
        "protocol_error",
        "error",
    ]
    payload: object | None
    timestamp: datetime
```

---

## 11. UI/UX Requirement — Professional Turkish Interface

Use CustomTkinter.

Design style:
- Dark theme.
- Modern engineering-dashboard look.
- Clear visual hierarchy.
- Rounded cards.
- Subtle borders.
- Clean spacing.
- No childish colors.
- No clutter.

Design tokens in `src/ui/theme.py`:

```python
COLORS = {
    "bg_primary": "#0F1419",
    "bg_secondary": "#1A2332",
    "bg_tertiary": "#243042",
    "bg_hover": "#2D3B4E",
    "accent_primary": "#00A88E",
    "accent_secondary": "#3B82F6",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_tertiary": "#64748B",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "border": "#334155",
    "transmit_bg": "#1E293B",
    "receive_bg": "#0F2922",
}
```

Typography:
- Headings: 16-20 px semibold
- Body: 13-14 px
- Monospace for timestamps and binary/protocol values
- All UI text Turkish

Window:
- Minimum size: 1100x720
- Resizable
- Default size: 1400x820

---

## 12. Multi-Instance Demo UX

The app must support a presentation-friendly default flow.

On launch, show a welcome screen:

Title:

```text
TCP Tactical Messenger
```

Subtitle:

```text
TCP/IP üzerinden ikili mesajlaşma, otomatik yanıt ve periyodik gönderim demo aracı
```

Quick start cards:

1. `Sunucu + İstemci (Otomatik Bağlan)`
2. `Sunucu + İstemci (Manuel)`
3. `Tek Sunucu`
4. `Tek İstemci`

Best demo mode:
`Sunucu + İstemci (Otomatik Bağlan)`

When clicked:
- Create server instance in left panel.
- Server listens on port `8080`.
- Create client instance in right panel.
- Client connects to `127.0.0.1:8080`.
- Both panels show `Bağlı`.
- User can immediately send messages.

Split view layout:

```text
┌──────────────────────────────────────────────────────────────────────┐
│ TCP Tactical Messenger                              [+ Yeni Instance] │
├──────────────────────────────┬───────────────────────────────────────┤
│ Instance 1 — Sunucu :8080    │ Instance 2 — İstemci → 127.0.0.1:8080 │
│ ● Bağlı                      │ ● Bağlı                               │
├──────────────────────────────┼───────────────────────────────────────┤
│ Mesaj Oluştur                │ Mesaj Oluştur                         │
│ [Mesaj 1] [Mesaj 2]          │ [Mesaj 1] [Mesaj 2]                   │
│ fields...                    │ fields...                             │
│ [Hızlı Doldur] [Gönder]      │ [Hızlı Doldur] [Gönder]               │
│                              │                                       │
│ Mesaj Geçmişi                │ Mesaj Geçmişi                         │
│ [time] Transmit Mesaj 1      │ [time] Receive Mesaj 1                │
│ [time] Receive Mesaj 2       │ [time] Transmit Mesaj 2 [Otomatik]    │
│                              │                                       │
│ Periyodik Gönderim           │ Periyodik Gönderim                    │
├──────────────────────────────┴───────────────────────────────────────┤
│ Shared Mesaj Detayı Paneli                                           │
└──────────────────────────────────────────────────────────────────────┘
```

Each instance must be independent:
- Own socket
- Own mode
- Own connection state
- Own message log
- Own compose form
- Own periodic sending
- Own auto-response toggle

Shared:
- Bottom message detail panel only.

Architecture:

```text
main.py
  -> AppShell
      -> InstanceManager
          -> Instance(server)
          -> Instance(client)
```

Create:

```text
src/instance.py
src/instance_manager.py
src/ui/welcome_screen.py
src/ui/split_view.py
```

Refactor `main_view.py` so it can be used as a reusable per-instance panel.

---

## 13. Compose Form

Each instance panel must include a `Mesaj Oluştur` card.

Features:
- Tabs/buttons: `Mesaj 1`, `Mesaj 2`
- Dynamic form fields based on selected message type
- `Hızlı Doldur` button
- `Gönder` button
- Validation state
- Error messages
- Disabled send button if invalid

Message 1 fields:
- Birlik Referans Numarası
- Adı
- Unit No
- Soyadı
- Rütbe dropdown

Message ID should be displayed but not editable:
- `Mesaj ID: 1`
- `Mesaj ID: 2`

Message 2 fields:
- Birlik Referans Numarası
- Birlik Konum Bilgisi Geçerliliği toggle
- Enlem
- Boylam
- Yükseklik

Use Turkish field labels exactly.

---

## 14. Message Log

Each instance panel must include a scrollable `Mesaj Geçmişi`.

Entry examples:

```text
[14:32:01.123] Transmit Mesaj 1
[14:32:01.456] Receive Mesaj 2 [Otomatik]
[14:32:03.012] Uyarı Tanımsız Mesaj ID: 99
[14:32:04.500] Hata Çözümlenemeyen mesaj
```

Visual rules:
- Transmit: blue accent
- Receive: green accent
- Auto-response: small `[Otomatik]` badge
- Unknown: warning accent
- Corrupt/protocol error: red accent
- Click any entry to show detail in shared bottom panel
- Auto-scroll unless user manually scrolled up

---

## 15. Message Detail Panel

Shared bottom panel.

When a log entry is clicked, show:

- Timestamp
- Direction: Transmit / Receive
- Message Type
- Auto-response status if applicable
- All decoded fields
- Human-readable labels

For Message 1:
- Mesaj ID
- Birlik Referans Numarası
- Adı
- Unit No
- Soyadı
- Rütbe: show both numeric code and label, e.g. `0 — Üsteğmen`

For Message 2:
- Mesaj ID
- Birlik Referans Numarası
- Birlik Konum Bilgisi Geçerliliği: show `Geçerli ✓` or `Geçersiz ✗`
- Enlem
- Boylam
- Yükseklik

For unknown/corrupt:
- Show raw metadata where possible
- Show clear warning/error text
- Do not crash

---

## 16. Periodic Sending Panel

Each instance must have a collapsible `Periyodik Gönderim` panel.

For each message type:

Message 1:
- Toggle ON/OFF
- Interval input
- Default: `100 ms`
- Min: `50 ms`
- Max: `10000 ms`
- Live sent counter
- Elapsed time

Message 2:
- Toggle ON/OFF
- Interval input
- Default: `500 ms`
- Min: `50 ms`
- Max: `10000 ms`
- Live sent counter
- Elapsed time

Also include:
- `Tümünü Durdur` button
- Pulsing indicator when active
- Periodic sending should use current form values if valid, otherwise Quick Fill defaults
- Periodic sending must stop when disconnected
- Periodic sending must stop when app closes

Implementation:
- Use background thread or scheduled loop.
- Ensure UI updates happen through queue/main thread.
- Avoid flooding UI so badly that it freezes.
- Keep log readable. If periodic messages become too many, use efficient appending.

---

## 17. Unknown Message Test Helper

Add a small developer/demo helper, hidden or placed under a collapsible `Test Araçları` section.

Feature:
- `Tanımsız Mesaj Gönder` button
- Sends a framed payload with Message ID `99`
- Receiver must show:
  - warning toast
  - warning log entry
  - no auto-response

Feature:
- `Bozuk Mesaj Gönder` button
- Sends intentionally truncated/corrupt framed payload
- Receiver must show:
  - error toast
  - error log entry
  - no crash
  - no auto-response

This helps prove requirement compliance during presentation.

---

## 18. Toast Notification System

Implement `src/ui/toast.py`.

Toasts:
- Top-right corner
- Auto-dismiss after 3 seconds
- Manual close button
- Types:
  - success
  - warning
  - error
  - info

Required messages:
- `Mesaj gönderildi`
- `Mesaj alındı`
- `Otomatik yanıt gönderildi: Mesaj 1`
- `Otomatik yanıt gönderildi: Mesaj 2`
- `Tanımlı olmayan mesaj alındı`
- `Hatalı mesaj alındı — çözümlenemedi`
- `Bağlantı kuruldu`
- `Bağlantı kesildi`
- `Sunucu başlatıldı`
- `Bağlantı kurulamadı`

---

## 19. Suggested Project Structure

Create this structure:

```text
tcp-tactical-messenger/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── app.py
│   ├── instance.py
│   ├── instance_manager.py
│   ├── network/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   ├── client.py
│   │   └── handler.py
│   ├── protocol/
│   │   ├── __init__.py
│   │   ├── messages.py
│   │   ├── serializer.py
│   │   ├── validator.py
│   │   ├── auto_response.py
│   │   └── errors.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── theme.py
│   │   ├── welcome_screen.py
│   │   ├── split_view.py
│   │   ├── main_view.py
│   │   ├── compose_form.py
│   │   ├── message_log.py
│   │   ├── detail_panel.py
│   │   ├── periodic_panel.py
│   │   ├── status_bar.py
│   │   └── toast.py
│   └── utils/
│       ├── __init__.py
│       ├── timestamp.py
│       └── defaults.py
├── tests/
│   ├── conftest.py
│   ├── test_serializer.py
│   ├── test_validator.py
│   ├── test_auto_response.py
│   ├── test_unknown_message.py
│   ├── test_framing.py
│   └── test_integration.py
├── docs/
│   ├── PROTOCOL.md
│   └── TEST_PLAN.md
├── build/
│   ├── build_macos.sh
│   └── build_windows.bat
├── assets/
│   └── icon.png
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── Makefile
├── README.md
├── .gitignore
└── .github/
    └── workflows/
        ├── ci.yml
        └── release.yml
```

---

## 20. Documentation Requirements

Create `docs/PROTOCOL.md`.

Include:
- Application purpose
- TCP framing rule
- Message 1 table
- Message 2 table
- Struct formats
- Validation constraints
- Auto-response behavior
- Unknown/corrupt message behavior

Create `docs/TEST_PLAN.md`.

Include:
- Unit test scenarios
- Integration test scenarios
- Manual system test scenarios
- Traceability matrix mapping requirements to tests

Manual system test scenarios:

```text
ST-01: Launch app and use automatic server-client demo mode.
ST-02: Send Message 1 manually and verify Message 2 auto-response.
ST-03: Send Message 2 manually and verify Message 1 auto-response.
ST-04: Enable periodic Message 1 sending at 100 ms.
ST-05: Enable periodic Message 2 sending at 500 ms.
ST-06: Try invalid field values and verify send button is disabled.
ST-07: Send unknown Message ID 99 and verify warning.
ST-08: Send corrupt/truncated payload and verify error handling.
ST-09: Disconnect peer and verify status update.
ST-10: Run 2-minute demo without crash or UI freeze.
```

---

## 21. Tests

Write meaningful tests.

Unit tests:
- Message 1 pack/unpack roundtrip
- Message 2 pack/unpack roundtrip
- Message 1 exact size = 64 bytes
- Message 2 exact size = 29 bytes
- Length header correctness
- UTF-8 Turkish characters:
  - `ğ`
  - `ş`
  - `ö`
  - `ü`
  - `ç`
  - `ı`
- Null padding correctness
- Reject string >25 bytes
- Boundary tests:
  - min
  - max
  - min-1
  - max+1
- Unknown message ID
- Corrupt/truncated payload

Integration tests:
- Server starts on localhost
- Client connects
- Client sends Message 1, server receives it
- Server sends Message 2, client receives it
- Unknown message produces warning event
- Disconnect produces disconnected event

Coverage:
- Protocol and validator modules should have at least 90% coverage.

---

## 22. Environment Setup

Create `Makefile`:

```makefile
.PHONY: setup run test lint lint-fix clean build

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

run:
	$(PYTHON) -m src.main

test:
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check src/ tests/

lint-fix:
	$(PYTHON) -m ruff check src/ tests/ --fix

clean:
	rm -rf dist/ build/ *.spec .pytest_cache .ruff_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build:
	$(PIP) install pyinstaller
	bash build/build_macos.sh
```

Create `.gitignore`:

```gitignore
.venv/
venv/
env/
dist/
build/
*.spec
__pycache__/
.pytest_cache/
.ruff_cache/
htmlcov/
*.pyc
coverage.xml
.coverage
.DS_Store
Thumbs.db
.vscode/
.idea/
```

---

## 23. CI/CD

Create `.github/workflows/ci.yml`.

CI should:
- Run on push to main
- Run on pull request to main
- Test Python 3.11 and 3.12
- Install runtime and dev dependencies
- Run Ruff
- Run pytest with coverage
- Enforce coverage on protocol/validator modules

Create `.github/workflows/release.yml`.

Release should:
- Run on tag push `v*`
- Run tests first
- Build macOS artifact using PyInstaller
- Build Windows artifact using PyInstaller
- Upload both artifacts to GitHub Release

---

## 24. README.md

Create a professional README.

Include:
- Title
- Badges
- Short description
- Screenshot placeholder
- Features
- Demo flow
- Message protocol tables
- Installation
- Running the app
- Quick demo with automatic server-client mode
- Running tests
- Building app
- Architecture
- Tech stack
- License

Use this project description:

```text
TCP Tactical Messenger is a native Python desktop application that demonstrates TCP/IP communication, binary message serialization, automatic response logic, and periodic transmission through a polished Turkish user interface.
```

---

## 25. Build Scripts

Create `build/build_macos.sh`:

```bash
#!/usr/bin/env bash
set -e

pyinstaller --onefile --windowed \
  --name "TCP Tactical Messenger" \
  --add-data "assets:assets" \
  src/main.py

cd dist
zip -r "TCP-Tactical-Messenger-macOS.zip" "TCP Tactical Messenger.app" || true
```

Create `build/build_windows.bat`:

```bat
pyinstaller --onefile --windowed ^
  --name "TCP Tactical Messenger" ^
  --add-data "assets;assets" ^
  src/main.py

cd dist
powershell Compress-Archive "TCP Tactical Messenger.exe" "TCP-Tactical-Messenger-Windows.zip"
```

---

## 26. Code Quality Rules

Follow:

- PEP 8
- Max line length 100
- Type hints on public functions
- Dataclasses for models/events
- No dead code
- No commented-out old code
- Small cohesive modules
- UI logic separated from protocol/networking logic
- Protocol layer must not import UI
- Network layer must not directly update UI
- Use queues/events between threads and UI
- Graceful shutdown on window close

---

## 27. Implementation Order

Implement in this order:

1. Project structure and dependency files
2. Message dataclasses
3. Validator
4. Serializer/framing
5. Unit tests for validator and serializer
6. Network server/client/handler
7. Basic single-instance UI
8. Message compose form
9. Message log and detail panel
10. Auto-response logic
11. Periodic sending
12. Unknown/corrupt message handling
13. Multi-instance split-view demo mode
14. Welcome screen
15. Test helper tools
16. Integration tests
17. Docs
18. README
19. CI/CD
20. Final polish and bug fixes

Do not stop after only generating files. Run tests, fix failures, and make the project runnable.

---

## 28. Acceptance Criteria

The final project is acceptable only if:

- App starts with `python -m src.main`.
- Automatic server-client demo works from a single click.
- Server and client connect on localhost.
- Message 1 can be sent and decoded.
- Message 2 can be sent and decoded.
- Receiving Message 1 triggers Message 2 response.
- Receiving Message 2 triggers Message 1 response.
- Auto-response does not create infinite ping-pong.
- Undefined Message ID shows a warning and does not crash.
- Corrupt payload shows an error and does not crash.
- Periodic Message 1 sending works at 100 ms.
- Periodic Message 2 sending works at 500 ms.
- Validation prevents invalid fields from being sent.
- UI looks polished and professional.
- Tests pass.
- README and protocol/test documentation exist.
- CI/CD workflow files exist.

Now inspect the current repository. If files already exist, modify/refactor carefully without breaking working functionality. If the repository is empty, create the full project from scratch. Implement the full application.
