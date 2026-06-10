# Protocol Bridge — Test Planı (Test Plan)

| Alan | Değer |
|---|---|
| **Proje** | Protocol Bridge — TCP Binary Messaging Platform |
| **Doküman** | TEST_PLAN.md |
| **Versiyon** | 2.0 |
| **Tarih** | 10 Haziran 2026 |
| **Hazırlayan** | QA / Test Mühendisliği |
| **Durum** | Onay için hazır |

---

## Revizyon Geçmişi

| Versiyon | Tarih | Değişiklik |
|---|---|---|
| 1.0 | — | İlk taslak (Protokol Köprüsü, kısa manuel akış) |
| 2.0 | 10.06.2026 | Protocol Bridge rebrand; kapsamlı test stratejisi, case kataloğu, izlenebilirlik, CI entegrasyonu, çoklu client senaryoları |

---

## 1. Giriş ve Amaç

Bu doküman, **Protocol Bridge** masaüstü uygulamasının kalite güvence sürecinde kullanılacak resmi test planıdır. Amaç:

- Fonksiyonel ve protokol gereksinimlerinin eksiksiz doğrulanması
- Regresyon riskinin ölçülebilir şekilde yönetilmesi
- Otomatik ve manuel testlerin tek çatı altında tanımlanması
- Gereksinim → test case izlenebilirliğinin sağlanması
- CI/CD pipeline ile uyumlu kalite kapılarının (quality gate) belgelenmesi

**Hedef kitle:** Test mühendisleri, geliştiriciler, teknik mülakat / case study sunumları.

---

## 2. Kapsam

### 2.1 Kapsam İçi (In Scope)

| Alan | Detay |
|---|---|
| Protokol katmanı | Mesaj 1 (64 B), Mesaj 2 (29 B), TCP framing, UTF-8 |
| Doğrulama | Alan sınırları, byte sayacı, Send butonu kilidi |
| Ağ | Sunucu/istemci, tek aktif client, disconnect, localhost |
| Otomatik yanıt | M1↔M2, toggle, döngü koruması |
| Periyodik gönderim | M1 100 ms / M2 500 ms varsayılan, toast davranışı |
| UI | Sekmeler, formlar, log, detay paneli, test araçları |
| Build | Windows exe, macOS dmg (smoke) |
| CI | Ruff + pytest + %90 protocol coverage |

### 2.2 Kapsam Dışı (Out of Scope)

- TLS / kimlik doğrulama / şifreleme
- Çoklu makine (WAN) dağıtık senaryolar
- Yük testi (1000+ eşzamanlı bağlantı)
- Gerçek GPS donanım entegrasyonu
- App Store / code signing detayları

---

## 3. Referans Dokümanlar

| Doküman | Açıklama |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Binary protokol spesifikasyonu |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Sistem mimarisi |
| [TEST_CASES.md](TEST_CASES.md) | Detaylı test case kataloğu |
| [TEST_REPORT.md](TEST_REPORT.md) | Son test koşturması raporu |
| [README.md](../README.md) | Kurulum ve hızlı başlangıç |

---

## 4. Test Stratejisi

### 4.1 Test Piramidi

```
                    ┌─────────────┐
                    │  ST (UI)    │  ~26 manuel case
                    ├─────────────┤
                    │  IT (TCP)   │  6 otomatik
                    ├─────────────┤
                    │  UT (Proto) │  24 otomatik
                    └─────────────┘
```

- **Birim (UT):** Saf protokol mantığı — hızlı, deterministik, CI'da zorunlu
- **Entegrasyon (IT):** Gerçek TCP socket ile sunucu-istemci etkileşimi
- **Sistem (ST):** CustomTkinter UI, çoklu sekme, kullanıcı akışları — manuel + smoke

### 4.2 Test Türleri

| Tür | Araç | Sıklık |
|---|---|---|
| Birim | pytest | Her commit (CI) |
| Entegrasyon | pytest + socket | Her commit (CI) |
| Lint | Ruff | Her commit (CI) |
| Manuel UI | Checklist (TEST_CASES ST-*) | Release öncesi |
| Regression | UT + IT tam suite + kritik ST | Her release |
| Smoke | ST-01, ST-02, ST-26 | Build sonrası |

