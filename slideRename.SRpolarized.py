#!/usr/bin/env python3

"""
slideRenameSRpolarized.py

This script renames SR_POLARIZED whole-slide images which are stored as .tif files 
and are named according to the T_NUMBER, {T_NUMBER}.tif. The script renames the files 
to {STUDY_TYPE}{STUDY_NUMBER}.{T_NUMBER}.SR_POLARIZED.tif.

This script renames the .tif files in a directory (`--input-dir`) based on a lookup table 
in a database file (`--input-db`) of either CSV or SPSS format. 
The database should contain the following columns: 
- STUDY_NUMBER, e.g., AE1234,
- T_NUMBER, e.g., T01-12345,
- UPID, e.g., UPID01234,
- informedconsent, e.g. 1. 

The `--studytype` flag should be used to specify the study type prefix (e.g., AE, AAA). 
All changes are logged to a log file (`--log`).

Additional options:
- `--verbose` to output more detailed information.
- `--dry-run` to perform a dry run (report in the terminal, no actual file operations).
- `--version` to show the program's version number and exit.

Example usage:
    python3 slideRenameSRpolarized.py --input-db "input.csv csv" --input-dir /path/to/tif/files --studytype AE --log logfilename --verbose --dry-run

Options:
    -i, --input-db: Input database file (CSV or SPSS). Specify the filename followed by the type (csv or spss). Required.
    -d, --input-dir: Input directory containing .tif files to be renamed. Required.
    -s, --studytype: Study type prefix (e.g., AE, AAA). Required.
    -l, --log: Base name for log file. Appended with .rename_sr_polarized.log. Required.
    -v, --verbose: Enable verbose mode for more detailed output. Optional.
    -n, --dry-run: Perform a dry run (report in the terminal, no actual file operations). Optional.
    -V, --version: Show program's version number and exit.

"""

# Version information
# Change log:
# * v1.0.11 (2024-10-16): Fixed an issue with the logger.
# * v1.0.10 (2024-10-16): Modified to only load relevant columns from SPSS to avoid datetime errors and added installation of pyreadstat.
# * v1.0.9 (2024-10-16): Added functionality to install `pyreadstat` via conda if it is not found.
# * v1.0.8 (2024-10-16): Modified `--input-db` to accept file name and format in a single argument (e.g., "filename.csv csv").
# * v1.0.7 (2024-10-16): Added `--input-db` option to handle both CSV and SPSS formats.
# * v1.0.6 (2024-10-16): Fixed issue where the logging info was not correctly displayed.
# * v1.0.5 (2024-10-16): Fixed an issue where the extension was not correctly added to the new filename. Fixed an issue where the version number was not correctly added to the new filename.
# * v1.0.4 (2024-10-16): Fixed an issue where the script was slow.
# * v1.0.3 (2024-10-16): Expanded --help message with more detailed information. 
# * v1.0.2 (2024-10-16): Fixed issue where different variations of T-numbers were not handled properly. Added --studytype.
# * v1.0.1 (2024-10-16): Fixed issue where T-numbers were not correctly extracted from filenames, and padded the number after the dash to 5 digits.
# * v1.0.0 (2024-10-16): Initial version.
VERSION_NAME = 'slideRenameSRpolarized'
VERSION = '1.0.11'
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

# Import required packages
import glob
import argparse
import os
import re
import subprocess

