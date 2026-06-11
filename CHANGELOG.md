# Changelog

All notable changes to slideToolKit are documented here.

---

## Script inventory

| Script | Version | Description |
|--------|---------|-------------|
| `slideRename.py` | v1.3.1 | Displays the label/macro thumbnail of a whole-slide image, attempts automatic barcode decoding (Data Matrix via pylibdmtx, other formats via pyzbar), and renames the file accordingly or falls back to manual input. Also provides `--batch-fix` mode to normalise scanner-generated NDPI filenames (e.g. `AE 4594  HE - 2026-02-20 08.53.54.ndpi`) to the canonical `AENNNN.STAIN.ndpi` format without opening slides. |
| `slideRename` | v1.2 | Legacy Bash script for batch-renaming whole-slide images using barcode readers (`dmtxread`, `zbarimg`) and ImageMagick for preview; requires several system-level dependencies and is superseded by `slideRename.py`. |
| `slideRename.SRpolarized.py` | v1.0.11 | Renames SR-polarised whole-slide `.tif` files from T-number-based scanner names to the canonical `AENNNN.T_NUMBER.SR_POLARIZED.tif` format using a CSV or SPSS lookup table mapping T-numbers to study numbers. |
| `slideDupIdentify.py` | v1.1.0 | Identifies and organises duplicate whole-slide image files within a study by study type and stain name, prioritising files according to configurable criteria and logging all decisions. |
| `slideEntropySegmentation.py` | v1.0.0 | Wraps the EntropyMasker tool to generate tissue masks for whole-slide images using entropy-based segmentation, producing mask files alongside the original images. |
| `slideExtract.py` | v1.1.0 | Extracts thumbnail and macro images from whole-slide image files (`.tif`, `.ndpi`, etc.) at a specified magnification level using OpenSlide. |
| `slideExtractTiles.py` | v1.0.0 | Extracts fixed-size tiles from a whole-slide image guided by a tissue mask, outputs individual tile files, and produces an overview image showing which regions were tiled. |
| `slideInfo.py` | v1.1.0 | Prints technical metadata (dimensions, magnification, format, associated images) for one or more whole-slide image files using OpenSlide. |
| `slideLookup.py` | v1.1.0 | Checks for the existence of a given list of samples (by study number and stain) across one or more WSI directories, optionally copying found files to a target location and logging all results. |
| `slideMacro.py` | v1.1.0 | Extracts and optionally displays the macro/label image embedded in whole-slide image files, saving it as a standalone image file. |
| `slideMoveNewWSI.py` | v1.1.1 | Moves newly scanned `.ndpi` files from an incoming folder to a destination directory for a given study type and stain, checking for pre-existing study numbers and computing file checksums to avoid duplicates. |
| `slideNormalize.py` | — | Normalises whole-slide image tiles using CLAHE (Contrast Limited Adaptive Histogram Equalization) in LAB colour space to reduce staining variability across batches. |
| `slideThumb.py` | v1.1.1 | Extracts and saves thumbnail images from whole-slide image files at a configurable zoom level, with optional display, for rapid visual quality control. |
| `slideToolKitTest.py` | — | Environment smoke-test that verifies all required Python packages and system dependencies for slideToolKit are correctly installed. |

---

## [slideRename.py v1.3.1] — 2026-06-11

### Fixed
- `--batch-fix`: files with no stain name in the filename (e.g. `AE 4985 - 2025-08-04 11.45.08.ndpi`, scanner output without a stain label) are now correctly flagged as `[SKIP]` instead of being renamed to `AENNNN.-.ndpi`.
- `--batch-fix`: intra-directory target collisions (two or more source files resolving to the same canonical name) are now detected in a pre-flight pass and reported as `[WARN]` in both dry-run and apply modes, rather than silently overwriting or erroring only on the second file.

## [slideRename.py v1.3.0] — 2026-06-11

### Added
- `--batch-fix` mode: batch-normalises scanner-generated NDPI filenames in one or more directories (passed via `-i/--input`) to the canonical `AENNNN.STAIN.ndpi` format (or `AENNNN.N.STAIN.ndpi` when a section number is present) without opening any slide file.
  - Stain names are normalised to canonical forms (e.g. `glyc.c` / `Glyc. C` → `Glyc.C`; `CD 34` → `CD34`; `a-SMA`, `HE`, `SR`, `EvG` etc.).
  - Embedded date/time stamps (`- YYYY-MM-DD HH.MM.SS`) are stripped.
  - Files already in canonical form are silently counted as "already correct".
  - Dry-run by default; combine with `--force` to overwrite existing destinations.
- Bumped copyright year to 2026.

### Removed
- `slideNDPIfix.py` — standalone script superseded by `--batch-fix` in `slideRename.py`.