### 4.3 Risk Tabanlı Önceliklendirme

| Risk | Etki | Olasılık | Mitigasyon |
|---|---|---|---|
| Protokol uyumsuzluğu | Yüksek | Orta | UT-01–11, IT-06 |
| Veri bozulması (UTF-8) | Yüksek | Orta | UT-06, ST-12 |
| Ping-pong döngüsü | Orta | Orta | UT-20, ST-10 |
| UI durum senkronu | Yüksek | Orta | ST-21, ST-23 |
| İkinci client eski UI | Orta | Yüksek | ST-23 (regression) |
| Coverage düşüşü | Orta | Orta | CI `--cov-fail-under=90` |

---

## 5. Test Ortamı

### 5.1 Donanım / Yazılım

| Bileşen | Gereksinim |
|---|---|
| OS | Windows 10/11 (birincil), macOS (build smoke) |
| Python | 3.11, 3.12 (CI matrix) |
| Bağımlılıklar | `requirements.txt`, `requirements-dev.txt` |
| Ağ | localhost (127.0.0.1), firewall izinli |

### 5.2 Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m src.main            # Geliştirme modu
```

### 5.3 CI Ortamı

- **Platform:** `ubuntu-latest`
- **Tetikleyici:** `push` / `pull_request` → `main`
- **Adımlar:** checkout → Python matrix → pip install → Ruff → pytest + coverage

---

## 6. Giriş ve Çıkış Kriterleri

### 6.1 Teste Giriş (Entry Criteria)

- [ ] Kaynak kod `main` branch'te build edilebilir durumda
- [ ] Bağımlılıklar `requirements*.txt` ile tanımlı
- [ ] Protokol spesifikasyonu (PROTOCOL.md) güncel
- [ ] Test ortamı kurulu

### 6.2 Testten Çıkış (Exit Criteria)

- [ ] Tüm UT ve IT testleri geçiyor (48/48)
- [ ] `src/protocol` coverage ≥ %90
- [ ] Ruff lint hatasız
- [ ] Kritik manuel testler (ST-01, ST-02, ST-08, ST-10, ST-21, ST-23) PASS
- [ ] Bilinen P1 açık defect yok
- [ ] TEST_REPORT.md güncel

---

## 7. Otomatik Test Envanteri

### 7.1 Test Dosyaları

| Dosya | Test Sayısı | Kapsam |
|---|---|---|
| `test_serializer.py` | 13 | Pack/unpack, framing, UTF-8 |
| `test_validator.py` | 11 | Alan doğrulama, build_message |
| `test_auto_response.py` | 7 | Yanıt eşlemesi, döngü koruması |
| `test_integration.py` | 4 | TCP bağlantı, gönder/al, disconnect |
| `test_framing.py` | 3 | Socket okuma, partial read |
| `test_unknown_message.py` | 2 | Bilinmeyen ID |
| `test_messages.py` | 8 | Metadata, dict, hint |
| **Toplam** | **48** | |

### 7.2 Çalıştırma Komutları

```bash
# CI ile aynı
python -m ruff check src/ tests/
python -m pytest tests/ -v \
  --cov=src/protocol \
  --cov-report=term-missing \
  --cov-fail-under=90

