#!/bin/bash

convert -flatten "$1[0]" flatten.webp
convert -background none -gravity center flatten.webp -resize 300x300 -extent 300x300 "`basename "$1" .pdf`.webp"   
rm -f flatten.webp
