#!/bin/bash

process_column() {
	col=$1
	if [ $col -eq 1 ]; then
		magick $pic -crop "50%x100%+0+0" +repage $pic.$col
	elif [ $col -eq 2 ]; then
		magick $pic -crop "50%x100%+%[fx:0.5*w]+0" +repage $pic.$col
	fi
	tesseract $topts $pic.$col $pic.$col $tcfg >> $log 2>&1
	iconv -f utf-8 -t ascii//TRANSLIT $pic.$col.txt -o $pic.$col.txt.ascii
	cat $pic.$col.txt.ascii >> "$dir"/"$txt"
}

crop_percent=94

while getopts ":chf:l:p:" opt; do
	case ${opt} in
		c )
			crop_footer=1

			;;
		f )
			first_page=$OPTARG
			;;
		l )
			last_page=$OPTARG
			;;
		p )
			crop_percent=$OPTARG
			;;
		h )
			echo "Usage: $(basename $0) [-c] [-f N] [-l N] [-p N] <pdf_file> >&2"
			exit 1
			;;
	esac
done
shift "$((OPTIND -1))"

tmp_dir=$(mktemp -d -t pdf-XXXXXXXXXX --tmpdir=$XDG_RUNTIME_DIR)

pdf=$1
base=`basename "$pdf" .pdf`
dir="$base"
txt="$base".txt

log=`basename "$0" .sh`.log
rm -f $log
touch $log

rm -rf "$dir"
mkdir -p "$dir"

total_pages=`pdfinfo "$pdf" | grep Pages | sed 's/[^0-9]*//'`

if [ ! -z $first_page ]; then
	fp_opt="-f $first_page"
else
	first_page=1
fi

if [ ! -z $last_page ]; then
	lp_opt="-l $last_page"
else
	last_page=$total_pages
fi

# pdf first/last page selection
popts="$fp_opt $lp_opt"

echo "Processing pages $first_page-$last_page"

# Extract images
echo "Extract embedded images"
pdfimages -all $popts "$pdf" "$dir"/"$base" >> $log 2>&1

# Prep OCR images
echo "Prepare page images for OCR"
pdftoppm $popts "$pdf" $tmp_dir/pdf-image >> $log 2>&1

# disable tesseract form feed page separator
echo "page_separator " > $tmp_dir/tc.cfg
tcfg=$tmp_dir/tc.cfg

page=$first_page
for pi in $tmp_dir/pdf-image-*.ppm
do
	echo "Converting page $page"
	pic=$tmp_dir/`basename "$pi" .ppm`-crop.ppm

	# Crop footer
	if [ ! -z $crop_footer ]; then
		magick $pi -crop "100%x$crop_percent%" +repage $pic
	else
		cp $pi $pic
	fi

	process_column 1
	process_column 2

	((page+=1))
done

rm -rf $tmp_dir

echo Text in "$dir"/"$txt"
