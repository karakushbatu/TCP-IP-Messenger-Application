# Protocol Bridge — Mimari Dokümantasyon

## Genel Bakış

Protocol Bridge, Python 3.11+ ve CustomTkinter ile geliştirilmiş tek pencere masaüstü uygulamasıdır. TCP/IP üzerinden ikili (binary) mesajlaşmayı gösterir; sunucu/istemci modları, otomatik yanıt, periyodik gönderim ve çoklu instance sekmeleri desteklenir.

## Katmanlı Yapı

```
┌─────────────────────────────────────────────────────────┐
│  UI Layer (CustomTkinter)                               │
│  SplitView · WelcomeScreen · InstancePanel · Forms      │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Application Layer                                      │
│  Instance · InstanceManager                             │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Network Layer                                          │
│  TcpServer · TcpClient · ConnectionHandler              │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Protocol Layer                                         │
│  serializer · validator · messages · auto_response      │
└─────────────────────────────────────────────────────────┘
```

## Bileşenler

| Bileşen | Sorumluluk |
|---|---|
| `AppShell` | Ana pencere, tema, yaşam döngüsü |
| `SplitView` | Sekme yönetimi, event polling (50 ms) |
| `WelcomeScreen` | Mod seçimi, hoş geldin ekranı |
| `InstancePanel` | Bağlantı, form, log, periyodik, test araçları |
| `Instance` | Tek sunucu veya istemci oturumu |
| `InstanceManager` | Demo modlarına göre instance çifti/tekli kurulum |
| `TcpServer` | Tek aktif bağlantı, accept döngüsü |
| `TcpClient` | Uzak sunucuya bağlanma |
| `ConnectionHandler` | Send/receive, framing, auto-response tetikleme |

## Event Akışı

1. Ağ işlemleri arka plan thread'lerinde çalışır
2. Olaylar `queue.Queue[NetworkEvent]` ile ana thread'e aktarılır
3. `SplitView._poll_events` (50 ms) kuyruğu boşaltır
4. `InstancePanel.handle_network_event` UI'ı günceller

## Çoklu Instance Modeli

- **Home** sekmesi: hoş geldin ekranı; kapatılınca reset
- **+ Instance**: yeni seçici sekme
- Workspace sekmeleri: sunucu/istemci panelleri yan yana veya tek panel

## Build & Dağıtım

| Platform | Komut | Çıktı |
|---|---|---|
| Windows | `build\build_windows.bat` | `dist/Protocol Bridge.exe` |
| macOS | `bash build/build_macos.sh` | `dist/Protocol-Bridge-macOS.dmg` |

PyInstaller one-file, windowed mod.

## CI/CD

GitHub Actions (`ci.yml`):

- Ruff lint (`src/`, `tests/`)
- pytest + `src/protocol` coverage ≥ %90
- Python 3.11 ve 3.12 matrix

Release workflow ayrı (`release.yml`); tag push ile Windows ZIP + macOS DMG.
