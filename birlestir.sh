#!/bin/bash
# 20 klibi başlık kartlarıyla tek katalog videosunda birleştirir -> katalog.mp4 (+ 720p)
set -e; cd "$(dirname "$0")"; mkdir -p _kat; rm -f _kat/*
SERIF=/System/Library/Fonts/Supplemental/Georgia.ttf; ITAL="/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
i=0; : > _kat/list.txt
while IFS='|' read -r slug ad grup; do
  i=$((i+1)); n=$(printf %02d $i)
  [ -f "stiller/$slug/$slug.mp4" ] || { echo "EKSİK: $slug"; continue; }
  python3 - "$n  ·  $ad" "$grup" "_kat/k$n.png" <<'PY'
import sys
from PIL import Image, ImageDraw, ImageFont
t, g, out = sys.argv[1:]
im = Image.new('RGB', (1920, 1080), (28, 26, 22)); d = ImageDraw.Draw(im)
f1 = ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia.ttf', 86)
f2 = ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia Italic.ttf', 34)
for txt, f, y, c in ((g, f2, 430, (163, 155, 139)), (t, f1, 500, (243, 238, 226))):
    w = d.textlength(txt, font=f); d.text(((1920 - w) / 2, y), txt, font=f, fill=c)
im.save(out)
PY
  ffmpeg -nostdin -v error -y -loop 1 -framerate 30 -t 1.4 -i "_kat/k$n.png" -f lavfi -i anullsrc=r=48000:cl=stereo -t 1.4 \
    -vf "fade=t=in:d=0.3,fade=t=out:st=1.15:d=0.25,format=yuv420p" -c:v libx264 -crf 18 -c:a aac -b:a 192k -shortest _kat/k$n.mp4
  ffmpeg -nostdin -v error -y -i "stiller/$slug/$slug.mp4" -vf "scale=1920:1080,fps=30,format=yuv420p" -af "aformat=sample_rates=48000:channel_layouts=stereo" \
    -c:v libx264 -crf 18 -c:a aac -b:a 192k _kat/v$n.mp4
  echo "file 'k$n.mp4'" >> _kat/list.txt; echo "file 'v$n.mp4'" >> _kat/list.txt
done <<'L'
kurzgesagt|Kurzgesagt|Düz grafik
izometrik|İzometrik|Düz grafik
bauhaus|Bauhaus|Düz grafik
memphis|Memphis|Düz grafik
beyaz-tahta|Beyaz tahta|El çizimi
kara-tahta|Kara tahta|El çizimi
blueprint|Blueprint|El çizimi
tek-cizgi|Tek çizgi|El çizimi
kagit-kesik|Kâğıt kesik|Doku ve zanaat
karakalem|Karakalem|Doku ve zanaat
linocut|Linocut|Doku ve zanaat
kil|Kil (stop-motion)|Doku ve zanaat
retro-70ler|70’ler|Nostalji
piksel|Piksel sanat|Nostalji
belgesel-16mm|16 mm belgesel|Nostalji
cizgi-roman|Çizgi roman|Nostalji
terminal|Terminal|Teknik
hud|Bilim-kurgu arayüzü|Teknik
veri|Veri görselleştirme|Teknik
kinetik-tipografi|Kinetik tipografi|Deneysel
L
[ -f katalog/son.mp4 ] && echo "file '../katalog/son.mp4'" >> _kat/list.txt   # kapanış kartı (logo + adres)
ffmpeg -nostdin -v error -y -f concat -safe 0 -i _kat/list.txt -c copy katalog/katalog_1080p.mp4
ffmpeg -nostdin -v error -y -i katalog/katalog_1080p.mp4 -vf scale=1280:-2 -c:v libx264 -crf 25 -c:a copy katalog/katalog.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 katalog.mp4; ls -la katalog*.mp4 | awk '{print $5,$9}'
