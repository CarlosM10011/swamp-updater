#!/usr/bin/env python3
#
# Copyright 2020 Carlos Medrano
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tempfile
import os
from pathlib import Path
import requests
from requests.exceptions import ChunkedEncodingError
import shutil
from subprocess import call
import time
from tqdm import tqdm
import zipfile

def dl_swamp_patch(tmp_dir, file_name):
    file_path = os.path.join(tmp_dir, file_name)
    print('Fetching file from \'https://www.kaldobsky.com/audiogames/%s\''
            %(file_name))
    downloaded_length = 0
    finished = False
    output = open(file_path,'ab')
    progress_bar = None
    total_size_in_bytes = None
    while not finished:
        try:
            resume_header = {
                    'Range': f'bytes={downloaded_length}-'
                    }
            response = requests.get(
                    'https://www.kaldobsky.com/audiogames/' + file_name,
                    stream=True, headers=resume_header)
            if not total_size_in_bytes:
                total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024 #1 Kibibyte
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            progress_bar.update(downloaded_length)
            for data in response.iter_content(block_size):
                downloaded_length += len(data)
                progress_bar.update(len(data))
                output.write(data)
            output.flush()
            if downloaded_length == total_size_in_bytes:
                finished = True
            progress_bar.close()
        except requests.ConnectionError as e:
            if progress_bar:
                progress_bar.close()
            print('Connection failed. Retrying in 5 seconds...')
            time.sleep(5)
        except ChunkedEncodingError as e:
            if progress_bar:
                progress_bar.close()
            print('Connection failed. Retrying in 5 seconds...')
            time.sleep(5)
    output.close()
    return file_path


def unzip_archive(file_path, exclude_list):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        filelist = zip_ref.namelist()
        replace_list = []
        for i in filelist:
            exclude = False
            for j in exclude_list:
                if i.lower().find(j) == 0:
                    exclude = True
                    break
            if exclude == False:
                replace_list.append(i)
        for i in replace_list:
            zip_ref.extract(i)
        update_timestamps(zip_ref, replace_list)
    print('done')


def update_timestamps(zip_ref, file_list):
    for i in file_list:
        info = zip_ref.getinfo(i)
        date = time.mktime(info.date_time + (0, 0, -1))
        os.utime(i, (date, date))


def read_exclude_list():
    if not os.path.isfile('excluded_files.txt'):
        create_default_excludes()
    f = open('excluded_files.txt', 'r')
    lst = f.read().lower().split('\n')
    lst = [i for i in lst if i[:2] != '//' and i != '']
    f.close()
    return lst


def create_default_excludes():
    defaults = """// Add any files you wish to exclude from updating here. Lines beginning with // are ignored.
// To exclude a file, add it relative to the swamp folder. You also may add
// incomplete paths, if you wish to exclude entire folders from being touched by
// the updater. For example:
//
// Exclude the AA12 sound folder from updating:
// sounds/weapons/AA12
//
// Prevent my fieldkit reload sound from updating:
// sounds/weapons/Fieldkit/Reloading.wav
//
// A few examples are included below to help get you started.
Chatlog.txt
debuglog.txt
keyconfig.ini
losers.txt
muted.txt
myversion.txt
progress.ini
scriptkeys.txt
volumes.txt
"""
    f = open('excluded_files.txt', 'w')
    f.write(defaults)
    f.close()


def call_patch_updater():
    try:
        print('Running swamp-updater.exe')
        call(['swamp-updater'])
    except FileNotFoundError as e:
        print('Error running patch updater: %s' %(e))


def main():
    try:
        tmp_dir = tempfile.mkdtemp()
        print('Downloading files.')
        part1 = dl_swamp_patch(tmp_dir, 'SwampPart1.zip')
        part2 = dl_swamp_patch(tmp_dir, 'SwampPart2.zip')
        excludes = read_exclude_list()
        print('extracting Part1...')
        unzip_archive(part1, excludes)
        print('extracting Part2...')
        unzip_archive(part2, excludes)
        choice = input('Would you like to download the latest patch in order to play online? [y/n]: ')
        if choice == 'y' or choice == 'Y':
            call_patch_updater()
        else:
            choice = input('Would you like to view the changelog? [y/n]: ')
            if choice == 'y' or choice == 'Y':
                call(['notepad','changelog.txt'])
        print('Download complete.')
    except PermissionError as e:
        print('Error extracting update: %s' %(e))
        print('Make sure the game is closed before updating.')
    except KeyboardInterrupt:
        print('Ctrl+C pressed. Cleaning up...')
    except requests.ConnectionError as e:
        print('Error downloading update: %s' %(e))
    finally:
        shutil.rmtree(tmp_dir)
        input('Press return to continue: ')
    return 0


if __name__ == '__main__':
    main()
