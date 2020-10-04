# 5etools conversion tools

A set of tools that simplifies conversion of PDF format adventures into 5etools json schema for homebrew.

## Dependencies

* Imagemagick 7
   * Debian/Ubuntu use https://github.com/SoftCreatR/imei to install
   * Fedora has it
* poppler-utils
   * `sudo apt install poppler-utils`
* teseract
   * `sudo apt install tesseract-ocr`

## pdf-two-column-to-text.sh

`pdf-two-column-to-text.sh` splits a two column pdf into ordered single column sheets and OCRs the entire document. Text is converted to ASCII7.

`pdf-two-column-to-text.sh` supports these options:
- `-c`: Crop footer from pdf (default top 94% of page is preserved)
- `-f`: First page to parse
- `-l`: Last page to parse
- `-p`: Percentage of of page to crop (top N% of page is preserved)

## pdf-to-5etools-thumbnail.sh

Creates a 5etools cover thumbnail in webp format.

## Badooga's markdown_to_5etools.py

An enhanced version of [Badooga's excellent markdown to 5etools json converter](https://github.com/badooga/Programs/tree/master/Dungeons%20and%20Dragons/5eTools) is included. The included version additionally supports
- Markdown image handling
- Setting 5etools area IDs (same as the header name) automatically for header levels 2-4
- Use a 5etools json meta template to produce a turnkey file to upload to the Homebrew Manager.

## Workflow Example

Using the [Crypts of Kelemvor](https://media.wizards.com/2018/dnd/dragon/18/DRA18_CryptsKelemvor.pdf) adventure:
```
./pdf-two-column-to-text.sh -c DRA18_CryptsKelemvor.pdf
```
yields a `DRA18_CryptsKelemvor/` subdirectory with all extracted images and `DRA18_CryptsKelemvor.txt`

> The `-c` option is optional but recommended for clean text output. It removes all the footer text which would otherwise be intermingled into the OCRed column text. Depending on the size of the footer, it will be necessary to adjust the `-p` option appropriately to get all the column text depending on pdf layout.

Copy the text file to `DRA18_CryptsKelemvor.md` and edit appropriately to meet the `markdown_to_5etools.py` markdown requirements and add all desired tags. I use `grip` to preview basic sections and image placement locally (although it can't handle webp images).

Create a 5etools meta template json file following the included `CoK-meta-template.json` sample. This allows the generated 5etools json to be loaded without any manual post processing so it's possible to iterate by:
1. Edit markdown
1. Run `./markdown_to_5etools.py ...`
1. Load in Homebrew Manager and review

A cover thumbnail for the meta template can be generated as follows:
```
$ ./pdf-to-5etools-thumbnail.sh DRA18_CryptsKelemvor.pdf
```
yields a `DRA18_CryptsKelemvor.webp` cover thumbnail image.

Generate the 5etools json:
```
$ ./markdown_to_5etools.py --area-header 2 --meta-template CoK-meta-template.json "Wizards of the Coast; Crypts of Kelemvor.md"
```
yields a `Wizards of the Coast; Crypts of Kelemvor.json` that is ready to load into the Homebrew Manager.

> The `--area-header 2` option is used because the CoK markdown has its areas to be referenced in header level 2. Header level 3 has a number of **Treasure** sections with duplicate names. By limiting assignment of area ids to a maximum header level of 2, we ensure that we don't break the 5etools requirement of having unique area ids within a document.
> It will be necessary to adjust image links in the case of images stored in the homebrew repo.
> Creatures/items/etc need to be manually added to the final json.
