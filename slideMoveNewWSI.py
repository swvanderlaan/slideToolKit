#!/usr/bin/env python3

"""
slideMoveNewWSI.py

This script moves *.ndpi files from an input folder to a destination folder based on specified 
study type (--study-type AE) and stain name (--stain). It checks if the AE-studynumber is already 
present in the destination folder (--destination) before moving any files. It prioritizes multiplicates 
according to certain rules. It provides options (`--verbose`) to output information about the 
multiplicates and log statistics using `--log`.

Images are expected to be of the form `study_typestudy_number.[additional_info.]stain.[random_info.]file_extension`, 
e.g., `AE1234.T01-12345.CD34.ndpi`, where `AE` is the `study_type`, `1234` is the `study_number`, 
`T01-12345` is the `additional_info` and optional, `CD34` is the stain name, and `ndpi` is the `file_extension`. 
The `random_info` is optional and can be any random string of characters, e.g. `2017-12-22_23.54.03`. The 
`file_extension` is expected to be `ndpi` or `TIF` for the original image files. 

The script will move all files with the same `study_number` and `stain` name to the duplicate folder. It will 
prioritize the files based on the following criteria:
- There is a ndpi > keep ndpi, `keep_this_one`
- Different creation date > keep latest file, `different_date_kept_latest`
- Same date, different type > keep ndpi, `same_date_diff_type_kept_ndpi`
- Same date, same type, different checksum > keep biggest, `same_date_same_type_diff_checksum_biggest`
- Same date, same type, same checksum > keep first one, `same_date_same_type_same_checksum_keep_this_one`
- When none of the above apply > `cannot_assign_priority`

Optionally, it can perform a dry run (--dry_run) to report the operations without actually moving, 
and print detailed operations for each file (--verbose).

Usage:
python slideMoveNewWSI.py --input /path/to/input --study-type AE --stain CD34 --destination /path/to/destination [options]

Options:
    --input, -i        Specify the input folder where images are located. Required.
    --study-type, -t   Specify the study type prefix, e.g., AE. Required.
    --stain, -s        Specify the stain name, e.g., CD34. Required.
    --destination, -d  Specify the destination folder to move the files. Required.
    --log, -l          Specify the log file name to write statistics. Optional.
    --dry-run, -n      Perform a dry run (report in the terminal, no actual file operations). Optional.
    --verbose, -v      Print detailed operations for each file. Optional.
    --help, -h         Print this help message and exit. Optional.
"""

# Version information
# Change log:
# * v1.0.0 (2024-10-14): Initial version.
VERSION_NAME = 'slideMoveNewWSI'
VERSION = '1.0.0'
VERSION_DATE = '2024-10-14'
COPYRIGHT = 'Copyright 1979-2024. Tim S. Peters & Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com | https://vanderlaanand.science.'
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
import os
import argparse
import shutil
import pandas as pd
import hashlib
from collections import defaultdict
from datetime import timedelta
import time

# Calculate the checksum of a file
def calculate_checksum(file_path):
    '''Calculate the checksum of a file.'''
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to get the study number from a file name
def get_study_number(file_name, study_type):
    '''Extract the study number from a file name.'''
    if file_name.startswith(study_type):
        parts = file_name.split('.', 1)
        if len(parts) > 0:
            return parts[0]  # Extract AE1234
    return None

# Function to rename input file if a duplicate exists
def get_next_version_filename(file_path):
    '''Get the next version filename (e.g., .v2, .v3) if a duplicate exists.'''
    base, ext = os.path.splitext(file_path)
    version = 2
    while os.path.exists(file_path):
        file_path = f"{base}.v{version}{ext}"
        version += 1
    return file_path

# Function to move files to duplicates folder with optional renaming for input
def move_to_duplicates(file_path, duplicate_folder, from_input=False, dry_run=False, verbose=False):
    '''Move the file to the duplicate folder. If from_input is True, rename to v2, v3, etc.'''
    if from_input:
        duplicate_file = get_next_version_filename(os.path.join(duplicate_folder, os.path.basename(file_path)))
    else:
        duplicate_file = os.path.join(duplicate_folder, os.path.basename(file_path))

    if os.path.exists(duplicate_file):
        if verbose:
            print(f"File {duplicate_file} already exists in duplicates. Skipping move.")
        return duplicate_file  # Skip moving since it's already in duplicates.

    try:
        if not dry_run:
            shutil.move(file_path, duplicate_file)
        else:
            print(f"Dry-run mode: would be moving {file_path} > {duplicate_file}")
        if verbose:
            print(f"  - {file_path} > {duplicate_file} (moved to duplicates)")
    except Exception as e:
        print(f"Error moving {file_path} to {duplicate_file}: {e}")
        raise

    return duplicate_file

