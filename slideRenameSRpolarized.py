#!/usr/bin/env python3

"""
slideRenameRSpolarized.py

This script renames SR_POLARIZED whole-slide images which are stored as .tif files 
and are named according to the T_NUMBER, {T_NUMBER}.tif. The script renames the files 
to AE{STUDY_NUMBER}.{T_NUMBER}.SR_POL.tif.

This script renames the .tif files in a directory (`--input-dir`) based on a lookup table 
in a CSV file (`--input-csv`). The CSV file should contain the following columns: 
- STUDY_NUMBER, e.g., AE1234,
- T_NUMBER, e.g., T01-12345; note that when no T_NUMBER is known, the column should be empty,
- UPID, e.g., UPID01234,
- informedconsent, e.g. 1. 
All changes are logged to a log file (`--log`).

Optionally, the script can output verbose information (`--verbose`).

Example usage:
    python3 slideRenameSRpolarized.py --input-csv input.csv --input-dir /path/to/tif/files --log logfilename --verbose

"""

# Version information
# Change log:
# * v1.0.1 (2024-10-16): Fixed issue where T-numbers were not correctly extracted from filenames, and padded the number after the dash to 5 digits.
# * v1.0.0 (2024-10-16): Initial version.
VERSION_NAME = 'slideRenameRSpolarized'
VERSION = '1.0.1'
VERSION_DATE = '2024-10-16'
COPYRIGHT = 'Copyright 1979-2024. Tim van de Kerkhof & Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com | https://vanderlaanand.science.'
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

import pandas as pd
import numpy as np
import glob
import os
import argparse
import logging
from datetime import timedelta
import time
import re

