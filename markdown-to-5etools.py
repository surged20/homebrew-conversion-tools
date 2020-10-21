#!/usr/bin/env python3
# vim: set noexpandtab:

"""
Made by badooga. https://github.com/badooga/Programs/
Additional features by Surge. https://github.com/surge/5etools-conversion-tools

This script converts an adventure or book from markdown form to 5eTools. To use it, pass the md file as an argument in the cmd.

This script does not automatically input tags, or metadata, nor does it automatically add content like monsters and spells to 5eTools:
- Make sure the first line of your document is an h1 header (# Header Title)!
- For tags, add them to the markdown before using this script. Other than bold and italics tags, this script does not handle that sort of thing.
- For monsters, use CritterDB or Homebrew Builder with Text Converter to turn it into JSON, and include the monster in the adventure as normal.
- For images, use the standard markdown format below (creates standard image type, no gallery support).
- For tables, you will have to adjust the col-styles manually, if you feel that they need adjusting.
- If you're using this for homebrew, you'll have to do the metadata (_meta) yourself. There is now an option to pass a _meta template.
- This script also handles the table of contents for you, but you might want to double check it to make sure it's to your satisfaction.
- Area ids are generated for all headers. Duplicate section header names will have the area id be the section name + instance for the area id. e.g. "Treasure 3"

See the example md file in the linked repository (in the same folder as this script) for formatting guidelines. In particular, note the following:

Image:
- [Player Handout 1](https://i.imgur.com/fBjhiNG.png)


- BUG: Be sure to put two lines after an image or the parser may place it in the following heading

This list:
- ***Is not valid.*** Triple asterisks are reserved for inline headers.

This list:
- **Is valid.** Using double asterisks to bold the text conveys the same meaning and avoids any issues with this script.

----------------------------------

***This inline header and list combo.*** Is not valid.

- Note the line break above.
- It probably won't kill you to do this, but to receive the right output, see below.

***This inline header and list combo.*** Is valid.
- Putting the list here will nest things properly.
- For the record, that extra line break is the source of many headaches.

---------------------------------

##### This table

| Is not valid   | Note the above line break is not valid, and that the line with dashes (see below) is absent. |
| Entry 1        | Description 1       |

##### This table
| Is Valid | A version of line below is required |
|----------|--------------------------------------|
| Entry 1  | Description 1       |

Happy converting!
"""


import json, re
import argparse

area_ids = {}

def get_area_id(name):
	if args.area_pattern is None:
		area_name = name
	else:
		area = re.match(args.area_pattern, name)
		area_name = area.group(0) if area is not None else name
	if area_name in area_ids:
		area_ids[area_name] = area_ids.get(area_name) + 1
		area_id = area_name + ' ' + str(area_ids.get(area_name))
	else:
		area_ids[area_name] = 1
		area_id = area_name
	return area_id

parser = argparse.ArgumentParser()
parser.add_argument("markdown_file", help="Markdown file to be processed")
parser.add_argument("-a", "--area-pattern", help="Regex pattern to match/shorten area ids")
parser.add_argument("-b", "--base-image-url", help="Base image url to prepend to image urls")
parser.add_argument("-m", "--meta-template", help="5etools _meta json template file")
args = parser.parse_args()

# The next few lines collect the data from the file passed as an argument and convert it to a list of lines to be iterated through

with open(args.markdown_file, "r") as f:
	text = f.readlines()
	htext = [(x, i.replace("\n","")) for x, i in enumerate(text)]
	text = "\n" + "".join(text)

h1, h2, h3, h4 = [[i.replace("#"*h,"").strip() for x, i in htext if i.startswith("#"*h + " ")] for h in range(1,5)]
h3d = []

data = [{"type": "section", "name": i, "id": get_area_id(i), "entries":[]} for i in h1]
text = text.split("\n# ")[1:]

# Initializes flags for header nesting and its tracking

z = [0, 0, 0]
h1c, h2c, h3c, h4c = -1, *z

# Initializes flags for each type of special formatting; the "b" stands for "boolean", but the actual var is an integer so that I don't have to type a boolean every time every time; bh3_h2 is a special flag used when detecting h3 headers that don't have h2 parents

bInset, bInset2, bRead, bRead2, bImage, bInline1, bInline2, bList, bh3_h2, bListInset, bTable, bTable2, bTable3, bInlineList = [0] * 14

# Initializes structure used for each type of special formatting

image = {"type": "image", "href": { "type": "external", "url": ""}, "title": ""}
inset = {"type": "inset", "name": "", "entries": []}
insetReadAloud = {"type": "insetReadaloud", "entries": []}
inlineHeader = {"type": "entries", "name": "", "entries": []}
unorderedList = {"type": "list", "items": []}
table = {"type": "table", "colLabels": [], "colStyles": [], "rows": []}

# Function used to add various data to the output based on the appropriate nesting structure

