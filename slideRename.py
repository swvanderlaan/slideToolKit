#!/usr/bin/env python3
#
# script to display a whole-slide image file and manually rename the file (*.TIF, *.NDPI, etc.)
#
# Ref: https://github.com/choosehappy/Snippets/blob/master/extract_macro_level_from_wsi_image_openslide_cli.py
#

# Only import heavy libraries after determining they are needed
import argparse
import textwrap
import os
from sys import exit

# Version information
# Change log:
# * v1.1.0 (2024-09-26): Overhaul to make the script more modular, define functions, and easier to read.
# * v1.0.0 (2023-12-15): Initial version.
VERSION_NAME = 'slideRename'
VERSION = '1.1.0'
VERSION_DATE = '2024-09-26'
COPYRIGHT = 'Copyright 1979-2024. Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com | https://vanderlaanand.science.'
COPYRIGHT_TEXT = '''
The MIT License (MIT).

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and 
associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS 
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE 
OR OTHER DEALINGS IN THE SOFTWARE.

Reference: http://opensource.org.
'''

# Define the header
def print_header():
    print(f"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"                                   {VERSION_NAME}: display and manually rename images ")
    print(f"\n* Version          : {VERSION}")
    print(f"* Last update      : {VERSION_DATE}")
    print(f"* Written by       : Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com")
    print(f"* Inspired by      : choosehappy | https://github.com/choosehappy\n")
    print(f"* Description      : This script will get thumbnails from (a list of given) images. The user can hit a key and")
    print(f"                     manually type in the correct file name. If the new filename already exists in that ")
    print(f"                     directory the renaming will be cancelled.\n")
    print(f"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")

def print_footer():
    print(f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"+ The MIT License (MIT)                                                                                           +")
    print(f"+ {COPYRIGHT}                          +")
    print(f"+ Reference: http://opensource.org.                                                                               +")
    print(f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog=VERSION_NAME,
        description=f'''
+ {VERSION_NAME} v{VERSION} +

This script will display thumbnails from (a list of given) images and opens a terminal window for manual renaming of images.''',
        usage='python3 slideRename.py -i/--input; optional: -o/--outdir -s/--suffix -f/--force; for help: -h/--help',
        epilog=f'''
+ {VERSION_NAME} v{VERSION}. {COPYRIGHT} +\nThe MIT License (MIT)\nReference: http://opensource.org
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-o', '--outdir', help="Output dir, default is the input image(s) directory. Optional.", default="<<SAME>>", type=str)
    parser.add_argument('-s', '--suffix', help="Suffix to append to end of file, no suffix will be added by default. Optional.", default="", type=str)
    parser.add_argument('-f', '--force', help="Force output even if it exists. Optional.", default=False, action="store_true")
    parser.add_argument('-v', '--verbose', help="Verbose output. Optional.", default=False, action="store_true")
    parser.add_argument('-V', '--version', action='version', version=VERSION_NAME + ' v' + VERSION + ' (' +  VERSION_DATE + ') | ' + COPYRIGHT)

    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-i', '--input', help="An input image (or directory containing image files). Required.", nargs="*")
    
    return parser.parse_args()

def validate_input(args):
    import glob
    if not args.input:
        print("\nOh, computer says no! You must supply correct arguments when running *** slideRename ***!")
        print("Note that -i/--input is required. Try: --input IMG012.ndpi (or *.TIF or /path_to/images/*.ndpi).\n")
        exit()

    if len(args.input) > 1:
        return args.input
    else:
        return glob.glob(args.input[0])

def process_images(files, args):
    import numpy as np
    import openslide
    import cv2

    for fname in files:
        fname_base, fname_base_ext = os.path.splitext(os.path.basename(fname))

        outdir = args.outdir if args.outdir != "<<SAME>>" else os.path.dirname(os.path.realpath(fname))
        os.makedirs(outdir, exist_ok=True)
        
        print(f"Output directory set to [{outdir}].")
        
        fimage = openslide.OpenSlide(fname)
        img = np.asarray(fimage.associated_images["macro"])[:, :, 0:3]
        img_r = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        print(f"Display [{fname_base}] at path [{outdir}] with extension [{fname_base_ext}].")
        if args.verbose:
            print_image_info(img)

        cv2.imshow('slidePreview', cv2.cvtColor(img_r, cv2.COLOR_RGB2BGR))
        cv2.waitKey(1)

        new_fname = get_new_filename(fname_base)
        rename_file(outdir, fname_base, fname_base_ext, new_fname, args.force)

        cv2.destroyAllWindows()
        cv2.waitKey(1)

def print_image_info(img):
    print('* Image dimensions (height x width in pixels):', img.shape)
    img_size_kb = img.size / 1024
    print(f'* Image size: {img_size_kb:,.2f} KB')

def get_new_filename(old_fname):
    new_fname = input(f"Enter new name for [{old_fname}]: ")
    print(f"You entered: {new_fname}")
    return new_fname

def rename_file(outdir, old_fname, ext, new_fname, force):
    old_fnameout = f"{outdir}/{old_fname}{ext}"
    new_fnameout = f"{outdir}/{new_fname}{ext}"

    if not force and os.path.exists(new_fnameout):
        print(f"Skipping {new_fnameout}, output file exists and --force is not set.")
    else:
        os.rename(old_fnameout, new_fnameout)
        print(f"Renamed [{old_fnameout}] to [{new_fnameout}].")

if __name__ == "__main__":
    args = parse_arguments()

    print_header()
    files = validate_input(args)
    process_images(files, args)
    print_footer()
