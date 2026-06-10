# TCP Tactical Messenger — Test Plan

Bu doküman case study kapsamındaki gereksinimlere göre test akışını özetler.

---

## Özet Manuel Test Akışı (~15 dk)

Aşağıdaki sırayı izleyerek uygulamayı uçtan uca doğrulayabilirsiniz.

### 1. Başlangıç & Sekmeler (ST-01)

1. Uygulamayı aç → **Ana Sayfa** sekmesi ve mod kartları görünmeli.
2. **Sunucu + İstemci (Otomatik)** seç → aynı sekme çalışma alanına dönmeli, sekme adı **Otomatik Bağlantı** olmalı.
3. Sunucu ve istemci **Bağlı** durumuna geçmeli.
4. Sekmeyi kapat (× veya sağ tık) → **Ana Sayfa** hoş geldin ekranına dönmeli.
5. **+ Instance** → yeni **Instance** sekmesi; mod seç → sekme adı moda göre değişmeli.
6. Instance sekmesini kapat → Ana Sayfa sekmesine geçilmeli.

### 2. Manuel Bağlantı

1. Ana Sayfa → **Sunucu + İstemci (Manuel)**.
2. Sol panel: **Sunucuyu Başlat** (8080).
3. Sağ panel: **Bağlan** (`127.0.0.1:8080`).
4. Her iki panelde **Bağlı** ve toast: *Bağlantı kuruldu*.

### 3. Mesaj Gönderimi & Otomatik Yanıt (ST-02, ST-03)

1. Otomatik modda veya manuel bağlantıda **Mesaj 1** formunu doldur → **Gönder**.
2. Logda Transmit + Receive satırları; karşı panelde **Mesaj 2** otomatik yanıt (`[Otomatik]`).
3. **Mesaj 2** gönder → **Mesaj 1** otomatik yanıt gelmeli.
4. **Otomatik Yanıt** anahtarını kapat → tek yönlü gönderim; otomatik karşı mesaj gelmemeli.

### 4. Form Doğrulama (ST-06)

1. Ad alanına 26+ byte Türkçe karakter gir → Gönder pasif, byte sayacı kırmızı.
2. Birlik referans numarasına geçersiz değer → hata metni ve pasif Gönder.

### 5. Periyodik Gönderim (ST-04, ST-05)

1. Bağlantı kurulu iken **▶ Periyodik Gönderim** aç.
2. Mesaj 1 anahtarını aç → **Gönderilen** sayacı artmalı; logda `[Periyodik]` satırları.
3. Toast spam olmamalı.
4. Bağlantı kesilince periyodik gönderim durmalı.

### 6. Test Araçları (ST-07, ST-08)

1. **▶ Test Araçları** aç.
2. **Tanımsız Mesaj** → logda uyarı, toast: tanımsız mesaj.
3. **Bozuk Mesaj** → logda hata, toast: hatalı mesaj.

### 7. Bağlantı Kesme & Stabilite (ST-09, ST-10)

1. **Bağlantıyı Kes** / **Sunucuyu Durdur** → durum güncellenmeli.
2. Otomatik modda 2 dk mesaj alışverişi → UI donmamalı, çökme olmamalı.

---

## Otomatik Testler (pytest)

| ID | Senaryo | Modül |
|---|---|---|
| UT-01 | Mesaj 1 pack/unpack | serializer |
| UT-02 | Mesaj 2 pack/unpack | serializer |
| UT-03–08 | Boyut, framing, UTF-8, padding | serializer |
| UT-09 | Sınır doğrulama | validator |
| UT-10–11 | Bilinmeyen ID, bozuk payload | serializer |
| UT-12–13 | Otomatik yanıt eşlemesi, döngü koruması | auto_response |
| IT-01–06 | TCP bağlantı, gönder/al, otomatik yanıt, disconnect | integration |

Çalıştırma:

```bash
python -m pytest tests/ -v --cov=src/protocol --cov-report=term-missing
```

---

## Gereksinim İzlenebilirlik Matrisi

| Gereksinim | Testler |
|---|---|
| Binary serileştirme | UT-01–08, IT-03 |
| Alan doğrulama | UT-09, ST-06 |
| Otomatik yanıt | UT-12, IT-04, ST-02–03 |
| Döngü önleme | UT-13 |
| Bilinmeyen mesaj | UT-10, IT-05, ST-07 |
| Bozuk mesaj | UT-11, ST-08 |
| TCP framing | UT-05, framing tests |
| Periyodik gönderim | ST-04–05 |
| Çoklu instance / sekmeler | ST-01 |
| Bağlantı kesme | IT-06, ST-09 |
| UI stabilitesi | ST-10 |

---

## Kapsam Dışı (test edilmez)

- Gerçek ağ keşfi / sandbox topoloji haritası
- Çoklu makine dağıtık senaryolar (yalnızca localhost)
- Üretim düzeyi güvenlik (TLS, kimlik doğrulama)
