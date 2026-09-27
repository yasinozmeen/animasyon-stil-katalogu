# Stil kataloğu — her animasyon tarzı için kısa vitrin klibi

Yasin (ürün sahibi, "irticalen" adlı Türkçe konuşma pratiği sitesi ve YouTube kanalı) animasyon tarzlarını görmek istiyor.
Her tarz için **o tarzı en iyi gösteren**, kendi içinde tamamlanmış **8–10 saniyelik** kısa bir klip yap. Ortak bir hikâye yok:
içeriği tarzın güçlü yanını sergileyecek şekilde SEN seç. İstersen irticalen dünyasından bir mini fikir kullan (konuşma balonu,
geri sayan sayaç, konu seçen çark, mikrofon, doğaçlama konuşma, kelimeler), ama zorunlu değil. Amaç: izleyen 3 saniyede
"ha, bu tarz buymuş" desin ve tarzın imza öğelerini (doku, hareket dili, renk, tipografi, geçiş) net görsün.

## Kalite çıtası
- Profesyonel stüdyo işi: tek odak, bilinçli kompozisyon, yumuşak ve anlamlı hareket (anticipation, overshoot, stagger), en az bir sahne dönüşümü/geçişi.
- Tarzın klişesine düşmeden en iyi örneği: o tarzda çalışan bir tasarımcı "evet, doğru yapılmış" demeli.
- İnsan figürü varsa özenle çiz (oranlar, eller) ya da tarz izin veriyorsa figürsüz anlat. Figür bu projede hassas konu.
- Yazı varsa Türkçe ve Türkçe harfler doğru fontta (Google Fonts'tan indir; latin + latin-ext). Stok görsel/fotoğraf yok, gerçek kişi fotoğrafı yok, marka logosu yok (irticalen logosu serbest: konuşma balonu + 3 elmas, `~/.claude/skills/video-kurgu/engine/overlay.html` → `logo()`).
- Klip kendi içinde başlasın ve bitsin (giriş + çıkış), son karede sert kesilmesin.

## Teknik
- Her tarz kendi klasöründe: `~/Movies/kurgu/stil-katalogu/<slug>/` → `anim.html` (canvas 1920×1080, `window.draw({t})` o anın karesini `toDataURL('image/jpeg', 0.92)` base64 döndürür, `window.ready` font/doku hazırlığını bekler) + çıktı `out/<slug>.mp4` (H.264, 30 fps, yuv420p, crf 18).
- Örnek kare çizici: `~/Movies/kurgu/stil-katalogu/render_ornek.mjs` (kendi klasörüne kopyala; `anim.html` yolunu, süreyi kullan). **En fazla 2 paralel sayfa** — aynı anda 4 başka ajan daha render alıyor. Her render öncesi `memory_pressure | tail -1` (boş < %25 ise bekle). Kareleri JPEG tut, bitince kare klasörünü sil.
- Pahalı efektleri (doku, gren, bulanık ışıma, kâğıt) bir kez üret (offscreen canvas), her karede yeniden hesaplama.
- Ses: opsiyonel. İstersen tarzına uygun çok kısa sentez sesler (ffmpeg ile: tık, pop, bip, tebeşir sürtmesi taklidi…) — hışırtı/whoosh YOK. Ses yoksa sessiz AAC kanal ekle (birleştirme için her klipte ses kanalı olsun: `-f lavfi -i anullsrc=r=48000:cl=stereo -shortest`).
- Kontrol: her klip için `ffmpeg -i out/<slug>.mp4 -vf "fps=2,scale=480:-1,tile=4x5" -frames:v 1 _kontrol.jpg` + önemli anlardan tam çözünürlük tek kare; Read ile bak, en az 1 düzeltme turu.

## Sınırlar
Yalnız kendi tarz klasörlerine yaz. Başka klasöre, skill dosyalarına dokunma. hcom/git yok. Sunucu başlatma.

## Rapor (kısa)
Her tarz için: slug, klipte ne anlattın (1 cümle), tarzın hangi imza öğelerini gösterdin, bilinen kusur, çıktı yolu.
