"""
This python script uses ffmpeg to make proxy files from high
resolution Apple ProRes mov files.

Input 1: Target directory containing the media.
Input2: Destination directory for proxy files.

Settings can be configured below.

FFMPEG_PATH: location of ffmpeg on the system.
CRF_VALUE: Adjusts the output quality. 0 is lossless, 23 is default,
    51 is the worst.

for more information:
    http://ffmpeg.org/trac/ffmpeg/wiki/x264EncodingGuide

"""

import os
import sys
import subprocess

# Settings
FFMPEG_PATH = '/usr/local/bin/ffmpeg'
CRF_VALUE = '25'
VIDEO_BR = '100' + 'k'
AUDIO_BR = '96' + 'k'
PRESET = 'ultrafast'


if len(sys.argv) > 1:
    target_dir = sys.argv[1]
    dest_dir = sys.argv[2]
else:
    print('Please provide an input and output directory')


def scan_files(target):
    destination = dest_dir + target_dir
    if not os.path.exists(destination):
        os.makedirs(destination)
    for root, dirs, files in os.walk(target):
        for d in dirs:
            if not os.path.exists(d):
                proxy_directory = dest_dir + target_dir + d
                try:
                    os.makedirs(proxy_directory)
                except OSError:
                    print('Directory exists')
                    continue
        for f in files:
            if f.endswith(".mov"):
                mov_file = os.path.join(root, f)
                if '.AppleDouble' in mov_file or '/._' in mov_file:
                    continue
                else:
                    build_proxy(mov_file)
            else:
                continue


def build_proxy(fname):
    try:
        command = [
            FFMPEG_PATH, '-i', fname,
            '-y',
            '-t', '6',
            '-c:v', 'h264',
            '-b:v', VIDEO_BR,
            '-crf', CRF_VALUE,
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=320:240',
            '-sws_flags', 'lanczos',
            '-preset', PRESET,
            '-c:a', 'aac',
            '-ac', '2',
            '-b:a', AUDIO_BR,
            '{}{}.mp4'.format(dest_dir, fname.replace('.mov', ''))
            ]
        subprocess.call(command)
    except Exception:
        print Exception


if __name__ == '__main__':
    scan_files(target_dir)

