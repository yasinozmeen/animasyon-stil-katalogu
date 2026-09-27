#!/bin/zsh
# ./build.sh <slug> <dur>  — kareleri çiz, H.264 + ses, kontrol karosu, kare klasörünü sil
set -e; cd "${0:A:h}"; slug=$1; dur=$2
while :; do free=$(memory_pressure | tail -1 | grep -oE '[0-9]+'); [ "$free" -ge 25 ] && break; echo "RAM boş %$free, bekliyorum"; sleep 20; done
rm -rf _frames; node render.mjs _frames 30 0 $dur 2
ffmpeg -loglevel error -y -framerate 30 -i _frames/%05d.jpg -i sfx.wav -map 0:v -map 1:a -vf "scale=in_range=full:out_range=tv,format=yuv420p" -c:v libx264 -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart out/$slug.mp4
rm -rf _frames _test
ffmpeg -loglevel error -y -i out/$slug.mp4 -vf "fps=2,scale=480:-1,tile=4x5" -frames:v 1 _kontrol.jpg
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,pix_fmt -of csv=p=0 out/$slug.mp4
