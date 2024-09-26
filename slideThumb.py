#!/usr/bin/env python3
#
# script to extract thumbnails (and display) from whole-slide image files (*.TIF, *.NDPI, etc.)
#
# Ref: https://github.com/choosehappy/Snippets/blob/master/extract_macro_level_from_wsi_image_openslide_cli.py
#

import argparse
import textwrap
import os
from sys import exit

# Version information
# Change log:
# * v1.1.0 (2024-09-26): Overhaul to make the script more modular, define functions, and easier to read.
# * v1.0.3 (2022-09-07): Initial version.
VERSION_NAME = 'slideThumb'
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
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"                                   {VERSION_NAME}: extract thumbnails images ")
    print(f"\n* Version          : {VERSION}")
    print(f"* Last update      : {VERSION_DATE}")
    print(f"* Written by       : Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com")
    print(f"* Inspired by      : choosehappy | https://github.com/choosehappy\n")
    print("* Description      : This script will get thumbnails from (a list of given) images for quick inspection.\n")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")

def print_footer():
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+ The MIT License (MIT)                                                                                           +")
    print(f"+ {COPYRIGHT}                          +")
    print("+ Reference: http://opensource.org.                                                                               +")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

# Argument parser
def parse_arguments():
    parser = argparse.ArgumentParser(
        prog=VERSION_NAME,
        description=f'''
+ {VERSION_NAME} v{VERSION} +

This script will get thumbnails from (a list of given) images for quick inspection.''',
        usage='python3 slideThumb.py -i/--input; optional: -d/--display -o/--outdir -s/--suffix -t/--type -f/--force -v/--verbose; for help: -h/--help''',
        epilog=f'''
+ {VERSION_NAME} v{VERSION}. {COPYRIGHT} +\nThe MIT License (MIT)\nReference: http://opensource.org
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-d', '--display', help="Also show thumbnail on display, default simply writes thumbnails. Optional.", action='store_true')
    parser.add_argument('-o', '--outdir', help="Output dir, default is present working directory. Optional.", default="<<SAME>>", type=str)
    parser.add_argument('-s', '--suffix', help="Suffix to append to end of file, default is 'thumb' for thumbnail. Optional.", default="", type=str)
    parser.add_argument('-t', '--type', help="Output file type, default is png (which is slower), other options are tif. Optional.", default="png", type=str)
    parser.add_argument('-f', '--force', help="Force output even if it exists. Optional.", default=False, action='store_true')
    parser.add_argument('-v', '--verbose', help="While writing images also display image properties. Optional.", default=False, action='store_true')
    parser.add_argument('-V', '--version', action='version', version=VERSION_NAME + ' v' + VERSION + ' (' +  VERSION_DATE + ') | ' + COPYRIGHT)

    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-i', '--input', help="Input (directory containing files). Try: IMG012.ndpi (or *.TIF or /path_to/images/*.ndpi).", nargs="*")
    
    return parser.parse_args()

def validate_input(args):
    import glob
    if not args.input:
        print("\nOh, computer says no! You must supply correct arguments when running *** slideThumb ***!")
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
    from pathlib import Path

    for fname in files:
        # Determine output directory
        outdir = args.outdir if args.outdir != "<<SAME>>" else os.path.dirname(os.path.realpath(fname))
        os.makedirs(outdir, exist_ok=True)
        
        print(f"Output directory set to [{outdir}].")
        
        fnameout = f"{Path(fname).stem}{args.suffix}.!!.{args.type if args.type[0] == '' else ''+args.type}"
        fnameout = Path(outdir, fnameout)

        if not args.force and os.path.exists(fnameout):
            print(f"Skipping {fnameout} as output file exists and --force is not set")
            continue

        fimage = openslide.OpenSlide(fname)
        img = np.asarray(fimage.associated_images["macro"])[:, :, 0:3]
        img_r = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        if args.display:
            display_image(fname, img_r)
        elif args.verbose:
            print_verbose_info(fname, img)
            cv2.imwrite(str(fnameout).replace("!!", "thumb"), cv2.cvtColor(img_r, cv2.COLOR_RGB2BGR))
        else:
            print(f"Writing thumbnail for [{fname}].")
            cv2.imwrite(str(fnameout).replace("!!", "thumb"), cv2.cvtColor(img_r, cv2.COLOR_RGB2BGR))

def print_verbose_info(fname, img):
    print(f"Processing [{fname}].")
    print(f"* Image dimensions (height x width in pixels): {img.shape}")
    img_size = img.size / 1024  # to get kilobytes
    print(f"* Image size: {'{:,.2f}'.format(img_size)} KB")

def display_image(fname, img_r):
    import cv2
    print(f"Displaying [{fname}].")
    print(f"* Image dimensions (height x width in pixels): {img_r.shape}")
    img_size = img_r.size / 1024  # to get kilobytes
    print(f"* Image size: {'{:,.2f}'.format(img_size)} KB")

    cv2.imshow("slidePreview", cv2.cvtColor(img_r, cv2.COLOR_RGB2BGR))
    print("(hit any key on the image to close)")
    cv2.waitKey()  # Wait for any key press
    cv2.destroyAllWindows()
    cv2.waitKey(1)

if __name__ == "__main__":
    args = parse_arguments()
    print_header()
    files = validate_input(args)
    process_images(files, args)
    print_footer()