def add(dtext):
	global h1c, h2c, h3c, h4c, bh3_h2, data
	if h4c > 0:
		if not bh3_h2:
			data[h1c]["entries"][-1]["entries"][-1]["entries"][-1]["entries"].append(dtext)
		else:
			data[h1c]["entries"][-1]["entries"][-1]["entries"].append(dtext)
	elif h3c > 0:
		if not bh3_h2:
			data[h1c]["entries"][-1]["entries"][-1]["entries"].append(dtext)
		else:
			data[h1c]["entries"][-1]["entries"].append(dtext)
	elif h2c > 0:
		data[h1c]["entries"][-1]["entries"].append(dtext)
	else:
		data[h1c]["entries"].append(dtext)

# Function used to create inlineHeaders while taking into account the nesting structure

def indent():
	global h1c, h2c, h3c, h4c
	def iter(n=1):
		global inlineHeader
		for _ in range(n): inlineHeader = {"type": "entries", "entries": [inlineHeader]}
	if h4c > 0: iter(bh3_h2)
	elif h3c > 0: iter(1 + bh3_h2)
	elif h2c > 0: iter(2)
	elif h1c > 0: iter(3)

for x, i in htext:
	try:
		# Resets a few things back to default + skips to the next line when it detects a blank line
		# As the first line is always going to be a h1 header and is already accounted for on line 65, it can be skipped
		if not x or i == "":
			if bImage:
				add(image)
				image = {"type": "image", "href": { "type": "external", "url": ""}, "title": ""}
				bImage = 0
			if bTable:
				add(table)
				table = {"type": "table", "colLabels": [], "colStyles": [], "rows": []}
				bTable = 0
			if bInset: bInset2 = 1
			if bRead: bRead2 = 1
			if not x: h1c += 1
			if bList:
				add(unorderedList)
				unorderedList = {"type": "list", "items": []}
				bList = 0
			elif bInline1:
				bInline1 = 0
				bInline2 = 1
			else: continue

		i = i.strip()
		ii = i.replace("#", "").strip()

		if not bImage and (i.startswith("!")):
			bImage = 1
			if args.base_image_url is None:
				base_url = ''
			else:
				base_url = args.base_image_url
			m = re.search("(?:!\[(.*?)\]\((.*?)\))", i)
			image["title"] = m.group(1)
			image["href"]["url"] = base_url+m.group(2)
			continue

		# Formatting for a table - bTable is switched when the table starts and ends, bTable2 is used when there is an optional caption, and bTable3 is used to format the text-align
		if not bTable and (i.startswith("#####") or i.startswith("|")):
			bTable = 1
			bTable3 = 1
			if i.startswith("#####"):
				bTable2 = 1
				table["caption"] = ii.strip()
				continue
			else:
				table["colLabels"] = [t.strip() for t in i.split("|") if t != ""]
				continue
		elif bTable2:
			bTable2 = 0
			table["colLabels"] = [t.strip() for t in i.split("|") if t != ""]
			continue
		elif bTable3:
			talign = [t for t in i.split("|") if t != ""]
			for k in talign:
				if (k[0], k[-1]) == (":", ":"):
					table["colStyles"].append("text-align-center")
				elif k[-1] == ":":
					table["colStyles"].append("text-align-right")
				else:
					table["colStyles"].append("text-align-left")
			bTable3 = 0
			continue

		elif i.startswith("|"):
			table["rows"].append([t.strip() for t in i.split("|") if t.strip() != ""])
			continue

		# insetReadAloud - must come before inset
		if bRead2:
			add(insetReadAloud)
			insetReadAloud = {"type": "insetReadaloud", "entries": []}
			bRead, bRead2 = 0, 0
		if i.startswith(">>"):
			bRead = 1
			insetReadAloud["entries"].append(i.replace(">>", "").strip())
			continue
		elif bRead:
			add(insetReadAloud)
			insetReadAloud = {"type": "insetReadaloud", "entries": []}
			bRead = 0

		# inset - both regular insets and lists within insets (line 181); must come before inlineHeader and unorderedList
		if bInset2:
			add(inset)
			inset = {"type": "inset", "name": "", "entries": []}
			bInset, bInset2 = 0, 0
		if i.startswith(">") or i.startswith(">-"):
			if not bInset:
				bInset = 1
				inset["name"] = i.replace("#####", "").replace(">", "").strip()
			else:
				if i.startswith(">-"):
					if not bListInset:
						inset["entries"].append({"type": "list", "items": [i.replace(">-", "").strip()]})
						li = len(inset["entries"]) - 1
						bListInset = 1
					else:
						inset["entries"][li]["items"].append(i.replace(">-", "").strip())
				else:
					bListInset = 0
					inset["entries"].append(i.replace(">", "").strip())
			continue
		elif bInset:
			add(inset)
			inset = {"type": "inset", "name": "", "entries": []}
			bInset = 0

		# inlineHeader - bInline2 is used alongside bInline1 to continue adding paragraphs until a blank line is encountered
		if i.startswith("***"):
			bInline1 = 1
			i = i.replace("***", "", 1)
			k = i.index("***") - 1
			inlineHeader["name"] = i[:k]
			inlineHeader["entries"].append(i[k+5:])
			continue

		if bInline1:
			if i.startswith("-"):
				bInlineList = 1
				unorderedList["items"].append(i[1:].strip())
				continue
			else:
				inlineHeader["entries"].append(i)
			continue

		elif bInline2:
			if bInlineList:
				inlineHeader["entries"].append(unorderedList)
				unorderedList = {"type": "list", "items": []}
				bInlineList = False
			indent(); add(inlineHeader)
			bInline1, bInline2 = 0, 0
			inlineHeader = {"type": "entries", "name": "", "entries": []}
			continue

		# unorderedList - other half is at top of loops
		if i.startswith("-"):
			bList = 1
			unorderedList["items"].append(i[1:].strip())
			continue

		# Headers - detect if a line has a header in it, and then adjusts the nesting accordingly

		if i.replace("##", "").strip() in h2:
			h2c += 1
			data[h1c]["entries"].append({"type": "section", "name": ii, "id": get_area_id(ii), "entries":[]})
			h3c, h4c = z[1:]
			bh3_h2 = 0

		elif i.replace("###", "").strip() in h3:
			h3c += 1
			h4c = 0
			if not h2c:
				bh3_h2 = 1
				h3d.append(ii)
				data[h1c]["entries"].append({"type": "entries", "name": ii, "id": get_area_id(ii), "entries": []})
			else:
				data[h1c]["entries"][-1]["entries"].append({"type": "entries", "name": ii, "id": get_area_id(ii), "entries": []})
		elif i.replace("####", "").strip() in h4:
			if not h2c:
				data[h1c]["entries"][-1]["entries"].append({"type": "entries", "name": ii, "id": get_area_id(ii), "entries": []})
			else:
				data[h1c]["entries"][-1]["entries"][-1]["entries"].append({"type": "entries", "name": ii, "entries": []})
			h4c += 1

		elif ii in h1:
			h1c += 1
			h2c, h3c, h4c = z

		# if it isn't a header and the line is a normal line, it gets add()-ed here; extra fail-safe against empty lines
		elif i != "": add(i)
	except Exception as e:
		print(e)
		print("Problem found on or related to markdown line", x)
		break

