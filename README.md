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

## Badooga's markdown to 5etools converter

An enhanced version of [Badooga's excellent markdown to 5etools json converter](https://github.com/badooga/Programs/tree/master/Dungeons%20and%20Dragons/5eTools) is included. The included version additionally supports
- Markdown inline image handling
- Optionally update image urls using a base url string (useful when previewing markdown with images locally and updating for homebrew repo)
- Setting unique area IDs automatically for header levels 1-4
- Optionally use a json _meta template to produce a turnkey file to upload to the Homebrew Manager.

## Workflow Example

### Convert PDF to ASCII7 text

Using the [Crypts of Kelemvor](https://media.wizards.com/2018/dnd/dragon/18/DRA18_CryptsKelemvor.pdf) adventure:
```
./pdf-two-column-to-text.sh -c DRA18_CryptsKelemvor.pdf
```
yields a `DRA18_CryptsKelemvor/` subdirectory with all extracted images and `DRA18_CryptsKelemvor.txt`

> The `-c` option is optional but recommended for clean text output. It removes all the footer text which would otherwise be intermingled into the OCRed column text. Depending on the size of the footer, it will be necessary to adjust the `-p` option appropriately to get all the column text depending on pdf layout.

Copy the text file to `Wizards of the Coast; Crypts of Kelemvor.md` and edit appropriately to meet the `markdown-to-5etools.py` markdown requirements and add all desired tags. I use [grip](https://github.com/joeyespo/grip) to preview the layout locally using this [patch for webp image support](https://github.com/joeyespo/grip/pull/327).

### Process markdown to 5etools json

Process overview:
1. Edit text to add markdown syntax
1. Optionally preview in `grip`
1. Run `./markdown-to-5etools.py ...`
1. Load in Homebrew Manager and review

#### Optionally create a 5etools _meta template

Create a 5etools _meta template json file following the included `CoK-meta-template.json` sample. This allows the generated 5etools json to be loaded without any manual post processing.

#### Cover thumbnail generation
A cover thumbnail for the meta template can be generated as follows:
```
$ ./pdf-to-5etools-thumbnail.sh DRA18_CryptsKelemvor.pdf
```
yields a `DRA18_CryptsKelemvor.webp` cover thumbnail image.

#### Simple markdown to 5etools json

Generate the 5etools json:
```
$ ./markdown-to-5etools.py --meta-template CoK-meta-template.json "Wizards of the Coast; Crypts of Kelemvor.md"
```
yields a `Wizards of the Coast; Crypts of Kelemvor.json` that is ready to load into the Homebrew Manager.

#### markdown to 5etools json with image url translation

In the case of using `grip` to preview markdown with images stored locally. e.g. images stored in `./_img/COK/` where the markdown references image urls as `[foo](_img/COK/foo.webp)`, it's helpful to have the urls updated to point at the homebrew repo. Generate the 5etools json with image urls updated:
```
$ ./markdown-to-5etools.py --base-image-url "https://raw.githubusercontent.com/TheGiddyLimit/homebrew/master/" --meta-template CoK-meta-template.json "Wizards of the Coast; Crypts of Kelemvor.md"
```
yields a `Wizards of the Coast; Crypts of Kelemvor.json` with:
- Image URLs updated for loading from the homebrew repo
- Ready to load into the **Homebrew Manager**.

#### markdown to 5etools json with area id truncation

If converting an adventure with keyed areas, the section headers may be extremely long (e.g. **Area 37B: This Is An Extremely Long Title For A Room In A Dungeon**). In the preceding example, it's convenient to truncate the unique area id to just `Area 37B` so that tagging areas are not unwieldy or require remembering the complete text of the section header. To address this a --area-pattern option is available which accepts a regex. This regex should match the adventure's pattern for keyed area section names. A common pattern in use is **Area N** where **N**  is one or more digits followed by an upper or lower case letter. A working regex for this common pattern is `^Area [0-9]+[a-zA-Z]?`. Generate the 5etools json with truncated area ids:
```
./markdown-to-5etools.py --area-pattern "Area [0-9]+[a-zA-Z]?" --base-image-url "https://raw.githubusercontent.com/TheGiddyLimit/homebrew/master/" --meta-template CoK-meta-template.json "Wizards of the Coast; Crypts of Kelemvor.md"
```
yields a `Wizards of the Coast; Crypts of Kelemvor.json` with:
- Image URLs updated for loading from the homebrew repo
- Area IDs truncated to just the area number (e.g. `Area 37B`) to work with a more minimal area tag (e.g. `{@area 37B|Area 37B}`)
- Ready to load into the **Homebrew Manager**.

### Cleanup

Creatures/items/etc need to be manually added to the meta template or final json.

## TODO

* Support setting command line options via a config file