# HTML rapor
python -m pytest tests/ --cov=src/protocol --cov-report=html:htmlcov
```

---

## 8. Manuel Test Senaryoları (Özet Akış)

> Tam adım/beklenti tabloları: [TEST_CASES.md](TEST_CASES.md)

### 8.1 Hızlı Smoke (~5 dk)

1. Uygulamayı aç → Home + mod kartları (ST-01)
2. Auto Connect → iki panel Connected (ST-02)
3. M1 gönder → M2 auto yanıt (ST-10)
4. Disconnect → durum güncellenir (ST-21)

### 8.2 Tam Regresyon (~45 dk)

Tüm ST-01 — ST-26 case'leri sırayla veya gruplar halinde:

| Grup | Case ID | Süre (tahmini) |
|---|---|---|
| Sekme & mod | ST-01–07 | 8 dk |
| Mesajlaşma | ST-08–11 | 10 dk |
| Form & doğrulama | ST-12–14 | 5 dk |
| Periyodik | ST-15–17 | 5 dk |
| Hata senaryoları | ST-18–19 | 3 dk |
| Bağlantı & çoklu | ST-20–23 | 10 dk |
| UI & stabilite | ST-24–25 | 4 dk |
| Build smoke | ST-26 | 2 dk |

### 8.3 Kritik Senaryo: İkinci Client (ST-23)

**Amaç:** Sunucunun tek client politikası ve UI senkronu.

1. Sekme A: Server Only → Start Server `:8080`
2. Sekme B: Client Only → Connect `127.0.0.1:8080` → **Connected**
3. Sekme C: Client Only → Connect `127.0.0.1:8080`
4. **Beklenen:**
   - Sekme B client: **Not connected** (yeşil takılı kalmamalı)
   - Sekme C client: **Connected**
   - Sekme A server: **Connected** (yeni client)

---

## 9. Gereksinim İzlenebilirlik Matrisi

| REQ | Gereksinim | UT | IT | ST |
|---|---|---|---|---|
| REQ-01 | Binary M1/M2 | 01–04 | 06 | 08–09 |
| REQ-02 | TCP framing | 05 | 06 | — |
| REQ-03 | UTF-8 TR | 06–07 | — | 12, 26 |
| REQ-04 | Validasyon | 11–17 | — | 13 |
| REQ-05 | Auto yanıt | 18–19 | 03 | 10–11 |
| REQ-06 | Döngü önleme | 20–21 | — | 10 |
| REQ-07 | Unknown msg | 09 | 04 | 18 |
| REQ-08 | Corrupt msg | 10–11 | — | 19 |
| REQ-09 | Periyodik | — | — | 15–17 |
| REQ-10 | Çoklu sekme | — | — | 06–07, 22 |
| REQ-11 | Tek client | — | — | 23 |
| REQ-12 | UI durum sync | — | 05 | 21, 23 |
| REQ-13 | UI dil / rütbe | 23 | — | 24 |
| REQ-14 | Build | — | — | 26 |

---

## 10. Defect Yönetimi

| Öncelik | Tanım | SLA (öneri) |
|---|---|---|
| P1 — Blocker | Uygulama çöker, veri kaybı, protokol kırılır | Hemen |
| P2 — Major | Ana özellik çalışmaz, workaround yok | 1 sprint |
| P3 — Minor | Workaround var, kozmetik | Backlog |
| P4 — Trivial | Metin, hizalama | İsteğe bağlı |

**Örnek kapatılan defect:** Eski client disconnect sonrası UI "Connected" gösteriyordu → `handle_network_event` + server listening durumu düzeltildi (ST-23).

---

## 11. Regression Stratejisi

Her merge / release öncesi:

1. CI pipeline yeşil (Ruff + 48 pytest + coverage)
2. ST-23 (ikinci client) manuel doğrulama
3. Build smoke (ST-26)

---

## 12. Roller ve Sorumluluklar

| Rol | Sorumluluk |
|---|---|
| Geliştirici | UT/IT yazımı, CI fix, code review |
| QA / Test | ST execution, TEST_REPORT güncelleme, defect triage |
| Tech Lead | Exit criteria onayı, release kararı |

---

## 13. Ekler

- **Ek A:** [TEST_CASES.md](TEST_CASES.md) — Tam test case kataloğu
- **Ek B:** [TEST_REPORT.md](TEST_REPORT.md) — Son koşturma metrikleri
- **Ek C:** `htmlcov/index.html` — HTML coverage raporu (lokal üretim)

---

## 14. Sunum Notları (Mülakat İçin)

1. **Test piramidi** ile protokol katmanını otomatikleştirip UI'ı manuel tuttuk — maliyet/ güvenilirlik dengesi.
2. **Coverage gate %90** yalnızca `src/protocol` — iş mantığının çekirdeği; UI thread testleri kapsam dışı (CustomTkinter mock maliyeti yüksek).
3. **ST-23** gerçek kullanıcı bug'ından türetilmiş regression case — tek client politikası + UI sync.
4. **İzlenebilirlik matrisi** REQ → test ID ile audit-ready.
5. **CI matrix** Python 3.11/3.12 — sürüm uyumluluğu.
