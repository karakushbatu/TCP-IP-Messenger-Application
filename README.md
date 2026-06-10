# TCP Tactical Messenger

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

TCP/IP üzerinden binary mesajlaşmayı gösteren, Türkçe arayüzlü masaüstü uygulaması. Sunucu/istemci modları, otomatik yanıt, periyodik gönderim ve çoklu instance sekmeleri tek uygulamada bir arada.

## Özellikler

- **Instance sekmeleri** — Ana Sayfa + `+ Instance` ile birden fazla sunucu/istemci oturumu
- **Dört başlangıç modu** — Otomatik, Manuel, Yalnız Sunucu, Yalnız İstemci
- **Binary protokol** — Mesaj 1 (Personel, 64 B) ve Mesaj 2 (Konum, 29 B), length-prefixed TCP framing
- **Otomatik yanıt** — Mesaj 1 ↔ Mesaj 2 çapraz yanıt, döngü koruması ile
- **Periyodik gönderim** — 100 ms / 500 ms varsayılan aralıklar (toast göstermez)
- **Doğrulama** — Alan sınırları, byte sayacı, geçersiz veride gönder butonu kapalı
- **Test araçları** — Tanımsız ID ve bozuk paket gönderimi
- **Mesaj geçmişi & detay** — Log satırına tıklayınca alt panelde tam içerik

## Hızlı Başlangıç

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python -m src.main
```

Uygulama açıldığında **Ana Sayfa** sekmesi görünür. Bir mod seçildiğinde sekme çalışma alanına dönüşür; kapatıldığında tekrar hoş geldin ekranına döner.

## Arayüz

| Bölüm | Açıklama |
|---|---|
| Ana Sayfa | Mod seçim ekranı (ilk açılış) |
| + Instance | Yeni instance seçici sekmesi |
| Sekme kapatma | × veya sağ tık → Sekmeyi Kapat |
| Otomatik Yanıt | Gelen mesaja protokole uygun karşı mesaj üretir (demo amaçlı) |

## Mesaj Protokolü

### Mesaj 1 — Personel (64 byte)

| Alan | Tip | Kısıt |
|---|---|---|
| Mesaj ID | int32 | `1` |
| Birlik Referans Numarası | int32 | `-1000` … `9999` |
| Adı | string(25) | UTF-8, null-padded |
| Unit No | uint32 | `0` … `4294967295` |
| Soyadı | string(25) | UTF-8, null-padded |
| Rütbe | int16 | `0–2` |

### Mesaj 2 — Birlik Konumu (29 byte)

| Alan | Tip | Kısıt |
|---|---|---|
| Mesaj ID | int32 | `2` |
| Birlik Referans Numarası | int32 | `1` … `9999` |
| Geçerlilik | byte | `0/1` |
| Enlem | int64 | `-32400000` … `32400000` |
| Boylam | int64 | `-64800000` … `64800000` |
| Yükseklik | int32 | `0` … `10000` |

Detaylı spesifikasyon: [docs/PROTOCOL.md](docs/PROTOCOL.md)

## Test

### Otomatik testler

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

### Manuel test akışı

Kapsam içi senaryoların özeti: [docs/TEST_PLAN.md](docs/TEST_PLAN.md)

## Derleme (Windows / macOS)

```bash
pip install -r requirements-dev.txt

# Windows → dist/TCP Tactical Messenger.exe
build\build_windows.bat

# macOS → dist/*.dmg (+ zip yedek)
bash build/build_macos.sh
```

## Mimari

```
main.py → AppShell → SplitView (sekmeler)
                    → InstanceManager → Instance (server | client)
                         ├── protocol/  (messages, serializer, validator, auto_response)
                         ├── network/   (server, client, handler)
                         └── ui/        (compose, log, periodic, detail)
```

## Teknoloji

- Python 3.11+
- CustomTkinter
- `socket`, `threading`, `queue`
- `struct` (binary serialization)
- pytest, Ruff, PyInstaller

## Release

GitHub Actions ile tag push sonrası otomatik build yapılır. **Yeni release yalnızca açık onay sonrası yayınlanmalıdır.**

## Lisans

MIT