# Set up logger function
def setup_logger(log_name, log_file, verbose):
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Formatter for the log messages
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler to log to a file
    file_handler = logging.FileHandler(log_file + '.rename_sr_polarized.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Console handler to log to the console (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Function to add version suffix (v1, v2, v3, etc.) to avoid overwriting files
def add_version_if_exists(filepath):
    base, ext = os.path.splitext(filepath)
    version = 1
    new_filepath = filepath
    while os.path.exists(new_filepath):
        new_filepath = f"{base}_v{version}{ext}"
        version += 1
    return new_filepath

# Function to extract T-number and additional info
def extract_tnum_and_info(filename):
    # Regular expression to match T-number pattern (e.g., T01-12345)
    match = re.search(r'(T\d{2})-(\d+)', filename)
    if match:
        tnum_part1 = match.group(1)  # T01 part
        tnum_part2 = match.group(2).zfill(5)  # Pad the number after the dash to 5 digits
        tnum = f"{tnum_part1}-{tnum_part2}"
        # Remove T-number from the rest of the filename and get the additional info
        additional_info = filename.replace(match.group(0), "").replace(".tif", "").strip().replace(" ", ".")
        return tnum, additional_info
    else:
        return None, None  # Return None if no match is found

# Main renaming function
def rename_tif_files(input_csv, input_dir, log_filename, verbose, dry_run):
    # Set up logging
    logger = setup_logger("slideRenameRSpolarized", log_filename, verbose)
    
    # Read CSV
    logger.info(f"Reading TNUM_CONSENT from: {input_csv}")
    TNUMDF = pd.read_csv(input_csv)

    # Process all TIF files in the input directory
    for tif in glob.glob(os.path.join(input_dir, "*.tif")):
        # Remove spaces from file name for processing
        tif_no_space = tif.replace(" ", "")
        
        # Extract T-number and additional info from the filename
        tnum, additional_info = extract_tnum_and_info(tif)
        
        if tnum:
            # Match T-number with the CSV data to get the STUDY_NUMBER
            index = TNUMDF.index[TNUMDF['T_NUMBER'] == tnum]
            if index.any():
                index = index[0]
                SAMPLEID = "AE" + str(TNUMDF.at[index, 'STUDY_NUMBER'])
                newname = os.path.join(input_dir, f"{SAMPLEID}.{tnum}.{additional_info}.tif")
                origname = tif
                
                # Check if file with newname exists and add version if necessary
                newname = add_version_if_exists(newname)
                
                # Log and optionally print the renaming process
                logger.info(f"Renaming: {origname} to {newname}")
                if verbose:
                    print(f"Renaming: {origname} to {newname}")
                
                # Only perform renaming if not in dry-run mode
                if not dry_run:
                    os.rename(origname, newname)
                else:
                    logger.info(f"Dry run: {origname} would be renamed to {newname}")
                    if verbose:
                        print(f"Dry run: {origname} would be renamed to {newname}")
            else:
                logger.warning(f"T_NUMBER {tnum} not found in {input_csv}. Skipping file: {tif}")
                if verbose:
                    print(f"Warning: T_NUMBER {tnum} not found in {input_csv}. Skipping file: {tif}")
        else:
            logger.warning(f"Could not extract T_NUMBER from {tif}. Skipping file.")
            if verbose:
                print(f"Warning: Could not extract T_NUMBER from {tif}. Skipping file.")

# Main function
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=f'''
+ {VERSION_NAME} v{VERSION} +
This script renames .tif files in a directory (`--input-dir`) based on a lookup table 
in a CSV file (`--input-csv`). The CSV file should contain the following columns: 
- STUDY_NUMBER, 
- T_NUMBER, 
- UPID, 
- informedconsent. 
If there is no value the column should be empty. The .tif files are expected to be of 
the format T_NUMBER.tif. The script will rename the files to AE{STUDY_NUMBER}.{T_NUMBER}.SR_POL.tif.
All changes are logged to a log file (`--log`).

Optionally, the script can output verbose information (`--verbose`).

Example usage:
    python3 slideRenameSRpolarized.py --input-csv input.csv --input-dir /path/to/tif/files --log logfilename --verbose

        ''',
        epilog=f'''
+ {VERSION_NAME} v{VERSION}. {COPYRIGHT} \n{COPYRIGHT_TEXT}+''', 
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i", "--input-csv", type=str, required=True,
                        help="Input CSV file containing T_NUMBER and STUDY_NUMBER. Required.")
    parser.add_argument("-d", "--input-dir", type=str, required=True,
                        help="Input directory containing .tif files to be renamed. Required.")
    parser.add_argument("-l", "--log", type=str, required=True,
                        help="Base name for log file. Appended with .rename_sr_polarized.log. Required.")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Enable verbose mode for more detailed output. Optional.")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Perform a dry run (report in the terminal, no actual file operations). Optional.")
    parser.add_argument("-V", "--version", action="version",
                        version=f'%(prog)s {VERSION} ({VERSION_DATE}).')

    args = parser.parse_args()

    start_time = time.time()  # Add this line to start the timer
    
    # Set up the logger
    logger = setup_logger(VERSION_NAME, args.log, args.verbose)

    logger.info(f"\n+ {VERSION_NAME} {VERSION} ({VERSION_DATE}) +")
    logger.info(f"Renaming .tif files for SR_POLARIZED whole-slide images.")

    # Report the input arguments
    logger.info(f"\nInput CSV.......: {args.input_csv}")
    logger.info(f"Input directory.: {args.input_dir}")
    logger.info(f"Log file........: {args.log}")
    logger.info(f"Verbose.........: {args.verbose}")
    logger.info(f"Dry run.........: {args.dry_run}")

    if args.dry_run:
        logger.info("\nDry run mode: no actual file operations will be performed.")

    # Call the renaming function
    rename_tif_files(args.input_csv, args.input_dir, args.log, args.verbose, args.dry_run)

    # Execution time reporting
    elapsed_time = time.time() - start_time
    formatted_time = str(timedelta(seconds=elapsed_time))

    logger.info(f"\nScript total execution time: {formatted_time}")
    
if __name__ == '__main__':
    main()

# Print the version number
print(f"\n+ {VERSION_NAME} v{VERSION} ({VERSION_DATE}). {COPYRIGHT} +")
print(f"{COPYRIGHT_TEXT}")