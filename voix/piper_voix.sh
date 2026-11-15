#!/usr/bin/env bash
# Voix maison sans limite dans la session cloud (Piper, open source). Usage : ./voix/piper_voix.sh tom|pierre texte.txt sortie.wav
set -e; V=${1:?tom|pierre}; cd "$(dirname "$0")"
pip install -q --break-system-packages piper-tts >/dev/null 2>&1 || true
M=$([ "$V" = tom ] && echo fr_FR-tom-medium || echo fr_FR-upmc-medium); S=$([ "$V" = pierre ] && echo "-s 1" || echo "")
[ -d vits-piper-$M ] || curl -sSL https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-$M.tar.bz2 | tar xj
python3 -m piper -m vits-piper-$M/$M.onnx $S -f brut.wav < "$2"
ffmpeg -v error -y -i brut.wav -af "aresample=44100,asetrate=44100*0.94,aresample=44100,atempo=1.06,equalizer=f=120:t=q:w=1:g=4,equalizer=f=3500:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=4:attack=5:release=80,aecho=0.8:0.4:35:0.12,loudnorm=I=-14" "$3"
