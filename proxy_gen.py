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
import argparse
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


# Set up logging
fflog = logging.getLogger(__name__)
fflog.setLevel(logging.DEBUG)

fhandler = logging.FileHandler('proxy_gen.log')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)

fflog.addHandler(fhandler)

# Extra ffmpeg args. To be reviewed
opts = None
target_dir = ''
dest_dir = ''

parser = argparse.ArgumentParser(description='Proxy file creator')
parser.add_argument('-i', '--input', help='Choose input file')
parser.add_argument('-o', '--output', help='Choose output directory')
parser.add_argument('-au', nargs='+', help="Choose audio channels to map for proxy")
parser.add_argument('-d', '--info', help='Display info on submitted media')
arg = parser.parse_args()

if arg.input:
    target_dir = arg.input
    if target_dir[-1] == '/':
        target_dir = target_dir[:-1]

if arg.output:
    dest_dir = arg.output
    if dest_dir[-1] == '/':
        dest_dir = dest_dir[:-1]
    
if arg.au:
    opts = dict([('-map', a) for a in arg.au])
    print(opts)

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
                proxy_mp4 = dest_dir + mov_file.replace(
                        os.path.splitext(mov_file)[1], '.mp4')
                proxy_mov = dest_dir + mov_file.replace(
                        os.path.splitext(mov_file)[1], '.mov')
                if '.AppleDouble' in mov_file or '/._' in mov_file:
                    continue
                if os.path.isfile(proxy_mp4) or os.path.isfile(proxy_mov):
                    print('Filescan: proxy has already been made '
                            'for: {}'.format(f))
                    continue
                if opts != None:
                    build_proxy_options(mov_file)
                else:
                    print('simple build')
                    build_proxy(mov_file)
            else:
                continue

def display_media_info(fname):
    try:
        command = [FFMPEG_PATH, '-i', fname]
        subprocess.call(command)
    except Exception as DisplayError:
        print('Filescan: {}'.format(DisplayError))


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
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()
        print(output)
    except Exception:
        print(Exception)
        logging.error('Proxy Build Error: {} : {}'.format(Exception, outfile))



def build_proxy_options(fname):
    """
    Build video proxy using extra ffmpeg arguments
    """
    print('\nMULTI')
    outfile = fname.replace(os.path.splitext(fname)[1], '.mp4')

    try:
        command = [
            FFMPEG_PATH, '-i', fname,
            '-y',
            '-loglevel', 'warning',
            '-map', '0:1 0:2',
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
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()
        print(output)
        
    except Exception as FE:
        print(FE, Exception)
        logging.error('Proxy Build Error: {} : {}'.format(FE, outfile))



if __name__ == '__main__':
    if sys.argv[2].endswith(FILETYPES):
        try:
            display_media_info(sys.argv[2])
        except:
            print('Filescan: Filetype not support')
    else:
        scan_files(target_dir)