# Set up logger function
def setup_logger(log_name, log_file, verbose):
    import logging  # Import logging here to avoid unnecessary imports
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(log_file + '.rename_sr_polarized.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Function to check if pyreadstat is installed and install it if necessary
def check_and_install_pyreadstat():
    try:
        import pyreadstat
    except ImportError:
        print("pyreadstat is not installed. Attempting to install it using conda...")
        try:
            subprocess.check_call(["conda", "install", "-y", "pyreadstat"])
            import pyreadstat  # Try again after installation
        except subprocess.CalledProcessError as e:
            print(f"Failed to install pyreadstat: {e}. Please install it manually using 'conda install pyreadstat'.")

# Function to add version suffix (v1, v2, v3, etc.) to avoid overwriting files
def add_version_if_exists(filepath):
    base, ext = os.path.splitext(filepath)
    version = 1
    new_filepath = filepath
    while os.path.exists(new_filepath):
        new_filepath = f"{base}.v{version}{ext}"
        version += 1
    return new_filepath

# Function to extract T-number and additional info
def extract_tnum_and_info(filename):
    # Regular expression to match T-number pattern (e.g., T01-12345 or T1-12345)
    match = re.search(r'(T\d{1,2})[-_ ](\d+)', filename)  # Handles separators like _, space, or -
    if match:
        tnum_part1 = match.group(1)  # Txx part (T1 or T01)
        tnum_part2 = match.group(2).zfill(5)  # Ensure the number after the separator has 5 digits
        tnum = f"{tnum_part1}-{tnum_part2}"
        # Remove T-number from the rest of the filename and get the additional info
        additional_info = filename.replace(match.group(0), "").replace(".tif", "").strip().replace(" ", ".")
        return tnum, additional_info
    else:
        return None, None  # Return None if no match is found

# Function to load the database (CSV or SPSS) and only extract relevant columns
def load_database(input_db, db_type):
    import pandas as pd  # Import pandas here to avoid unnecessary imports
    check_and_install_pyreadstat()  # Ensure pyreadstat is installed
    if db_type == 'csv':
        return pd.read_csv(input_db)
    elif db_type == 'spss':
        import pyreadstat
        return pyreadstat.read_sav(input_db, usecols=['STUDY_NUMBER', 'T_NUMBER', 'UPID', 'informedconsent'])[0]
    else:
        raise ValueError("Unsupported database type. Use 'csv' or 'spss'.")

# Main renaming function
def rename_tif_files(input_db, db_type, input_dir, studytype, log_filename, verbose, dry_run):
    # Set up logging
    logger = setup_logger("slideRenameRSpolarized", log_filename, verbose)
    
    # Load the input database
    logger.info(f"Loading database from {input_db} as {db_type}.")
    TNUMDF = load_database(input_db, db_type)

    # Process all TIF files in the input directory
    for tif in glob.glob(os.path.join(input_dir, "*.tif")):
        # Remove spaces from file name for processing
        tif_no_space = tif.replace(" ", "")
        
        # Extract T-number and additional info from the filename
        tnum, additional_info = extract_tnum_and_info(tif)
        
        if tnum:
            # Match T-number with the database data to get the STUDY_NUMBER
            index = TNUMDF.index[TNUMDF['T_NUMBER'] == tnum]
            if index.any():
                index = index[0]
                SAMPLEID = studytype + str(TNUMDF.at[index, 'STUDY_NUMBER'])  # Use studytype flag value here
                # Adding SR_POLARIZED to the file name
                newname = os.path.join(input_dir, f"{SAMPLEID}.{tnum}.SR_POLARIZED.TIF")
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
                    # In dry run mode, log the rename and simulate it
                    logger.info(f"Dry run: {origname} would be renamed to {newname}")
                    if verbose:
                        print(f"Dry run: {origname} would be renamed to {newname}")
            else:
                logger.warning(f"T_NUMBER {tnum} not found in {input_db}. Skipping file: {tif}")
                if verbose:
                    print(f"Warning: T_NUMBER {tnum} not found in {input_db}. Skipping file: {tif}")
        else:
            logger.warning(f"Could not extract T_NUMBER from {tif}. Skipping file.")
            if verbose:
                print(f"Warning: Could not extract T_NUMBER from {tif}. Skipping file.")

# Main function
def main():
    # Import required packages
    import time
    from datetime import timedelta
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=f'''
+ {VERSION_NAME} v{VERSION} +
This script renames SR_POLARIZED whole-slide images which are stored as .tif files 
and are named according to the T_NUMBER, [T_NUMBER].tif. The script renames the files 
to [STUDY_TYPE][STUDY_NUMBER].[T_NUMBER].SR_POLARIZED.tif.

This script renames the .tif files in a directory (`--input-dir`) based on a lookup table 
in a database file (`--input-db`) in either CSV or SPSS format. The database should contain 
STUDY_NUMBER and T_NUMBER columns.

Additional options:
- `--verbose` to output more detailed information.
- `--dry-run` to perform a dry run (report in the terminal, no actual file operations).
- `--version` to show the program's version number and exit.

Example usage:
    python3 slideRenameSRpolarized.py --input-db "input.csv csv" --input-dir /path/to/tif/files --studytype AE --log logfilename --verbose --dry-run
        ''',
        epilog=f'''
+ {VERSION_NAME} v{VERSION}. {COPYRIGHT} \n{COPYRIGHT_TEXT}+''', 
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i", "--input-db", type=str, nargs=2, metavar=("FILE", "TYPE"),
                        help="Input database file (CSV or SPSS). Specify the filename followed by the type (csv or spss). Required.")
    parser.add_argument("-d", "--input-dir", type=str, required=True,
                        help="Input directory containing .tif files to be renamed. Required.")
    parser.add_argument("-s", "--studytype", type=str, required=True,
                        help="Study type prefix (e.g., AE, AAA). Required.")     
    parser.add_argument("-l", "--log", type=str, required=True,
                        help="Base name for log file. Appended with .rename_sr_polarized.log. Required.")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Enable verbose mode for more detailed output. Optional.")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Perform a dry run (report in the terminal, no actual file operations). Optional.")
    parser.add_argument("-V", "--version", action="version",
                        version=f'%(prog)s {VERSION} ({VERSION_DATE}).')

    args = parser.parse_args()

    start_time = time.time()  

    # Set up the logger
    logger = setup_logger(VERSION_NAME, args.log, args.verbose)

    logger.info(f"+ {VERSION_NAME} {VERSION} ({VERSION_DATE}) +")
    logger.info(f"Renaming .tif files for SR_POLARIZED whole-slide images.")

    # Report the input arguments
    logger.info(f"Input DB..........: {args.input_db[0]}")
    logger.info(f"DB Type...........: {args.input_db[1]}")
    logger.info(f"Input directory...: {args.input_dir}")
    logger.info(f"Study type........: {args.studytype}")
    logger.info(f"Log file..........: {args.log}")
    logger.info(f"Dry run...........: {args.dry_run}")
    logger.info(f"Verbose...........: {args.verbose}")

    if args.dry_run:
        logger.info("Dry run mode: no actual file operations will be performed.")

    # Call the renaming function
    rename_tif_files(args.input_db[0], args.input_db[1], args.input_dir, args.studytype, args.log, args.verbose, args.dry_run)

    # Execution time reporting
    elapsed_time = time.time() - start_time
    formatted_time = str(timedelta(seconds=elapsed_time))

    logger.info(f"Script total execution time: {formatted_time}")
    
if __name__ == '__main__':
    main()

# Print the version number
print(f"\n+ {VERSION_NAME} v{VERSION} ({VERSION_DATE}). {COPYRIGHT} +")
print(f"{COPYRIGHT_TEXT}")
