#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from glob import glob
from argparse import ArgumentParser
from os import remove
from os.path import isfile, join, isdir, exists, getctime
import dropbox
from datetime import datetime
from dropbox.exceptions import AuthError
from config import *


def dropbox_connect():
    """Create a connection to Dropbox."""

    try:
        dbx = dropbox.Dropbox(app_key=APP_KEY, app_secret=APP_SECRET, oauth2_refresh_token=REFRESH_TOKEN)
    except AuthError as e:
        print(f'Error connecting to Dropbox with access token: {e}')
    return dbx


def dropbox_download_file(dropbox_file_path, local_file_path):
    """Download a file from Dropbox to the local machine."""

    try:
        dbx = dropbox_connect()
        with open(local_file_path, 'wb') as f:
            metadata, result = dbx.files_download(path=dropbox_file_path)
            f.write(result.content)
    except Exception as e:
        print(f'Error downloading file from Dropbox: {e}')


def dir_path(string):
    if isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--path', type=dir_path)
    args = parser.parse_args()
    backup_path = args.path
    if backup_path and dir_path(backup_path) and exists(backup_path):
        print('Downloading vault...')
        vault_filename_template = join(backup_path, f'{VAULT_FILENAME}')
        filename = f'{vault_filename_template}_{datetime.now().date()}'
        dropbox_download_file(f'/{VAULT_FILENAME}', filename)
        print('Saved as', filename)
        vaults = list(filter(isfile, glob(vault_filename_template + '*')))
        if len(vaults) > 5:
            vaults.sort(key=lambda x: getctime(x))
            print(f'Removing oldest backup {vaults[0]}...')
            remove(vaults[0])
        print('Done!')
    else:
        print(f'Backup path {backup_path} does not exist. Did you forgot to add --path key?')
