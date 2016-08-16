#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
"""
This python script uses ffmpeg to make proxy files from higher
resolution video files.

Input 1: Target directory containing the media.
Input 2: Destination directory for proxy files.

Settings can be configured below.

FFMPEG_PATH: location of ffmpeg on the system.
CRF_VALUE: Adjusts the output quality. 0 is lossless, 23 is default,
    51 is the worst.

for more information:
    http://ffmpeg.org/trac/ffmpeg/wiki/x264EncodingGuide

"""

import logging
import os
import sys
import subprocess

# Settings
FFMPEG_PATH = '/usr/local/bin/ffmpeg'
CRF_VALUE = '35'
VIDEO_BR = '100' + 'k'
AUDIO_BR = '96' + 'k'
PRESET = 'ultrafast'
FILETYPES = (".mov", ".mxf", ".mpg", ".avi")

# Extra ffmpeg args. To be reviewed
opts = None

# Set up logging
fflog = logging.getLogger(__name__)
fflog.setLevel(logging.DEBUG)

fhandler = logging.FileHandler('proxy_gen.log')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)

fflog.addHandler(fhandler)


# Check user input arguments
if len(sys.argv) > 1:
    target_dir = sys.argv[1]
    dest_dir = sys.argv[2]
    if sys.argv[3]:
        opts = sys.argv[3]

    # Remove trailing '/'
    if target_dir[-1] == '/':
        target_dir = target_dir[:-1]
    if dest_dir[-1] == '/':
        dest_dir = dest_dir[:-1]
    fflog.info('{}\n{}'.format(target_dir, dest_dir))
else:
    print('Please provide an input and output directory')


def scan_files(target):
    """
    Checks if proxy destination already exists and creates
    the folder if not.
    Searches for videos to create proxy files from.
    """
    destination = dest_dir + target_dir
    if not os.path.exists(destination):
        os.makedirs(destination)
    for root, dirs, files in os.walk(target):
        for d in dirs:            
            if not os.path.exists(d):
                logging.info('Directory name: {}'.format(d))
                proxy_directory = dest_dir + os.path.join(root, d)
                try:
                    os.makedirs(proxy_directory)
                except OSError:
                    fflog.error('Directory exists: {}'.format(proxy_directory))
                    continue
        for f in files:
            if f.lower().endswith(FILETYPES):
                mov_file = os.path.join(root, f)
                proxy_file = dest_dir + mov_file.replace(
                        os.path.splitext(mov_file)[1], '.mp4')
                if '.AppleDouble' in mov_file or '/._' in mov_file:
                    continue
                if os.path.isfile(proxy_file):
                    continue
                if opts != None:
                    # extra = ' '.join(opts)
                    build_proxy_options(mov_file)
                else:
                    build_proxy(mov_file)
            else:
                continue


def build_proxy(fname):
    outfile = fname.replace(os.path.splitext(fname)[1], '.mp4')
    try:
        command = [
            FFMPEG_PATH, '-i', fname,
            '-y',
            '-loglevel', 'warning',
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
            '{}{}'.format(dest_dir, outfile)
            ]
        print('\nBuilding proxy file: {}'.format(outfile))
        subprocess.call(command)
    except Exception:
        print(Exception)
        logging.error('{} : {}'.format(Exception, outfile))



def build_proxy_options(fname):
    """
    Build video proxy using extra ffmpeg arguments
    """
    outfile = fname.replace(os.path.splitext(fname)[1], '.mp4')
    try:
        command = [
            FFMPEG_PATH, '-i', fname,
            '-y',
            '-loglevel', 'warning',
            '-map 0:1',
            '-map 0:2',
            '-map 0:10',
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
            '{}{}'.format(dest_dir, outfile)
            ]
        # print('\tffmpeg command: {}\n'.format(command.join(' ')))
        print('\t FFmpeg command: {} \n'.format(' '.join(command)))
        print('\nBuilding proxy file: {}'.format(outfile))
        subprocess.call(command)
    except Exception as FE:
        print(FE)
        logging.error('{} : {}'.format(FE, outfile))



if __name__ == '__main__':
    scan_files(target_dir)