# Function to preprocess file type for prioritization
def process_prioritization(metadata_df, verbose=False):
    '''Process the metadata for prioritization.'''
    study_numbers = defaultdict()
    for snr in metadata_df['study_number'].unique():
        study_number_df = metadata_df.loc[metadata_df['study_number'] == snr]
        study_numbers[snr] = study_number_df

    for study_number, study_number_df in study_numbers.items():
        if verbose:
            print(f"> Processing {study_number} with {len(study_number_df)} files")
        
        if study_number_df['filetype'].nunique() > 1:
            ndpi_files = study_number_df.loc[study_number_df['filetype'] == '.ndpi']
            prioritized_file = prioritize_files(ndpi_files)
        else:
            prioritized_file = prioritize_files(study_number_df)
        
        reason = f"{list(prioritized_file.values())[0]['filetype'].replace('.','')}_{list(prioritized_file.values())[1]}"
        filename = list(prioritized_file.values())[0]['filename']
        if verbose:
            print(f' Prioritized file: {filename} - Reason: {reason}')
        metadata_df.loc[metadata_df['filename'] == filename, 'priority'] = reason

    return metadata_df

# Function returning a prioritized list of the same study_number
def prioritize_files(files):
    '''Prioritize the files based on certain criteria.'''
    if len(files) == 1:
        return {'metadata': files.iloc[0], 'priority': 'keep_this_one'}    

    if files['file_mod_date'].nunique() > 1:
        files_sorted_by_date = files.sort_values(by='file_mod_date', ascending=[False])
        kept_file = files_sorted_by_date.iloc[0]
        prioritized_file = {'metadata': kept_file, 'priority': 'different_date_kept_latest'}
    else:
        if files['checksum'].nunique() > 1:
            files_same_type = files.sort_values(by=['filesize'], ascending=[False])
            kept_file = files_same_type.iloc[0]
            prioritized_file = {'metadata': kept_file, 'priority': 'same_date_same_type_diff_checksum_biggest'}
        elif files['checksum'].nunique() == 1:
            kept_file = files.iloc[0]
            prioritized_file = {'metadata': kept_file, 'priority': 'same_date_same_type_same_checksum_keep_this_one'}
        else:
            prioritized_file = {'metadata': None, 'priority': 'cannot_assign_priority'}

    return prioritized_file

# Function to move and prioritize ndpi files
def move_and_prioritize_files(input_folder, study_type, stain, destination_folder, dry_run=False, verbose=False):
    '''Move and prioritize ndpi files based on study type and stain name.'''
    duplicates_folder = os.path.join(destination_folder, '_duplicates')

    files_metadata = []
    unique_samples = set()  # Track unique study numbers
    duplicate_study_numbers = set()  # Track duplicates

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.ndpi') and stain in file:
                study_number = get_study_number(file, study_type)
                if study_number:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(destination_folder, file)

                    # Check if the file exists in the destination folder
                    if os.path.exists(dest_file):
                        if verbose:
                            print(f"Duplicate found for {study_number}. Moving destination file to duplicates and renaming input.")
                        duplicate_study_numbers.add(study_number)

                        # Move the destination file to _duplicates without renaming
                        move_to_duplicates(dest_file, duplicates_folder, from_input=False, dry_run=dry_run, verbose=verbose)

                        # Move and rename the input file to _duplicates (e.g., v2, v3)
                        moved_input_file = move_to_duplicates(src_file, duplicates_folder, from_input=True, dry_run=dry_run, verbose=verbose)

                        if not dry_run:
                            # Only calculate checksum and file metadata if not in dry-run mode
                            file_checksum = calculate_checksum(moved_input_file)
                            file_size = os.path.getsize(moved_input_file)
                            file_mod_date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(moved_input_file)))
                            files_metadata.append({
                                'study_number': study_number,
                                'filename': moved_input_file,
                                'file_mod_date': file_mod_date,
                                'checksum': file_checksum,
                                'filesize': file_size,
                                'filetype': '.ndpi'
                            })
                    else:
                        # Move files to the destination folder
                        if verbose:
                            print(f"Moving {file} to {destination_folder}")
                        if not dry_run:
                            shutil.move(src_file, dest_file)
                        unique_samples.add(study_number)

    if not dry_run and files_metadata:
        files_df = pd.DataFrame(files_metadata)
        prioritized_metadata = process_prioritization(files_df, verbose)

        if verbose:
            print("Prioritization process completed.")
        return unique_samples, duplicate_study_numbers, prioritized_metadata
    return unique_samples, duplicate_study_numbers, None

