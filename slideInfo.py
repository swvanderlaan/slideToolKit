#!/usr/bin/env python3
#
# script to get whole-slide image information.
# Ref: https://lists.andrew.cmu.edu/pipermail/openslide-users/2015-May/001060.html
#

import argparse
import textwrap
import sys
import os
from datetime import datetime

# Version information
# Change log:
# * v1.1.0 (2024-09-26): Overhaul to make the script more modular, define functions, and easier to read.
# * v1.0.2 (2023-12-15): Initial version.
VERSION_NAME = 'slideInfo'
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
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Reference: http://opensource.org.
'''

# Define the header
def print_header():
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"                                      {VERSION_NAME}: whole-slide image information ")
    print(f"\n* Version          : {VERSION}")
    print(f"* Last update      : {VERSION_DATE}")
    print(f"* Written by       : Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com")
    print(f"* Suggested for by : Toby Cornish\n")
    print("* Description      : This script will get whole-slide image information from (a list of given) images ")
    print("                     for quick inspection.")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")

def print_footer():
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"+ The MIT License (MIT)                                                                                           +")
    print(f"+ {COPYRIGHT}                          +")
    print("+ Reference: http://opensource.org.                                                                               +")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog=VERSION_NAME,
        description=f'''
+ {VERSION_NAME} v{VERSION} +

This script will get whole-slide image information from (a list of given) images for quick inspection.''',
        usage='python3 slideInfo.py -i/--input [-h/--help] [--write STAIN]',
        epilog=f'''
+ {VERSION_NAME} v{VERSION}. {COPYRIGHT} +\nThe MIT License (MIT)\nReference: http://opensource.org
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-w', '--write', help="Write the output to a text file. Provide STAIN information (e.g., H&E). Optional.", type=str)
    parser.add_argument('-v', '--verbose', help="Will get all available image properties. Note: this produces a lot of information. Optional.", default=False, action="store_true")
    parser.add_argument('-V', '--version', action='version', version=VERSION_NAME + ' v' + VERSION + ' (' +  VERSION_DATE + ') | ' + COPYRIGHT)

    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-i', '--input', help="Input (directory containing files). Try: IMG012.ndpi (or *.TIF or /path_to/images/*.ndpi).", nargs="*")

    return parser.parse_args()

def validate_input(args):
    import glob
    if not args.input:
        print("\nOh, computer says no! You must supply correct arguments when running *** slideInfo ***!")
        print("Note that -i/--input is required. Try: AE107.HE.ndpi or AE-SLIDES/HE/*.ndpi.\n")
        exit()

    if len(args.input) > 1:
        return args.input
    else:
        return glob.glob(args.input[0])

def check_requirements():
    try:
        import openslide
        import numpy as np
        print("Requirements are met: OpenSlide and NumPy are installed.")
    except ImportError as e:
        print(f"Missing required module: {e.name}")
        if e.name == 'openslide':
            print("Installing OpenSlide Python bindings...")
            os.system("pip install openslide-python")
        elif e.name == 'numpy':
            print("Installing NumPy...")
            os.system("pip install numpy")
        else:
            raise e

def get_output_filename(stain, input_file):
    """Generate the output filename with date, stain, and the .info.txt extension."""
    date_prefix = datetime.now().strftime('%Y%m%d')
    if not os.path.isabs(stain):
        directory = os.path.dirname(input_file)  # Get directory of input file
        output_filename = os.path.join(directory, f"{date_prefix}.{stain}.info.txt")
    else:
        output_filename = f"{date_prefix}.{stain}.info.txt"

    return output_filename

def display_slide_info(fname, verbose=False, file_writer=None):
    import numpy as np
    import openslide

    slide = openslide.OpenSlide(fname)
    console_output = []
    file_output = []
    
    if verbose:
        # Verbose mode, write everything to both console and file
        console_output.append(f"Showing all image properties for [{fname}]:")
        for prop_key in slide.properties.keys():
            console_output.append(f"  Property: {prop_key}, value: {slide.properties.get(prop_key)}")
    else:
        # Only specific parts go to both console and file in non-verbose mode
        basic_info = [
            f"Showing some properties for slide [{fname}] with format: {slide.detect_format(fname)}",
            "Slide associated images:"
        ]
        console_output.extend(basic_info)
        file_output.extend(basic_info)
        
        for ai_key in slide.associated_images.keys():
            image_info = f"  {ai_key}: {slide.associated_images.get(ai_key)}"
            console_output.append(image_info)
            file_output.append(image_info)

        macroIm = slide.associated_images['macro']
        img = np.asarray(macroIm)[:, :, 0:3]
        img_size = img.size / 1024  # to get kilobytes
        image_dims = [
            f"* key-image dimensions (height x width in pixels): {img.shape}",
            f"* key-image size: {'{:,.2f}'.format(img_size)} KB",
            f"Slide dimensions: {slide.dimensions}",
            f"Slide objective power: {int(slide.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER])}",
            f"Available 'levels': {slide.level_count}",
            f"* level dimensions: {slide.level_dimensions}",
            f"* level downsamples: {slide.level_downsamples}"
        ]
        console_output.extend(image_dims)
        file_output.extend(image_dims)

    slide.close()

    # Print to console
    for line in console_output:
        print(line)

    # Write to file only the required output when not verbose
    if file_writer:
        if verbose:
            file_writer.write('\n'.join(console_output) + '\n\n')
        else:
            file_writer.write('\n'.join(file_output) + '\n\n')

def main():
    args = parse_arguments()
    check_requirements()
    
    print(f'Python version: {sys.version}')
    try:
        import openslide
        print(f'OpenSlide version: {openslide.__version__}')
        print(f'OpenSlide library version: {openslide.__library_version__}')
    except ImportError:
        print("OpenSlide is not installed. Exiting...")
        exit()

    files = validate_input(args)

    file_writer = None
    if args.write:
        # Generate the output filename with the given stain and the current date.
        output_filename = get_output_filename(args.write, files[0])
        try:
            file_writer = open(output_filename, 'w')
            print(f"Writing output to: {output_filename}")
        except Exception as e:
            print(f"Error: Unable to open the file for writing: {e}")
            exit()

    for fname in files:
        display_slide_info(fname, args.verbose, file_writer)

    if file_writer:
        file_writer.close()

if __name__ == "__main__":
    args = parse_arguments()

    print_header()
    main()
    print_footer()
