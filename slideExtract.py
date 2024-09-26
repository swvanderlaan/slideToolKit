#!/usr/bin/env python3
#
# script to extract thumbnails and macros from whole-slide image files (*.TIF, *.NDPI, etc.)
#
# Ref: https://github.com/choosehappy/Snippets/blob/master/extract_macro_level_from_wsi_image_openslide_cli.py
#

import argparse
import textwrap
import os
import glob
import numpy as np
from pathlib import Path

# Version information
# Change log:
# * v1.1.0 (2024-09-26): Overhaul to make the script more modular, define functions, and easier to read.
# * v1.0.5 (2023-01-08): Initial version.
VERSION_NAME = 'slideExtract'
VERSION = '1.1.0'
VERSION_DATE = '2024-09-26'
COPYRIGHT = 'Copyright 1979-2024. Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com | https://vanderlaanand.science.'

# Define the header
def print_header():
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"                                   {VERSION_NAME}: extract thumbnails and macro images ")
    print(f"\n* Version          : {VERSION}")
    print(f"* Last update      : {VERSION_DATE}")
    print(f"* Written by       : Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com")
    print(f"* Description      : This script will extract thumbnails and macro images from whole-slide image (WSI) files.")
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

This script is designed to extract thumbnails and macro-images from whole-slide image (WSI) files, 
such as TIF or NDPI files. The script uses the OpenSlide library to handle WSI and OpenCV for image processing.
        ''',
        epilog=f'''
+ {VERSION_NAME} v{VERSION}. {COPYRIGHT} +\nThe MIT License (MIT)\nReference: http://opensource.org
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-d', '--display', help="Also show macro on display, default simply writes macro. Optional.", action="store_true")
    parser.add_argument('-o', '--outdir', help="Output dir, default is the input directory. Optional.", default="<<SAME>>", type=str)
    parser.add_argument('-s', '--suffix', help="Suffix to append to end of file, default is 'm' for thumbnail and '#' for a given level. Optional.", default="", type=str)
    parser.add_argument('-t', '--type', help="Output file type, default is png, other options are tif. Optional.", default="png", type=str)
    parser.add_argument('-f', '--force', help="Force output even if it exists. Optional.", default=False, action="store_true")
    parser.add_argument('-v', '--verbose', help="While writing images also display image properties. Optional.", default=False, action="store_true")
    parser.add_argument('-de', '--debug', help="Debug mode. Note: produces a lot of information. Optional.", default=False, action="store_true")
    parser.add_argument('-V', '--version', action='version', version=VERSION_NAME + ' v' + VERSION + ' (' +  VERSION_DATE + ') | ' + COPYRIGHT)

    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument('-i', '--input', help="Input (directory containing files). Try: IMG012.ndpi (or *.TIF or /path_to/images/*.ndpi).", nargs="*", required=True)
    required_named.add_argument('-l', '--levels', help="Comma-separated list of magnification levels to extract, with 'm' as thumbnail and '6' as level 6. Try: m,6.", required=True)

    return parser.parse_args()

# Validate inputs
def validate_input(args):
    if not args.input or not args.levels:
        print("\nOh, computer says no! You must supply correct arguments when running *** slideExtract ***!")
        print("Note that -i/--input and -l/--levels are required.")
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

# Extract and process images
def process_image_levels(fname, levels, args):
    import openslide
    import cv2

    try:
        fimage = openslide.OpenSlide(fname)
    except openslide.OpenSlideError as e:
        print(f"Error: Could not open file {fname} as a valid WSI image. {str(e)}")
        return
    
    fname_base = Path(fname).stem

    for level in levels.split(","):
        # Set the level
        if level == 'm':
            img = fimage.associated_images.get("macro")
            if img is None:
                print(f"No thumbnail (macro) available for [{fname}].")
                continue
        else:
            try:
                level = int(level)
                img = fimage.read_region((0, 0), level, fimage.level_dimensions[level])
            except (ValueError, IndexError):
                print(f"Error: Invalid level '{level}' for file {fname}.")
                continue
        
        img = np.asarray(img)[:, :, 0:3]

        # Create output filename
        outdir = prepare_output_directory(args, fname)
        fnameout = Path(outdir, f"{fname_base}{args.suffix}.{level}.{args.type}")

        if not args.force and os.path.exists(fnameout):
            print(f"Skipping [{fnameout}] as output file exists and --force is not set.")
            continue
        
        # Verbose logging
        if args.verbose:
            print(f"Processing [{fname}] at level [{level}].")
            print(f'* Image dimensions (height x width in pixels): {img.shape}')
            img_size = img.size / 1024
            print(f'* Image size: {img_size:,.2f} KB')

        # Write the image
        try:
            cv2.imwrite(str(fnameout), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        except Exception as e:
            print(f"Error: Could not write image file {fnameout}. {str(e)}")

        # Display the image if requested
        if args.display:
            try:
                img_r = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                cv2.imshow(f'slidePreview - {fname_base} - Level {level}', cv2.cvtColor(img_r, cv2.COLOR_RGB2BGR))
                cv2.waitKey()
                cv2.destroyAllWindows()
            except Exception as e:
                print(f"Error: Could not display image for {fname}. {str(e)}")

# Main processing loop
def process_files(files, args):
    for fname in files:
        process_image_levels(fname, args.levels, args)

# Main function
if __name__ == "__main__":
    args = parse_arguments()

    print_header()
    files = validate_input(args)
    process_files(files, args)
    print_footer()
