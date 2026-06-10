# Protocol Bridge — Test Case Kataloğu

> Detaylı test case tanımları. Ana test planı: [TEST_PLAN.md](TEST_PLAN.md)

**Öncelik:** P1 = Kritik · P2 = Yüksek · P3 = Orta · P4 = Düşük

---

## Birim Testleri (UT)

| ID | Başlık | Öncelik | Önkoşul | Adımlar | Beklenen Sonuç | Otomatik |
|---|---|---|---|---|---|---|
| UT-01 | Mesaj 1 pack boyutu | P1 | — | Message1 pack | 64 byte payload | ✅ |
| UT-02 | Mesaj 2 pack boyutu | P1 | — | Message2 pack | 29 byte payload | ✅ |
| UT-03 | Mesaj 1 roundtrip | P1 | — | pack → unpack | Alanlar eşit | ✅ |
| UT-04 | Mesaj 2 roundtrip | P1 | — | pack → unpack | Alanlar eşit | ✅ |
| UT-05 | TCP framing | P1 | — | frame_payload | 4 byte header + payload | ✅ |
| UT-06 | UTF-8 Türkçe karakter | P2 | — | ğ,ş,ö,ü,ç,ı encode/decode | Kayıpsız | ✅ |
| UT-07 | Null padding | P2 | — | Kısa string pack | Null ile doldurulmuş | ✅ |
| UT-08 | Uzun string reddi | P1 | — | 26+ byte string | ValueError | ✅ |
| UT-09 | Bilinmeyen mesaj ID unpack | P1 | — | ID=99 payload | UnknownMessageError | ✅ |
| UT-10 | Truncate Mesaj 1 | P1 | — | Eksik payload | ProtocolError | ✅ |
| UT-11 | Truncate Mesaj 2 | P1 | — | Eksik payload | ProtocolError | ✅ |
| UT-12 | Validator sınır min/max M1 | P1 | — | unit_reference -1000/9999 | Geçerli/geçersiz | ✅ |
| UT-13 | Validator string byte M1 | P1 | — | 25/26 byte ad | Geçerli/hata | ✅ |
| UT-14 | Validator M2 unit ref | P1 | — | 0 ve 9999+ | 0 geçersiz | ✅ |
| UT-15 | Validator M2 altitude | P2 | — | 10000/10001 | Sınır testi | ✅ |
| UT-16 | build_message geçerli | P1 | — | Form dict | Message nesnesi | ✅ |
| UT-17 | build_message geçersiz | P1 | — | Hatalı dict | ValueError | ✅ |
| UT-18 | Auto-response M1→M2 | P1 | — | create_auto_response(M1) | Message2 | ✅ |
| UT-19 | Auto-response M2→M1 | P1 | — | create_auto_response(M2) | Message1 | ✅ |
| UT-20 | Döngü koruması | P1 | — | Ardışık auto-send | should_auto_respond=False | ✅ |
| UT-21 | Manuel gönderim suppression reset | P2 | — | manual send sonrası | Auto-response tekrar aktif | ✅ |
| UT-22 | field_range_hint | P3 | — | Her alan tipi | Anlamlı ipucu metni | ✅ |
| UT-23 | message_to_dict | P3 | — | M1/M2 | İngilizce etiket + rütbe TR | ✅ |
| UT-24 | Partial socket read | P2 | — | Mock socket | Tam okuma | ✅ |

---

## Entegrasyon Testleri (IT)

| ID | Başlık | Öncelik | Önkoşul | Adımlar | Beklenen Sonuç | Otomatik |
|---|---|---|---|---|---|---|
| IT-01 | Sunucu-istemci bağlantı | P1 | Port boş | Server start + client connect | connected event | ✅ |
| IT-02 | Mesaj 1 gönder/al | P1 | IT-01 | Client M1 gönder | Server alır, log | ✅ |
| IT-03 | Otomatik yanıt M1→M2 | P1 | Auto reply açık | M1 gönder | M2 otomatik döner | ✅ |
| IT-04 | Bilinmeyen mesaj event | P1 | Bağlı | Raw ID 99 gönder | unknown_message event | ✅ |
| IT-05 | Disconnect event | P1 | Bağlı | Bağlantı kes | disconnected event | ✅ |
| IT-06 | Framing uçtan uca | P1 | Bağlı | Framed binary gönder | Doğru unpack | ✅ |

---

## Sistem / UI Testleri (ST)

