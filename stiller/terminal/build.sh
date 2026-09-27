#!/bin/zsh
# ./build.sh → out/<slug>.mp4 (9 sn, 30 fps, H.264 crf 18, yuv420p + ses) ve _kontrol.jpg
set -e
cd "$(dirname "$0")"; SLUG=$(basename "$PWD"); DUR=9
while true; do FREE=$(memory_pressure | tail -1 | grep -o '[0-9]*'); [ "$FREE" -ge 25 ] && break; echo "RAM boş %$FREE, bekleniyor"; sleep 20; done
rm -rf _frames; node render.mjs _frames 30 0 $DUR 2
node sfx.mjs && python3 sfx.py
mkdir -p out
ffmpeg -loglevel error -y -framerate 30 -i _frames/%05d.jpg -i sfx.wav -map 0:v -map 1:a \
  -vf "scale=in_range=pc:out_range=tv,format=yuv420p" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -color_range tv -c:a aac -b:a 192k -ar 48000 -t $DUR -movflags +faststart out/$SLUG.mp4
ffmpeg -loglevel error -y -i out/$SLUG.mp4 -vf "fps=2,scale=480:-1,tile=4x5" -frames:v 1 _kontrol.jpg
rm -rf _frames _test
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,pix_fmt -of compact out/$SLUG.mp4
