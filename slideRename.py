#!/usr/bin/env python3
#
# script to display a whole-slide image file and (auto- or manually) rename the file (*.TIF, *.NDPI, etc.)
#
# Ref: https://github.com/choosehappy/Snippets/blob/master/extract_macro_level_from_wsi_image_openslide_cli.py
#

# Only import heavy libraries after determining they are needed
import argparse
import os
import re
from sys import exit

# Prefer strict top-level imports, but keep them optional so the script can still run without barcode features.
try:
    from pylibdmtx.pylibdmtx import decode as DMTX_DECODE  # Data Matrix
except Exception:
    DMTX_DECODE = None

try:
    from pyzbar.pyzbar import decode as ZBAR_DECODE        # QR/Code128/EAN/…
except Exception:
    ZBAR_DECODE = None

# Version information
# Change log:
# * v1.2.0 (2025-08-25): Add --preview {cv2,none}, --resize WxH, --dry-run, --to-upper/--to-lower, --rotate {0,90,180,270}. Add automatic barcode decoding (Data Matrix via pylibdmtx, other barcodes via pyzbar).
# * v1.1.0 (2024-09-26): Overhaul to make the script more modular, define functions, and easier to read.
# * v1.0.0 (2023-12-15): Initial version.
VERSION_NAME = 'slideRename'
VERSION = '1.2.0'
VERSION_DATE = '2025-08-25'
COPYRIGHT = 'Copyright 1979-2025. Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com | https://vanderlaanand.science.'
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