| ID | Başlık | Öncelik | Önkoşul | Adımlar | Beklenen Sonuç | Otomatik |
|---|---|---|---|---|---|---|
| ST-01 | Uygulama açılışı | P1 | Exe/python | Uygulamayı başlat | Home sekmesi, mod kartları | ❌ Manuel |
| ST-02 | Otomatik bağlantı modu | P1 | ST-01 | Auto Connect seç | İki panel, Connected | ❌ |
| ST-03 | Manuel bağlantı | P1 | ST-01 | Manual → Start Server → Connect | Her iki panel Connected | ❌ |
| ST-04 | Sunucu Only modu | P2 | ST-01 | Server Only seç | Tek sunucu paneli | ❌ |
| ST-05 | İstemci Only modu | P2 | ST-01 | Client Only seç | Tek istemci paneli | ❌ |
| ST-06 | Sekme kapatma Home reset | P2 | Workspace açık | Home sekmesini kapat | Welcome ekranı | ❌ |
| ST-07 | + Instance yeni sekme | P2 | ST-01 | + Instance tıkla | Instance seçici sekmesi | ❌ |
| ST-08 | Mesaj 1 manuel gönderim | P1 | Bağlı | Form doldur → Send | Log Transmit, toast | ❌ |
| ST-09 | Mesaj 2 manuel gönderim | P1 | Bağlı | M2 form → Send | Log Transmit | ❌ |
| ST-10 | Otomatik yanıt çapraz | P1 | Auto Reply ON | M1 gönder | Karşı panel M2 [Auto] | ❌ |
| ST-11 | Otomatik yanıt kapalı | P1 | Auto Reply OFF | M1 gönder | Tek yönlü, karşı yanıt yok | ❌ |
| ST-12 | Form byte sayacı | P2 | M1 seçili | 26 byte Türkçe ad | Kırmızı sayaç, Send disabled | ❌ |
| ST-13 | Form aralık doğrulama | P2 | M1 seçili | unit_ref 99999 | Hata metni, Send disabled | ❌ |
| ST-14 | Quick Fill | P3 | Form boş | Quick Fill | Varsayılan değerler | ❌ |
| ST-15 | Periyodik M1 gönderim | P2 | Bağlı | Periodic aç, M1 switch ON | Sayaç artar, [Periodic] log | ❌ |
| ST-16 | Periyodik toast yok | P2 | ST-15 | Periyodik çalışırken gözlem | Toast spam yok | ❌ |
| ST-17 | Periyodik disconnect dur | P2 | ST-15 aktif | Disconnect | Periyodik durur | ❌ |
| ST-18 | Unknown Message test | P2 | Bağlı | Test Tools → Unknown | Warning log + toast | ❌ |
| ST-19 | Corrupt Message test | P2 | Bağlı | Test Tools → Corrupt | Error log + toast | ❌ |
| ST-20 | Log detay paneli | P3 | Mesaj alındı | Log satırına tıkla | Alt panel detay | ❌ |
| ST-21 | Bağlantı kesme UI | P1 | Bağlı | Disconnect / Stop Server | Not connected / Waiting | ❌ |
| ST-22 | Çoklu sekme paralel | P2 | — | 2 workspace farklı port | Bağımsız çalışır | ❌ |
| ST-23 | İkinci client sunucuya | P1 | Server+Client1 bağlı | Yeni sekme Client2 aynı port | Client1 disconnect UI, Client2 connected | ❌ |
| ST-24 | Rütbe dropdown TR | P3 | M1 form | Rank aç | Üsteğmen/Teğmen/Asteğmen | ❌ |
| ST-25 | UI stabilite 2 dk | P2 | Auto mod | 2 dk mesaj alışverişi | Donma/çökme yok | ❌ |
| ST-26 | Exe build çalıştırma | P2 | Build alınmış | dist exe çalıştır | Uygulama açılır | ❌ |

---

## Gereksinim İzlenebilirlik Özeti

| Gereksinim ID | Açıklama | Test Case'ler |
|---|---|---|
| REQ-01 | Binary serileştirme M1/M2 | UT-01–04, IT-06 |
| REQ-02 | TCP length-prefix framing | UT-05, IT-06, UT-24 |
| REQ-03 | UTF-8 / Türkçe karakter | UT-06, UT-07, ST-12 |
| REQ-04 | Alan doğrulama | UT-11–17, ST-13 |
| REQ-05 | Otomatik yanıt M1↔M2 | UT-18–19, IT-03, ST-10–11 |
| REQ-06 | Ping-pong önleme | UT-20–21 |
| REQ-07 | Bilinmeyen mesaj toleransı | UT-09, IT-04, ST-18 |
| REQ-08 | Bozuk mesaj toleransı | UT-10–11, ST-19 |
| REQ-09 | Periyodik gönderim | ST-15–17 |
| REQ-10 | Çoklu instance / sekmeler | ST-06–07, ST-22 |
| REQ-11 | Tek client sunucu politikası | ST-23 |
| REQ-12 | Bağlantı durumu UI senkronu | ST-21, ST-23, IT-05 |
| REQ-13 | İngilizce UI + TR rütbe | ST-24 |
| REQ-14 | Windows/macOS build | ST-26 |
