import argparse
import re
import tempfile
import urllib
import urllib2
import requests

import errno
import time
import youtube_dl
import logging
import sys
import zipfile
import os
import shutil
import platform

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)


def main_download_list(source_file, checkup, password=''):
    current_time = time.strftime("%H-%M-%S_%d-%m-%Y")
    if not os.path.exists(current_time):
        try:
            log.info('main_download_list - CREATING FOLDER: {}'.format(os.path.join(os.getcwd(), current_time)))
            os.makedirs(current_time)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(os.getcwd(), current_time, '%(title)s.%(ext)s')
    }
    if checkup:
        checkup_download(password, ydl_opts)
    urls_to_download = []
    log.info('main_download_list - CREATING LIST OF URLS')
    with open(source_file, 'r') as f:
        data = f.read()
        names = data.split('\n')
        for name in names:
            vid_url = parse_name_to_url(name)
            if vid_url:
                urls_to_download.append(vid_url)
    log.info('main_download_list - DOWNLOADING LIST OF URLS')
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls_to_download)


def checkup_download(password, ydl_opts):
    temp_dir_path = tempfile.mkdtemp()
    log.info('checkup_download - CREATING FOLDER: {}'.format(temp_dir_path))
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # testing ydl.download with youtube video 
            ydl.download(['https://www.youtube.com/watch?v=0D5JJZl6MB0'])
    except youtube_dl.utils.DownloadError:
        log.error('checkup_download - FFPROBE OR AVPROBE NOT FOUND')
        log.info('checkup_download - FIXING *FFPROBE OR AVPROBE NOT FOUND*')
        system_name = platform.system().upper()
        if 'WINDOWS' in system_name:
            download_ffmpeg_windows(output_dir=temp_dir_path)
        elif 'LINUX' in system_name:
            download_ffmpeg_linux(password=password)
        else:
            log.error('checkup_download - NOT SUPPORTED PLATFORM')
    finally:
        shutil.rmtree(temp_dir_path)


def parse_name_to_url(name):
    url_search = 'https://www.youtube.com/results?search_query='
    url_flag_watch = '/watch\?v=[\S]+?\"'
    response = urllib2.urlopen(url_search + urllib.quote_plus(name))
    search_result_html = response.read()
    urls = re.findall(url_flag_watch, search_result_html)
    if urls:
        first_result = urls[0]
        vid_url = 'https://www.youtube.com{}'.format(first_result)
        log.info('parse_name_to_url - {} PARSED TO {}'.format(urllib.quote_plus(name), vid_url))
        return vid_url
    return None


def download_file(url, output):
    r = requests.get(url, stream=True)
    with open(output, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    return output


def download_ffmpeg_windows(output_dir):
    url = 'http://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20170921-183fd30-win64-static.zip'
    output_unzipped = os.path.join(output_dir, 'ffmpeg')
    output_zipped = os.path.join(output_dir, 'ffmpeg_folder')
    log.info('download_ffmpeg_windows - DOWNLOAD {} TO {}'.format(url, output_zipped))
    src = download_file(url, output=output_zipped)
    env_paths = os.environ['PATH'].split(';')
    for p in env_paths:
        if 'python' in p or 'Python' in p:
            zip_ref = zipfile.ZipFile(src, 'r')
            if not os.path.exists(output_unzipped):
                try:
                    os.makedirs(output_unzipped)
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            log.info('download_ffmpeg_windows - EXTRACT {} TO {}'.format(output_zipped, output_unzipped))
            zip_ref.extractall(output_unzipped)
            zip_ref.close()
            src = os.path.join(output_unzipped, 'ffmpeg-20170921-183fd30-win64-static', 'bin')
            src_files = os.listdir(src)
            for file_name in src_files:
                full_file_name = os.path.join(src, file_name)
                if os.path.isfile(full_file_name):
                    log.info('download_ffmpeg_windows - COPY {} TO {}'.format(full_file_name, p))
                    shutil.copy(full_file_name, p)
            return
    else:
        log.error('download_ffmpeg_windows - CANNOT FIND PYTHON DIR')


def download_ffmpeg_linux(password):
    if password:
        os.popen("sudo -S %s" % ('apt-get install --assume-yes libav-tools'), 'w').write('{}\n'.format(password))
        os.popen("sudo -S %s" % ('apt-get install --assume-yes ffmpeg'), 'w').write('{}\n'.format(password))
    else:
        log.error('download_ffmpeg_linux - NO PASSWORD GIVEN')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search and download list of songs')
    parser.add_argument('-c', '--check-up', help='fix fprobe or avprobe not found', required=False,
                        dest='checkup',
                        action='store_true')
    parser.add_argument('-s', '--source-file', type=str, help='path to file with list of songs', required=True,
                        dest='source_file')

    main_download_list(**vars(parser.parse_args()))
