#!/bin/bash
#
# It is good practice to properly name and annotate your script for future reference for
# yourself and others. Trust me, you'll forget why and how you made this!!!

### Creating display functions
### Setting colouring
NONE='\033[00m'
BOLD='\033[1m'
ITALIC='\033[3m'
OPAQUE='\033[2m'
FLASHING='\033[5m'
UNDERLINE='\033[4m'

RED='\033[01;31m'
GREEN='\033[01;32m'
YELLOW='\033[01;33m'
PURPLE='\033[01;35m'
CYAN='\033[01;36m'
WHITE='\033[01;37m'
### Regarding changing the 'type' of the things printed with 'echo'
### Refer to: 
### - http://askubuntu.com/questions/528928/how-to-do-underline-bold-italic-strikethrough-color-background-and-size-i
### - http://misc.flogisoft.com/bash/tip_colors_and_formatting
### - http://unix.stackexchange.com/questions/37260/change-font-in-echo-command

### echo -e "\033[1mbold\033[0m"
### echo -e "\033[3mitalic\033[0m" ### THIS DOESN'T WORK ON MAC!
### echo -e "\033[4munderline\033[0m"
### echo -e "\033[9mstrikethrough\033[0m"
### echo -e "\033[31mHello World\033[0m"
### echo -e "\x1B[31mHello World\033[0m"

function echobold { #'echobold' is the function name
    echo -e "${BOLD}${1}${NONE}" # this is whatever the function needs to execute, note ${1} is the text for echo
}
function echoitalic { 
    echo -e "${ITALIC}${1}${NONE}" 
}
function echocyan { 
    echo -e "${CYAN}${1}${NONE}" 
}

function echonooption { 
    echo -e "${OPAQUE}${RED}${1}${NONE}"
}

# errors
function echoerrorflash { 
    echo -e "${RED}${BOLD}${FLASHING}${1}${NONE}" 
}
function echoerror { 
    echo -e "${RED}${1}${NONE}"
}

# errors no option
function echoerrornooption { 
    echo -e "${YELLOW}${1}${NONE}"
}
function echoerrorflashnooption { 
    echo -e "${YELLOW}${BOLD}${FLASHING}${1}${NONE}"
}

### MESSAGE FUNCTIONS
script_copyright_message() {
	echo ""
	THISYEAR=$(date +'%Y')
	echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	echo "+ The MIT License (MIT)                                                                                 +"
	echo "+ Copyright (c) 2016-${THISYEAR} Sander W. van der Laan                                                        +"
	echo "+                                                                                                       +"
	echo "+ Permission is hereby granted, free of charge, to any person obtaining a copy of this software and     +"
	echo "+ associated documentation files (the \"Software\"), to deal in the Software without restriction,         +"
	echo "+ including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, +"
	echo "+ and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, +"
	echo "+ subject to the following conditions:                                                                  +"
	echo "+                                                                                                       +"
	echo "+ The above copyright notice and this permission notice shall be included in all copies or substantial  +"
	echo "+ portions of the Software.                                                                             +"
	echo "+                                                                                                       +"
	echo "+ THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT     +"
	echo "+ NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND                +"
	echo "+ NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES  +"
	echo "+ OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN   +"
	echo "+ CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                            +"
	echo "+                                                                                                       +"
	echo "+ Reference: http://opensource.org.                                                                     +"
	echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
}
script_arguments_error() {
	echoerror "$1" # ERROR MESSAGE
	echoerror "- Argument #1  -- name of the stain as it appears in the filenames, e.g. FIBRIN."
	echoerror "- Argument #2  -- study type of the analysis, e.g. AE or AAA."
	echoerror "- Argument #3  -- image file type, e.g. TIF, NDPI."
	echoerror "- Argument #4  -- the filename containin, e.g. Image.csv.gz, the script will automatically append STAIN, e.g. STAIN_Image.csv.gz"
	echoerror ""
	echoerror "An example command would be: slideAppend [arg1: STAIN] [arg2: STUDYTYPE ] [arg3: IMAGETYPE ] [arg4: Output_Image.csv.gz] "
	echoerror "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  	# The wrong arguments are passed, so we'll exit the script now!
  	exit 1
}

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echobold "                              slideAppend"
echo ""
echoitalic "* Written by  : Tim G.M. van de Kerkhof; Sander W. van der Laan"
echoitalic "* E-mail      : s.w.vanderlaan-2@umcutrecht.nl"
echoitalic "* Last update : 2023-02-18"
echoitalic "* Version     : v1.0.7"
echo ""
echoitalic "* Description : This script will collect results and append these in a CSV."
echoitalic "                Input CSV-files are expected to be gzipped."
echo ""
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "Today's: $(date)"
TODAY=$(date +"%Y%m%d") # set Today

echo ""
### REQUIRED | GENERALS	
STAIN="$1" # Depends on arg1
STUDYTYPE="$2"
IMAGETYPE="$3"
RESULTSFILENAME="$4"

