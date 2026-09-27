#!/bin/zsh
# tam render + kodlama: ./yap.sh <slug> <sure>
set -e
cd "$(dirname "$0")"
SLUG=$1; DUR=$2
rm -rf _kareler; node render.mjs _kareler 30 0 $DUR 2 | tail -1
if [ -f out/ses.wav ]; then AUD=(-i out/ses.wav); else AUD=(-f lavfi -i anullsrc=r=48000:cl=stereo); fi
ffmpeg -loglevel error -y -framerate 30 -pattern_type glob -i '_kareler/*.jpg' $AUD -map 0:v -map 1:a \
  -vf "scale=in_range=pc:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -ar 48000 -shortest -movflags +faststart out/$SLUG.mp4
rm -rf _kareler
ffmpeg -loglevel error -y -i out/$SLUG.mp4 -vf "fps=2,scale=480:-1,tile=4x5" -frames:v 1 _kontrol.jpg
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,pix_fmt -of compact out/$SLUG.mp4
