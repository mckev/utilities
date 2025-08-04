#!/usr/bin/env python3

"""
iPhone is really bad in mixing all image files into DCIM directory. This script attempts to separate the files based on some rules.
"""

import os


def move_file(filename, dest_dir, is_create_dest_dir=True):
    if is_create_dest_dir:
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
    os.rename(filename, dest_dir + filename)


def main():
    print(f'Processing iPhone DCIM files on current directory {os.getcwd()}')

    for filename in os.listdir('.'):
        # Only process IMG_*.* files
        if not filename.startswith('IMG_'):
            continue
        filename_root, filename_ext = os.path.splitext(filename)
        if filename_ext == '.MOV':
            if os.path.exists(f'{filename_root}.HEIC'):
                # IMG_XXXX.MOV file that has accompany IMG_XXXX.HEIC is a live photo
                print(f'{filename} is a live photo of {filename_root}.HEIC')
                move_file(filename, 'pictures/')
                move_file(f'{filename_root}.HEIC', 'pictures/')
            elif os.path.exists(f'{filename_root}.JPG'):
                # Similarly, IMG_XXXX.MOV file that has accompany IMG_XXXX.JPG is a live photo
                print(f'{filename} is a live photo of {filename_root}.JPG')
                move_file(filename, 'pictures/')
                move_file(f'{filename_root}.JPG', 'pictures/')
            else:
                print(f'{filename} is a video')
                move_file(filename, 'videos/')
        elif filename_ext == '.PNG':
            print(f'{filename} is a screenshot')
            move_file(filename, 'screenshots/')

    # Remaining IMG_*.HEIC files
    for filename in os.listdir('.'):
        if filename.startswith('IMG_') and (filename.endswith('.HEIC') or filename.endswith('.JPG')):
            print(f'{filename} is a picture')
            move_file(filename, 'pictures/')


main()