# Reparses the headers in (x, i) format where x is the htext index and i is the actual header
h1, h2, h3, h4 = [[(x, i.replace("#"*h,"").strip()) for x, i in htext if i.startswith("#"*h + " ")] for h in range(1,5)]

# Creates a list of headers in order for the table of contents
hlist = sorted(h1 + h2 + h3, key=lambda value: value[0])
headers = []

# Adds h1 and h2 headers to the table of contents; if it encounters any h3 headers without an h2 parent (see line 243), those are added too
counter = -1
for x, i in hlist:
	if (x, i) in h1:
		counter += 1
		headers.append({"name": i, "headers": []})
	elif (x, i) in h2 or i in h3d:
		headers[counter]["headers"].append(i)

# Nests all of this data into the proper 5eTools format, with blank strings for you to fill in; if you are making a book, change "adventure" to "book"
default_data = {
	"_meta": {
		"sources": [
			{
				"json": "",
				"abbreviation": "",
				"full": "",
				"authors": [
					""
				],
				"convertedBy": [
					""
				],
				"version": "1.0.0",
				"url": "https://github.com/TheGiddyLimit/homebrew",
				"targetSchema": "1.0.0"
			}
		]
	},
	"adventure": [
		{
			"name": "",
			"id": "",
			"source": "",
			"contents": headers,
			"level": {
				"start": 1,
				"end": 1
			},
			"published": "",
			"storyline": ""
		}
	],
	"adventureData": [
		{
			"id": "",
			"source": "",
			"data": data
		}
	]
}

if args.meta_template is None:
	adata = default_data
else:
	with open(args.meta_template, "r") as template:
		adata = json.load(template)
		adata["adventure"][0]["contents"] = list(headers)
		adata["adventureData"][0]["data"] = list(data)

# Turns the text into one big string for the purpose of bold and italics tags
adata = repr(adata)

b = ["{@b ", "}"]
v = 0
while "**" in adata:
	adata = adata.replace("**", b[v], 1)
	v = not v

b[0] = "{@i "
v = 0
while "*" in adata:
	adata = adata.replace("*", b[v], 1)
	v = not v

# Turns the string back into a dict
adata = eval("{}".format(adata))

# Writes your new file to a 5eTools JSON file
with open("{}.json".format(args.markdown_file[:-3]), "w") as f:
	json.dump(adata, f, indent="\t")