# ----------------------------------------
# UI
# ----------------------------------------
def print_header():
    print(f"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"                             {VERSION_NAME}: display and (auto-)rename whole-slide images ")
    print(f"\n* Version          : {VERSION}")
    print(f"* Last update      : {VERSION_DATE}")
    print(f"* Written by       : Sander W. van der Laan | s.w.vanderlaan [at] gmail [dot] com")
    print(f"* Inspired by      : choosehappy | https://github.com/choosehappy\n")
    print(f"* Description      : Shows a label/macro thumbnail, tries to read a barcode, and renames the file accordingly.")
    print(f"                     Falls back to manual input. Collision-safe with --force, and supports dry runs.\n")
    print(f"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")

def print_footer():
    print(f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"+ The MIT License (MIT)                                                                                           +")
    print(f"+ {COPYRIGHT}                          +")
    print(f"+ Reference: http://opensource.org.                                                                               +")
    print(f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

# ----------------------------------------
# Args
# ----------------------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(
        prog=VERSION_NAME,
        description=f'''
+ {VERSION_NAME} v{VERSION} +

Display thumbnails from whole-slide images, attempt barcode decoding for auto-rename, or prompt for manual name.''',
        usage=('python3 slideRename.py -i/--input '
               '[--outdir DIR] [--prefix P] [--suffix S] [--case {none,lower,upper}] '
               '[--to-upper|--to-lower] [--barcode {auto,dmtx,zbar,off}] '
               '[--preview {cv2,none}] [--resize WxH] [--rotate {0,90,180,270}] '
               '[-f/--force] [--dry-run] [-v/--verbose]'),
        epilog=f'''+ {VERSION_NAME} v{VERSION}. {COPYRIGHT} +\nThe MIT License (MIT)\nReference: http://opensource.org''',
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Core I/O
    parser.add_argument('-o', '--outdir', help="Output dir, default is the input image(s) directory. Optional.", default="<<SAME>>", type=str)
    parser.add_argument('--prefix', help="Filename prefix to prepend. Optional.", default="", type=str)
    parser.add_argument('-s', '--suffix', help="Suffix to append to end of file, no suffix will be added by default. Optional.", default="", type=str)
    parser.add_argument('--case', help="Output filename casing. Optional.", choices=['none','lower','upper'], default='none')
    parser.add_argument('--to-upper', help="Force UPPERCASE output filename (alias of --case upper).", action='store_true')
    parser.add_argument('--to-lower', help="Force lowercase output filename (alias of --case lower).", action='store_true')

    # Barcode / preview / speed
    parser.add_argument('--barcode', help="Attempt automatic barcode read from label/macro image. Optional.",
                        choices=['auto','dmtx','zbar','off'], default='auto')
    parser.add_argument('--preview', help="Preview window type. Optional.", choices=['cv2','none'], default='cv2')
    parser.add_argument('--resize', help="Resize preview/decoding image to WxH, e.g., 800x600. Optional.", default=None, type=str)
    parser.add_argument('--rotate', help="Rotate label/macro image before preview/decoding. Optional.", choices=[0,90,180,270], type=int, default=90)

    # Behavior
    parser.add_argument('--dry-run', help="Print intended renames, do not move files. Optional.", action='store_true')
    parser.add_argument('-f', '--force', help="Force output even if it exists. Optional.", default=False, action="store_true")
    parser.add_argument('-v', '--verbose', help="Verbose output. Optional.", default=False, action="store_true")
    parser.add_argument('-V', '--version', action='version', version=VERSION_NAME + ' v' + VERSION + ' (' +  VERSION_DATE + ') | ' + COPYRIGHT)

    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-i', '--input', help="An input image (or glob/dir containing image files). Required.", nargs="*")

    args = parser.parse_args()

    # Map alias flags to case; last one wins if both are present on CLI
    if args.to_upper:
        args.case = 'upper'
    if args.to_lower:
        args.case = 'lower'

    return args

# ----------------------------------------
# Helpers
# ----------------------------------------
def validate_input(args):
    import glob
    if not args.input:
        print("\nOh, computer says no! You must supply correct arguments when running *** slideRename ***!")
        print("Note that -i/--input is required. Try: --input IMG012.ndpi (or *.TIF or /path_to/images/*.ndpi).\n")
        exit()

    # Allow: multiple explicit paths OR one glob pattern
    if len(args.input) > 1:
        files = []
        for item in args.input:
            if os.path.isdir(item):
                for root, _dirs, fnames in os.walk(item):
                    for f in fnames:
                        files.append(os.path.join(root, f))
            else:
                files.extend(glob.glob(item))
        return sorted(set(files))
    else:
        item = args.input[0]
        if os.path.isdir(item):
            files = []
            for root, _dirs, fnames in os.walk(item):
                for f in fnames:
                    files.append(os.path.join(root, f))
            return sorted(set(files))
        else:
            return sorted(set(glob.glob(item)))

def sanitize_name(name: str) -> str:
    """Allow only safe filename chars; collapse whitespace and strip."""
    name = name.strip()
    name = re.sub(r'[^A-Za-z0-9._-]+', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('._')
    return name or "UNNAMED"

def apply_affixes_and_case(base: str, prefix: str, suffix: str, case: str) -> str:
    out = f"{prefix}{base}{suffix}"
    if case == 'lower':
        out = out.lower()
    elif case == 'upper':
        out = out.upper()
    return out

def parse_resize(s: str):
    """Parse WxH like '1024x512' -> (1024, 512). Returns None if invalid/not set."""
    if not s:
        return None
    m = re.fullmatch(r'(\d+)x(\d+)', s.strip().lower())
    if not m:
        raise ValueError(f"--resize must be WxH (e.g., 1024x512); got: {s}")
    w, h = int(m.group(1)), int(m.group(2))
    if w <= 0 or h <= 0:
        raise ValueError(f"--resize dimensions must be > 0; got: {s}")
    return (w, h)

# ----------------------------------------
# Barcode decoding
# ----------------------------------------
def try_imports():
    """
    Return the (possibly None) decoder callables imported at module load.
    Keeps behavior consistent whether dependencies are present or not.
    """
    return DMTX_DECODE, ZBAR_DECODE

def decode_datamatrix(img_rgb, dmtx_decode):
    """Return first Data Matrix string or None."""
    if dmtx_decode is None:
        return None
    import cv2
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    variants = [gray,
                cv2.GaussianBlur(gray, (3,3), 0),
                cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 31, 5)]
    for v in variants:
        for scale in (1.0, 1.5, 2.0):
            if scale != 1.0:
                v2 = cv2.resize(v, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            else:
                v2 = v
            res = dmtx_decode(v2)
            for r in res or []:
                if r and getattr(r, "data", None):
                    txt = r.data.decode(errors='ignore').strip()
                    if txt:
                        return txt
    return None

def decode_zbar(img_rgb, zbar_decode):
    """Return first non-empty string from pyzbar or None."""
    if zbar_decode is None:
        return None
    import cv2
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    res = zbar_decode(gray)
    for r in res or []:
        data = getattr(r, "data", b"")
        txt = data.decode(errors='ignore').strip()
        if txt:
            return txt
    return None

def decode_barcode_from_macro(img_rgb, method='auto', verbose=False):
    """
    Try reading barcode from the (already rotated/resized) macro/label image.
    method: 'auto'|'dmtx'|'zbar'
    Also tries extra rotations (0,+90,+180,+270) relative to the provided orientation.
    """
    dm_decode, zb_decode = try_imports()
    import cv2

    def try_all(img):
        if method == 'dmtx':
            order = ['dmtx']
        elif method == 'zbar':
            order = ['zbar']
        else:
            order = ['dmtx', 'zbar']  # auto: DM first, then others
        for m in order:
            out = decode_datamatrix(img, dm_decode) if m == 'dmtx' else decode_zbar(img, zb_decode)
            if verbose:
                print(f"[barcode] {m} => {out}")
            if out:
                return out
        return None

    rotations = [0, 90, 180, 270]
    for angle in rotations:
        if angle == 0:
            img2 = img_rgb
        elif angle == 90:
            img2 = cv2.rotate(img_rgb, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            img2 = cv2.rotate(img_rgb, cv2.ROTATE_180)
        else:
            img2 = cv2.rotate(img_rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)
        out = try_all(img2)
        if out:
            return out
    return None

# ----------------------------------------
# Core
# ----------------------------------------
def process_images(files, args):
    import numpy as np
    import openslide
    import cv2

    resize_wh = parse_resize(args.resize) if args.resize else None

    for fname in files:
        fname_base, fname_base_ext = os.path.splitext(os.path.basename(fname))

        outdir = args.outdir if args.outdir != "<<SAME>>" else os.path.dirname(os.path.realpath(fname))
        os.makedirs(outdir, exist_ok=True)
        print(f"Output directory set to [{outdir}].")

        # Open slide & macro/label
        try:
            fimage = openslide.OpenSlide(fname)
        except Exception as e:
            print(f"ERROR: Cannot open slide [{fname}]: {e}")
            continue

        assoc = fimage.associated_images
        macro_key = "label" if "label" in assoc else ("macro" if "macro" in assoc else (list(assoc.keys())[0] if assoc else None))

        if macro_key is None:
            print(f"WARNING: No associated label/macro image found in [{fname}]. Will skip preview and barcode; manual only.")
            img_rgb = None
        else:
            img_rgb = np.asarray(assoc[macro_key])[:, :, 0:3]

        # Base rotation (user-set) and optional resize for speed
        if img_rgb is not None:
            if args.rotate in (0,90,180,270):
                import cv2
                if args.rotate == 90:
                    img_rgb = cv2.rotate(img_rgb, cv2.ROTATE_90_CLOCKWISE)
                elif args.rotate == 180:
                    img_rgb = cv2.rotate(img_rgb, cv2.ROTATE_180)
                elif args.rotate == 270:
                    img_rgb = cv2.rotate(img_rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)
                # 0 => no change

            if resize_wh:
                import cv2
                # cv2 expects (width,height) as (cols, rows)
                img_rgb = cv2.resize(img_rgb, resize_wh, interpolation=cv2.INTER_AREA)

        # Preview
        if args.preview == 'cv2' and img_rgb is not None:
            if args.verbose:
                print_image_info(img_rgb)
            cv2.imshow('slidePreview', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
            # small wait to ensure window paints; not blocking on key
            cv2.waitKey(1)
        else:
            if args.verbose:
                print("Preview disabled (--preview none) or no label/macro image available.")

        # --- Barcode attempt ---
        auto_name = None
        if args.barcode != 'off' and img_rgb is not None:
            auto_name = decode_barcode_from_macro(
                img_rgb,
                method=args.barcode,
                verbose=args.verbose
            )
            if auto_name:
                print(f"[barcode] Raw decode: {auto_name}")
                auto_name = sanitize_name(auto_name)
                auto_name = apply_affixes_and_case(auto_name, args.prefix, args.suffix, args.case)
                print(f"[barcode] Using sanitized name: {auto_name}")
            else:
                print("[barcode] No barcode detected (will ask for manual name).")

        # Fallback manual name
        if not auto_name:
            new_base = get_new_filename(fname_base, args.dry_run)
            new_base = sanitize_name(new_base)
            auto_name = apply_affixes_and_case(new_base, args.prefix, args.suffix, args.case)

        # Plan rename
        old_path = os.path.join(outdir, f"{fname_base}{fname_base_ext}")
        new_path = os.path.join(outdir, f"{auto_name}{fname_base_ext}")

        if args.dry_run:
            action = "WOULD RENAME"
            exists_note = " (exists!)" if os.path.exists(new_path) else ""
            print(f"[dry-run] {action}: [{old_path}] -> [{new_path}]{exists_note}")
        else:
            # Perform rename, collision-aware
            if not args.force and os.path.exists(new_path):
                print(f"Skipping {new_path}, output file exists and --force is not set.")
            else:
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed [{old_path}] to [{new_path}].")
                except Exception as e:
                    print(f"ERROR: Failed to rename [{old_path}] -> [{new_path}]: {e}")

        # Cleanup preview window (if any)
        if args.preview == 'cv2':
            cv2.destroyAllWindows()
            cv2.waitKey(1)

def print_image_info(img):
    print('* Image dimensions (height x width x channels):', img.shape)
    img_size_kb = img.size / 1024
    print(f'* Image size (elements, not disk): {img_size_kb:,.2f} KB-equivalent')

def get_new_filename(old_fname, dry_run=False):
    suffix = " (dry-run: just planning)" if dry_run else ""
    new_fname = input(f"Enter new name for [{old_fname}]{suffix}: ")
    print(f"You entered: {new_fname}")
    return new_fname

# ----------------------------------------
# Main
# ----------------------------------------
if __name__ == "__main__":
    args = parse_arguments()
    print_header()
    files = validate_input(args)
    process_images(files, args)
    print_footer()