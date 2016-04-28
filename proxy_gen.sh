#!/usr/bin/env bash

# Requires a target directory to work through for input 1.
# Requires a directory to output proxy as input 2.


exec 1> >(logger -s -t $(basename $0)) 2>&1

cd "$1"
dest="$2$1"

[ -d "$dest" ] || mkdir -p "$dest"


for name in *.mov; do
    if [ ! -e "$dest${name%.*}.mp4" ];
    then
        echo "Building: $dest${name%.*}.mp4"
        ffmpeg -i "$name" \
        -y \
        -loglevel warning \
        -t 5 \
        -c:v h264 \
        -b:v 100k \
        -crf 25 \
        -pix_fmt yuv420p \
        -vf scale=320:240 \
        -sws_flags lanczos \
        -c:a aac \
        -ac 2 \
        -b:a 96k \
        "$dest/${name%.*}.mp4" > /dev/null 2> /dev/null
    fi
done