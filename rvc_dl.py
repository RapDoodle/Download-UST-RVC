# -*- coding: utf-8 -*-
import os
import re
import datetime
import requests
import concurrent.futures
import itertools
import argparse
import subprocess
from tqdm import tqdm
from time import sleep
from random import gauss
from urllib.parse import unquote, urlparse

DISP_MODE_LOG = 0
DISP_MODE_OK = 1
DISP_MODE_WARNING = 2
DISP_MODE_ERROR = 3

TEMP_VIDEO_LIST = 'videolist'
TEMP_FOLDER = './temp'


def get_urls_from_chunklist(chunklist_url, headers = {}):
    """
    Generate urls from a list of url parameters
    """
    import requests
    from urllib.parse import urljoin, urlparse

    # Remove all url parameters
    base_url = urljoin(chunklist_url, urlparse(chunklist_url).path)

    # Concatenate url params with the base_urls
    with requests.get(chunklist_url, headers=headers, allow_redirects=True) as r:
        if len(r.content) > 0:
            for line in r.content.decode().splitlines():
                if line.startswith('#'):
                    continue
                url = urljoin(base_url, line)
                yield url


def concat_m3u8_to_mp4(downloaded_files, urls, output_directory, output_filename, override_warning=True, **kwargs):
    """
    Convert m3u8 clips to an mp4 file
    """
    if len(urls) == 0 or len(downloaded_files) == 0:
        display('No files downloaded. Unable to proceed.', DISP_MODE_ERROR)
        exit(1)
    display('Processing video clips using ffmpeg...', DISP_MODE_LOG)
    with open(TEMP_VIDEO_LIST, 'w') as f:
        for index, file in enumerate(downloaded_files):
            if file is not None:
                f.write(f'file \'{file}\'\n')
    
    # Infer the filename
    if output_filename is None:
        re_res = re.search(r'[^/\\&\?:]+\.(mp4|MP4|mov|MOV|wmv|WMV|avi|AVI|flv|FLV|mkv|MKV|webm|WEBM)(?=([\?&].*|))', urls[0])
        if re_res is not None:
            output_filename = re_res.group(0)
        else:
            output_filename = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S') + '.mp4'
    output_path = f'{output_directory}/{output_filename}'

    # Determine whether the output filename already exists
    if os.path.exists(output_path) and override_warning and not y_n_choice(f'The file {output_path} already exists. Are you sure to continue?'):
        os.remove(TEMP_VIDEO_LIST)
        exit()
    
    # Create directory when not exists
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    # Subroutine: call ffmpeg to concatencate and convert the clips to an mp4 file 
    command_list = ['ffmpeg', 
                    '-safe', '0', 
                    '-loglevel', 'error',
                    '-f', 'concat',
                    '-i', 'videolist', 
                    '-c', 'copy',
                    '-bsf:a', 'aac_adtstoasc', 
                    '-y', 
                    output_path]
    if subprocess.run(command_list, shell=False).returncode == 0:
        display(f'Successfully concatenated {len(downloaded_files)} video clips into {output_path}', DISP_MODE_OK)
    else:
        display(f'Failed to concatencate video clips.', DISP_MODE_ERROR)

    # Remove the file containing the list of filenames
    os.remove(TEMP_VIDEO_LIST)


def remove_downloaded_files(downloaded_files, directory, **kwargs):
    display('Deleting original video clips...', DISP_MODE_LOG)
    for file in downloaded_files:
        if file is not None:
            os.remove(file)
    if len(os.listdir(directory)) == 0:
        try:
            os.rmdir(directory)
        except PermissionError:
            display(f'Permission denied. Unable to delete the empty folder {directory}', DISP_MODE_ERROR)


