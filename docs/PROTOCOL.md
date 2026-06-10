# Protocol Bridge — Protokol Spesifikasyonu

## Uygulama Amacı

**Protocol Bridge**, TCP/IP üzerinden ikili (binary) mesajlaşmayı gösteren bir masaüstü uygulamasıdır. İki tanımlı mesaj tipi, otomatik çapraz yanıt, periyodik gönderim, çoklu instance sekmeleri ve katı alan doğrulaması desteklenir.

## TCP/IP Bağlantısı — IP Ne Anlama Gelir?

**TCP/IP** iki katmandan oluşur:

| Katman | Rol | Bu projede |
|---|---|---|
| **IP** | Paketin *hangi makineye* gideceğini belirler (adres) | Client panelindeki IP alanı |
| **TCP** | O makinede *hangi uygulamanın* dinlediğini belirler (port) | Sunucu/istemci portu (örn. 8080) |

**IP adresi**, ağdaki bir bilgisayarın kimliğidir. Client bağlanırken hedef makinenin IP'sini yazar; sunucu ise `0.0.0.0` ile tüm ağ arayüzlerinde dinler.

| IP | Anlam | Ne olur? |
|---|---|---|
| `127.0.0.1` | Loopback — *aynı bilgisayar* | Sunucu ve client aynı makinede çalışırken kullanılır (Auto/Manual demo) |
| `192.168.x.x` | Yerel ağdaki başka bir cihaz | Aynı Wi‑Fi/LAN'daki başka PC'ye bağlanırsın |
| `0.0.0.0` (sunucu bind) | Tüm arayüzlerde dinle | Dışarıdan gelen bağlantıları da kabul eder |

Farklı IP yazarsan client **o adresteki makinede** çalışan sunucuya bağlanmaya çalışır. IP yanlışsa veya karşı tarafta sunucu yoksa bağlantı başarısız olur; mesajlar gitmez. Port da eşleşmeli (örn. her iki tarafta 8080).

## TCP Çerçeveleme Kuralı

Her mesaj kablo üzerinde uzunluk önekli (length-prefix) çerçeve ile gider:

```
[4 bayt uzunluk başlığı][ikili mesaj gövdesi]
```

- Başlık formatı: `!I` (unsigned int, network byte order, big-endian)
- Uzunluk değeri = yalnızca gövde boyutu (4 baytlık başlık hariç)
- Alıcı, başlıktan sonra tam olarak `length` bayt okumalıdır

## Mesaj 1 — Personel Mesajı (64 bayt)

| Alan | Dahili Ad | Tip | Boyut | Kısıt |
|---|---|---:|---:|---|
| Mesaj ID | message_id | int32 | 4 | sabit `1` |
| Birlik Referans No | unit_reference_no | int32 | 4 | `-1000` – `9999` |
| Ad | first_name | string | 25 | UTF-8, null ile doldurulmuş |
| Birlik No | unit_no | uint32 | 4 | `0` – `4294967295` |
| Soyad | last_name | string | 25 | UTF-8, null ile doldurulmuş |
| Rütbe | rank | int16 | 2 | `0=Üsteğmen`, `1=Teğmen`, `2=Asteğmen` |

Struct formatı: `!ii25sI25sh`

## Mesaj 2 — Birlik Konum Mesajı (29 bayt)

| Alan | Dahili Ad | Tip | Boyut | Kısıt |
|---|---|---:|---:|---|
| Mesaj ID | message_id | int32 | 4 | sabit `2` |
| Birlik Referans No | unit_reference_no | int32 | 4 | `1` – `9999` |
| Konum Geçerli | position_validity | byte | 1 | `1=True`, `0=False` |
| Enlem | latitude | int64 | 8 | `-32400000` – `32400000` |
| Boylam | longitude | int64 | 8 | `-64800000` – `64800000` |
| İrtifa | altitude | int32 | 4 | `0` – `10000` |

Struct formatı: `!iibqqi`

## Doğrulama Kuralları

- Tüm tamsayılar tanımlı aralıkta olmalıdır
- String alanları UTF-8 bayt uzunluğuna göre doğrulanır (maks. 25 bayt)
- Mesaj ID, seçilen mesaj tipi ile eşleşmelidir
- Geçersiz mesajlar UI'dan gönderilemez (Send butonu devre dışı)

## Otomatik Yanıt Davranışı

- Mesaj 1 alındığında → otomatik Mesaj 2 gönderilir
- Mesaj 2 alındığında → otomatik Mesaj 1 gönderilir
- Döngü koruması: otomatik gönderim sonrası ping-pong engellenir
- Otomatik yanıt UI'dan kapatılabilir (Auto Reply anahtarı)
- Otomatik yanıt mesajları logda `[Auto]` etiketi taşır

## Sunucu Bağlantı Politikası

- Her sunucu instance'ı aynı anda **yalnızca bir aktif TCP client** kabul eder
- Yeni client bağlandığında önceki client soket seviyesinde kapatılır
- UI durum göstergeleri, devre dışı kalan client için disconnect yansıtmalıdır

## Bilinmeyen / Bozuk Mesaj Davranışı

- Bilinmeyen mesaj ID → uyarı olayı, otomatik yanıt yok, çökme yok
- Kesik/bozuk gövde → protokol hatası olayı, otomatik yanıt yok, çökme yok
