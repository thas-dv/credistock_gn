#!/usr/bin/env bash
# Fabrique la vidéo du jour à partir de story.json, words.json et voix.mp3 (dans ce dossier).
# Usage : ./make_video.sh AAAAMMJJ    -> sortie/mindset24_AAAAMMJJ.mp4 (~20-25 Mo)
set -euo pipefail
D=${1:?date AAAAMMJJ}
cd "$(dirname "$0")"
python3 build_timing.py story.json words.json
python3 audio.py mix.wav
R=$(python3 -c "import json;print('render_doc.py' if json.load(open('timing_voix.json')).get('style')=='doc' else 'render.py')")
python3 $R timing_voix.json video_brut.mp4 > render.log 2>&1
mkdir -p sortie
ffmpeg -v error -y -i video_brut.mp4 -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 4.5M -maxrate 6M -bufsize 9M \
  -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart -shortest "sortie/mindset24_${D}.mp4"
ls -la "sortie/mindset24_${D}.mp4"