if [[ $# -lt 4 ]]; then 
	echoerrorflash "Oh, computer says no! Number of arguments found $#."
	script_arguments_error "You must supply correct (number of) arguments when running *** slideAppend ***!"

else

	OutFileName="${TODAY}.${STAIN}.${STUDYTYPE}.${IMAGETYPE}.ImageExp.csv" # Fix the output name
	
	echo ""
	echoitalic "Creating a new log."
	# make a new append.log
	echo "STUDYNUMBER FILENAME" > "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".append.log

	echo ""
	echoitalic "Creating folders to collect all masks and tile-crossed images."
	mkdir -v "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".MasksTileCrossedImages
	MASKDIR="${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".MasksTileCrossedImages
	mkdir -v $MASKDIR/_issues
	mkdir -v $MASKDIR/_masks
	mkdir -v $MASKDIR/_okay
	mkdir -v $MASKDIR/_fix
	mkdir -v $MASKDIR/_multiplaque
	mkdir -v $MASKDIR/_remove
	
	MASKISSUEDIR="$MASKDIR/_issues"
	MASKMASKDIR="$MASKDIR/_masks"
	
	# make tileselection file
	echo "Tile Width Height Keep Row Column" > $MASKDIR/tile_selection.txt
		
	i=0 # Reset a counter
	echo ""
	echoitalic "Collecting data for:"
	for filename in "$STUDYTYPE"*/cp_output/"${STAIN}"_"${RESULTSFILENAME}"; do 
		if [ "$filename"  != "$OutFileName" ] ; then # Avoid recursion
			# get the sample number from the filename
			STUDYNUMBER=${filename%%\/*} # Remove everything from the first slash >> https://unix.stackexchange.com/questions/268134/extract-a-specific-part-of-the-path-of-a-file
			
			cols=$(zcat "$filename" | awk -F, '{ print NF }' | uniq | wc -l)
			if [[ "$cols" -gt 1 ]]; then
				STUDYNUMBER=${filename%%\/*} # Remove everything from the first slash >> https://unix.stackexchange.com/questions/268134/extract-a-specific-part-of-the-path-of-a-file
				echo "**ERROR** no new line for end-of-file for [ $STUDYNUMBER ]."
				echo "$STUDYNUMBER $filename" >> "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".append.log
				cp -v $STUDYNUMBER/mask_${STUDYNUMBER}.png $MASKISSUEDIR/mask_${STUDYNUMBER}.png
				cp -v $STUDYNUMBER/tilecrossed_${STUDYNUMBER}.png $MASKISSUEDIR/tilecrossed_${STUDYNUMBER}.png
				cp -v $STUDYNUMBER/tile_selection.tsv.gz $MASKISSUEDIR/tile_selection_${STUDYNUMBER}.tsv.gz
			
			else	
				if [[ $i -eq 0 ]] ;  then
					echoitalic " First file no. $i: [ ${filename} ] ..."
					### DEBUG
					### echo "DEBUG: check head first file"
					### zcat "$filename" | head -1
					zcat "$filename" > "$OutFileName" # Copy header if it is the first file
					cp -v $STUDYNUMBER/mask_${STUDYNUMBER}.png $MASKMASKDIR/mask_${STUDYNUMBER}.png
					cp -v $STUDYNUMBER/tilecrossed_${STUDYNUMBER}.png $MASKDIR/tilecrossed_${STUDYNUMBER}.png
					
					zcat $STUDYNUMBER/tile_selection.tsv.gz | grep -v 'Tile' >> $MASKDIR/tile_selection.txt
					cp -v $STUDYNUMBER/tile_selection.tsv.gz $MASKMASKDIR/tile_selection_${STUDYNUMBER}.tsv.gz
				
				else
					echoitalic " File no. $i: [ ${filename} ] ..."
					### DEBUG
					### echo "DEBUG: check head next file"
					### zcat "$filename" | head -2
					zcat "$filename" | tail -n +2 >> "$OutFileName" # Append from the 2nd line each file
					
					### DEBUG
					### ls -lh "$OutFileName"
					
					cp -v $STUDYNUMBER/mask_${STUDYNUMBER}.png $MASKMASKDIR/mask_${STUDYNUMBER}.png
					cp -v $STUDYNUMBER/tilecrossed_${STUDYNUMBER}.png $MASKDIR/tilecrossed_${STUDYNUMBER}.png
					
					zcat $STUDYNUMBER/tile_selection.tsv.gz | grep -v 'Tile' >> $MASKDIR/tile_selection.txt
					cp -v $STUDYNUMBER/tile_selection.tsv.gz $MASKMASKDIR/tile_selection_${STUDYNUMBER}.tsv.gz
					
				fi
			fi
		fi
		i=$(( i + 1 )) # Increase the counter
		

	done

	echo ""
	echoitalic "Gzipping the shizzle."
	gzip -vf "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".ImageExp.csv
	gzip -vf $MASKDIR/tile_selection.txt
	
	tar -zcvf "${MASKDIR}".tar.gz "${MASKDIR}"/ 
	### OBSOLETE - we use ExpressHist now
	### mv -v readme.slidemask.* "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".readme.slidemask.txt
	mv -v readme.slide2tiles.* "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".readme.slide2tiles.txt
	mv -v readme.slidenormalize.* "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".readme.slidenormalize.txt
	mv -v readme.slidecellprofiler.* "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".readme.slidecelprofiler.txt
	mv -v readme.slidewrapup.* "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".readme.slidewrapup.txt

	echo ""
	echoitalic "Checking the log -- note: no results is a good thing."
	cat "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".append.log
	
	echoitalic "====                       NOTE                           ===="
	echoitalic "You should lways check the log and review the tile-crossed images. "
	echoitalic "The logs (summarized in 'readme'-files) might contain information "
	echoitalic "regarding issues with slides run."
	echoitalic "The tile-crossed images may involve samples that have too little"
	echoitalic "or too many crosses due to debris, air bubbles, smudges, or other"
	echoitalic "artefacts on the slides. Those samples you may want to re-run, re-"
	echoitalic "scan, or exclude."
	
	echo ""

### END of if-else statement for the number of command-line arguments passed ###
fi

script_copyright_message
