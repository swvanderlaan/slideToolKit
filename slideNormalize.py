#!/usr/bin/env python3

import cv2
import os
import argparse


def is_file_exist(filename):
    """Check if a file exists."""
    return os.path.isfile(filename)


def replace_string(subject, search, replace):
    """Replace occurrences of a substring in a string with another string."""
    return subject.replace(search, replace)


def remove_extension(filename):
    """Remove the extension from a filename."""
    return os.path.splitext(filename)[0]


def normalize_slide_image(input_filename, output_filename, show=False):
    """Normalize an image using CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    print("Starting image normalization.")

    # Read RGB image and convert to Lab color space
    print("\t...Reading RGB color image and converting to Lab.")
    bgr_image = cv2.imread(input_filename)
    lab_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2Lab)

    # Extract the L channel
    print("\t...Extracting the L channel.")
    lab_planes = list(cv2.split(lab_image))

    # Apply CLAHE to the L channel
    print("\t...Applying the CLAHE algorithm to the L channel.")
    clahe = cv2.createCLAHE(clipLimit=2)
    lab_planes[0] = clahe.apply(lab_planes[0])

    # Merge the planes back into a Lab image
    print("\t...Merging color planes back into a Lab image.")
    lab_image = cv2.merge(lab_planes)

    # Convert back to BGR color space
    print("\t...Converting back to RGB color image.")
    image_clahe = cv2.cvtColor(lab_image, cv2.COLOR_Lab2BGR)

    # Show images if required
    if show:
        print("Displaying results. (Press any key to quit...)")
        cv2.imshow("Original image", bgr_image)
        cv2.imshow("Normalized (CLAHE) image", image_clahe)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Save the result
    cv2.imwrite(output_filename, image_clahe)


def main():
    parser = argparse.ArgumentParser(
        description="Normalize an image using CLAHE (Contrast Limited Adaptive Histogram Equalization)."
    )
    parser.add_argument(
        "-f", "--file", required=True, help="The filename of the image to process."
    )
    parser.add_argument("-o", "--output", help="The output filename.")
    parser.add_argument(
        "-e", "--extension", help="The file extension for the output image."
    )
    parser.add_argument(
        "-s",
        "--show",
        action="store_true",
        help="Show results in a graphical interface.",
    )

    args = parser.parse_args()

    inname = args.file
    outname = (
        args.output
        if args.output
        else replace_string(inname, ".tile.tissue.png", ".normalized.tile.tissue.png")
    )

    if args.extension:
        outname = remove_extension(outname) + "." + args.extension

    if not is_file_exist(inname):
        print(f"ERROR: File '{inname}' not found.")
        exit(1)

    if inname == outname:
        print("ERROR: Refusing to overwrite source file with output.")
        exit(1)

    print(f"Input: {inname}")
    print(f"Output: {outname}")

    normalize_slide_image(inname, outname, args.show)


if __name__ == "__main__":
    main()