def find_missing_downloads(urls, downloaded_files, prompt=True, **kwargs):
    """
    Find the downloads that are missing as a result of unsuccessful 
    download for invalid urls
    Arguments:
        urls: a list of urls
        downloaded_files: a list containing the paths to the 
            downloaded files
        promot: a boolean indicating whether confirmation is needed 
            before proceeding
    """
    missing_count = 0 
    for index, file in enumerate(downloaded_files):
        if file is None:
            curr_file_url = urls[index]
            display(f'The file content for {curr_file_url} is empty.', DISP_MODE_WARNING)
            missing_count = missing_count + 1
    
    if missing_count > 0:
        warning_msg = f'There are {missing_count} missing file(s).' 
        if prompt:
            if not y_n_choice(f'{warning_msg} Are you sure to continue?', default_choice=False):
                exit()
        else:
            display(warning_msg, DISP_MODE_WARNING)


def y_n_choice(msg='Do you want to continue?', default_choice=False):
    default_choice_str = 'yes' if default_choice else 'no'
    while (True):
        choice = input(f'{msg} (default: {default_choice_str}) [Y/n] ')
        if choice == '':
            # Case: default
            return default_choice
        if choice.lower() == 'y':
            # Case: confirm
            return True
        if choice.lower() == 'n':
            # Case: reject
            return False
        # Case: unkown, continue


def display(msg, mode=DISP_MODE_LOG):
    if mode == DISP_MODE_OK:
        prefix = '[√]'
    elif mode == DISP_MODE_WARNING:
        prefix = '[!]'
    elif mode == DISP_MODE_ERROR:
        prefix = '[x]'
    else:
        prefix = '[*]'
    print(f'{prefix} {msg}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u', 
        '--url', 
        metavar='STRING', 
        required=True, 
        help='chunklist url')
    parser.add_argument(
        '-o', 
        '--output', 
        metavar='FILENAME', 
        required=False, 
        default=None,
        help='output filename')
    parser.add_argument(
        '-w', 
        '--workers', 
        metavar='INT', 
        type=int,
        required=False, 
        default=10,
        help='number of workers')
    args = parser.parse_args()

    interval_mean = 0
    interval_std = 0
    timeout = 180
    download_directory = TEMP_FOLDER
    urls = list(get_urls_from_chunklist(args.url))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }

    # Get the total number of urls to visit
    total = len(list(urls))

    # Atomic counter for the number of completed/failed downloads
    cont = itertools.count()

    # Create directory if not exists
    if not os.path.exists(download_directory):
        os.mkdir(download_directory)

    # Initialize progress bar
    pbar = tqdm(total=total, unit='files')
    downloaded_files = [None] * total

    def fetch(i, url, dst):
        """
        Download from a given resource
        Arguments:
            i: id/index of the current job
            url: url to the resource
            dst: destination folder
        """
        try:
            with requests.get(url, headers=headers, allow_redirects=True) as r:
                status_code_str = str(r.status_code)
                if status_code_str.startswith('4') or status_code_str.startswith('5'):
                    return
                fname = ''
                if "Content-Disposition" in r.headers.keys():
                    fname = re.findall("filename=(.+)", unquote(r.headers["Content-Disposition"]))[0]
                    fname = fname.replace('\t', '')
                    fname = fname.replace('|', '')
                    fname = fname.replace('"', '')
                    fname = fname.replace('/', '')
                else:
                    fname = os.path.basename(urlparse(url).path)
                fpath = f'{dst}/{fname}'
                with open(fpath, 'wb') as f:
                    f.write(r.content)
                    downloaded_files[i] = fpath
        except requests.RequestException as e:
            display(f'Failed to download {url}', DISP_MODE_ERROR)
        pbar.n = next(cont)
        pbar.update()

    # Submit jobs to parallel workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_list = list()
        for index, url in enumerate(urls):
            sleep(max(gauss(mu=interval_mean, sigma=interval_std), 0))
            future_list.append(executor.submit(fetch, index, url, download_directory))
        concurrent.futures.wait(future_list, timeout=timeout)

    pbar.close()

    find_missing_downloads(urls, downloaded_files, True)
    concat_m3u8_to_mp4(downloaded_files, urls, download_directory, args.output, True)
    remove_downloaded_files(downloaded_files, download_directory)

    display('Done', DISP_MODE_OK)