# Function to write log statistics to a file
def write_log(log_file_path, study_type, stain, unique_samples, duplicate_study_numbers, prioritized_metadata, start_time, formatted_time):
    '''Write log statistics to a file.'''

    try:
        with open(log_file_path, 'w') as log_file:
            log_file.write(f"+ {VERSION_NAME} v{VERSION} ({VERSION_DATE}) +\n")
            log_file.write(f"\nIdentified and moved multiplicate image files based on specified criteria for:\n> study_type: {study_type}\n> stain: {stain}\n")
            log_file.write(f"\nTotal unique samples for stain {stain}: {len(unique_samples)} | {unique_samples}\n")
            log_file.write(f"Total multiplicity files found: {len(duplicate_study_numbers)}\n")

            if prioritized_metadata is not None:
                log_file.write(f"Total unique multiplicity files found: {len(prioritized_metadata)}. Including:\n")
                for _, row in prioritized_metadata.iterrows():
                    log_file.write(f"> {row['study_number']}: {row['filename']}\n")
            else:
                log_file.write(f"No prioritized duplicates were found.\n")

            log_file.write(f"\nScript total execution time was {formatted_time} ({time.time() - start_time:.2f} seconds).\n")
            log_file.write(f"\n+ {VERSION_NAME} v{VERSION}. {COPYRIGHT} +\n")

    except Exception as e:
        print(f"Error: Unable to write to the log file: {e}")
        raise

# Main function
def main():
    parser = argparse.ArgumentParser(description="Move WSI files for a specific study type and stain, checking if the study number already exists in the destination.")
    parser.add_argument('--input', '-i', required=True, help='Specify the input folder where images are located. Required.')
    parser.add_argument('--study-type', '-t', required=True, help='Specify the study type prefix, e.g., AE. Required.')
    parser.add_argument('--stain', '-s', required=True, help='Specify the stain name, e.g., CD34. Required.')
    parser.add_argument('--destination', '-d', required=True, help='Specify the destination folder to move the files. Required.')
    parser.add_argument('--log', '-l', required=False, help='Specify the log file path. Optional.')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Perform a dry run (no actual file operations). Optional.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed operations for each file. Optional.')

    args = parser.parse_args()

    start_time = time.time()

    print(f"+ {VERSION_NAME} v{VERSION} ({VERSION_DATE}) +")
    print(f"\nMove new WSI files based on study type and stain name.")

    # Report the input arguments
    print(f"\nInput folder.......: {args.input}")
    print(f"Study type...........: {args.study_type}")
    print(f"Stain................: {args.stain}")
    print(f"Destination folder...: {args.destination}")
    print(f"Dry run..............: {args.dry_run}")
    print(f"Verbose..............: {args.verbose}")
    print(f"Log file.............: {args.log}")

    if args.dry_run:
        print("\nDry run mode: no actual file operations will be performed.")
    # Check if the input and destination folders exist
    if not os.path.exists(args.input):
        print(f"Error: Input folder '{args.input}' does not exist.")
        raise FileNotFoundError(f"Input folder '{args.input}' does not exist.")
    
    if not os.path.exists(args.destination):
        print(f"Error: Destination folder '{args.destination}' does not exist.")
        raise FileNotFoundError(f"Destination folder '{args.destination}' does not exist.")

    # Create the _duplicates folder if it does not exist
    duplicates_folder = os.path.join(args.destination, '_duplicates')
    if args.verbose:
        print(f"Creating duplicates folder: {duplicates_folder}")
    if not os.path.exists(duplicates_folder):
        os.makedirs(duplicates_folder, exist_ok=True)

    # Log file path
    if args.log:
        log_dir = os.path.dirname(args.log)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(duplicates_folder, args.log + '.' + args.study_type + '.' + args.stain + '.movenewwsi.log')

    # Move and prioritize files
    unique_samples, duplicate_study_numbers, prioritized_metadata = move_and_prioritize_files(
        args.input, args.study_type, args.stain, args.destination, dry_run=args.dry_run, verbose=args.verbose)

    elapsed_time = time.time() - start_time
    time_delta = timedelta(seconds=elapsed_time)
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = round(time_delta.microseconds / 1000)
    formatted_time = f"{hours} hours, {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds"

    # Write log statistics
    if args.log:
        write_log(log_file_path, args.study_type, args.stain, unique_samples, duplicate_study_numbers, prioritized_metadata, start_time, formatted_time)
        print(f"Log saved to: {log_file_path}")

    print(f"Script total execution time: {formatted_time}")
    
if __name__ == '__main__':
    main()

# Print the version number
print(f"\n+ {VERSION_NAME} v{VERSION} ({VERSION_DATE}). {COPYRIGHT} +")
print(f"{COPYRIGHT_TEXT}")