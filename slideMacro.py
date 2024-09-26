#!/usr/bin/env python3
#
# script to extract macro images (and display) from whole-slide image files (*.TIF, *.NDPI, etc.)
#
# Ref: https://github.com/choosehappy/Snippets/blob/master/extract_macro_level_from_wsi_image_openslide_cli.py
#

import argparse
import textwrap
import os
from sys import exit
from pathlib import Path
import glob

# Version information
# Change log:
# * v1.1.0 (2024-09-26): Overhaul to make the script more modular, define functions, and easier to read.
# * v1.0.3 (2023-12-15): Initial version.
VERSION_NAME = 'slideMacro'
VERSION = '1.1.0'
VERSION_DATE = '2024-09-26'
COPYRIGHT = 'Copyright 1979-2024. Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com | https://vanderlaanand.science.'

# Define the header
def print_header():
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"                                   {VERSION_NAME}: extract macro images ")
    print(f"\n* Version          : {VERSION}")
    print(f"* Last update      : {VERSION_DATE}")
    print(f"* Written by       : Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com")
    print(f"* Inspired by      : choosehappy | https://github.com/choosehappy\n")
    print("* Description      : This script will get macro-images at a given level of magnification from")
    print("                     (a list of given) images for quick inspection.")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")

# Define the footer
def print_footer():
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"+ The MIT License (MIT)                                                                                           +")
    print(f"+ {COPYRIGHT}                          +")
    print("+ Reference: http://opensource.org.                                                                               +")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

# Argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(
        prog=VERSION_NAME,
        description=f'''
+ {VERSION_NAME} v{VERSION} +

This script will get macro-images at a given level of magnification from (a list of given) images for quick inspection.''',
        usage='python3 slideMacro.py -i/--input -l/--level; optional: -d/--display -o/--outdir -s/--suffix -t/--type -f/--force -v/--verbose; for help: -h/--help',
        epilog=f'''
+ {VERSION_NAME} v{VERSION}. {COPYRIGHT} +\nThe MIT License (MIT)\nReference: http://opensource.org
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-d', '--display', help="Also show macro on display, default simply writes macro. Optional.", action="store_true")
    parser.add_argument('-o', '--outdir', help="Output dir, default is the input image(s) directory. Optional.", default="<<SAME>>", type=str)
    parser.add_argument('-s', '--suffix', help="Suffix to append to end of file, default is 'macro'. Optional.", default="macro", type=str)
    parser.add_argument('-t', '--type', help="Output file type, default is png (which is slower), other options are tif. Optional.", default="png", type=str)
    parser.add_argument('-f', '--force', help="Force output even if it exists. Optional.", default=False, action="store_true")
    parser.add_argument('-v', '--verbose', help="While writing images also display image properties. Optional.", default=False, action="store_true")
    parser.add_argument('-V', '--version', action='version', version=VERSION_NAME + ' v' + VERSION + ' (' +  VERSION_DATE + ') | ' + COPYRIGHT)

    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument('-i', '--input', help="Input (directory containing files). Try: IMG012.ndpi (or *.TIF or /path_to/images/*.ndpi).", nargs="*", required=True)
    required_named.add_argument('-l', '--level', help="Magnification level to extract, with '5' as level 5. Try: 5.", required=True)

    return parser.parse_args()

# Validate inputs
def validate_input(args):
    if not args.input or not args.level:
        print("\nOh, computer says no! You must supply correct arguments when running a *** slideMacro ***!")
        print("Note that -i/--input and -l/--level are required.")
        exit()

    if len(args.input) > 1:
        return args.input
    else:
        return glob.glob(args.input[0])

# Check and handle output directories
def prepare_output_directory(args, fname):
    if args.outdir == "<<SAME>>":
        outdir = os.path.dirname(os.path.realpath(fname))
    else:
        os.makedirs(args.outdir, exist_ok=True)
        outdir = args.outdir
    return outdir

# Extract macro image
def extract_macro_image(fname, level, args):
    import openslide
    import numpy as np
    import cv2

    fimage = openslide.OpenSlide(fname)
    level = int(level)
    img = fimage.read_region((0, 0), level, fimage.level_dimensions[level])
    img = np.asarray(img)[:, :, 0:3]

    return img

# Display the macro image using OpenCV
def display_image(img, fname, level):
    import cv2

    print(f"Displaying [{fname}] at level [{level}].")
    print(f'* image dimensions (height x width in pixels): {img.shape}')
    img_size = img.size / 1024
    print(f'* image size: {img_size:,.2f} KB')

    img_r = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    cv2.imshow('slidePreview', cv2.cvtColor(img_r, cv2.COLOR_RGB2BGR))
    print('(hit any key on the image to close)')
    cv2.waitKey()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

# Save the macro image to file
def save_image(img, fnameout, args):
    import cv2

    print(f"Writing macro for [{fnameout.stem}] at level.")
    cv2.imwrite(str(fnameout), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

# Main processing loop
def process_images(files, args):
    for fname in files:
        # Prepare the output directory
        outdir = prepare_output_directory(args, fname)
        print(f"Output directory set to [{outdir}].")

        # Prepare output file name
        fnameout = Path(outdir, f"{Path(fname).stem}.{args.suffix}.{args.type}")
        if not args.force and os.path.exists(fnameout):
            print(f"Skipping {fnameout} as output file exists and --force is not set")
            continue

        # Extract the macro image
        img = extract_macro_image(fname, args.level, args)

        # Display the image if requested
        if args.display:
            display_image(img, fname, args.level)
        elif args.verbose:
            print(f"Processing [{fname}] at level [{args.level}].")
            print(f'* image dimensions (height x width in pixels): {img.shape}')
            img_size = img.size / 1024
            print(f'* image size: {img_size:,.2f} KB')
            save_image(img, fnameout, args)
        else:
            save_image(img, fnameout, args)

if __name__ == "__main__":
    args = parse_arguments()

    print_header()
    files = validate_input(args)
    process_images(files, args)
    print_footer()
