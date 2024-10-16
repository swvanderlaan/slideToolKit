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
	echoerror "- Argument #2  -- (the path to) the filename, e.g. Image.gct.gz, the script will automatically append STAIN, e.g. STAIN_Image.gct.gz"
    echoerror "- Argument #3  -- (the path to) the slideToolkit output directory, e.g. ./slideToolkit"
	echoerror ""
	echoerror "An example command would be: slideAppendGCT [arg1: STAIN] [arg2: Image.gct.gz] [arg3: ./slideToolkit]"
	echoerror "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  	# The wrong arguments are passed, so we'll exit the script now!
  	exit 1
}

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echobold "                            slideAppendGCT"
echo ""
echoitalic "* Written by  : Tim G.M. van de Kerkhof; Sander W. van der Laan"
echoitalic "* E-mail      : s.w.vanderlaan-2@umcutrecht.nl"
echoitalic "* Last update : 2021-11-26"
echoitalic "* Version     : v1.0.0"
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
RESULTSFILENAME="$2"
OUTDIR="$3"

if [[ $# -lt 3 ]]; then 
	echoerrorflash "Oh, computer says no! Number of arguments found $#."
	script_arguments_error "You must supply correct (number of) arguments when running *** slideAppendGCT ***!"

else

	OutFileName=$OUTDIR/"${TODAY}.${STAIN}.ImageExp.gct" # Fix the output name
	
	echo ""
	echoitalic "Creating a new log."
	# make a new append.log
	echo "STUDYNUMBER FILENAME" > $OUTDIR/"${TODAY}"."${STAIN}".appendgct.log
	
	i=0 # Reset a counter
	echo ""
	echoitalic "Collecting data for:"
	for filename in $OUTDIR/cp_output/*/"${STAIN}"_"${RESULTSFILENAME}"; do 
		if [ "$filename"  != "$OutFileName" ] ; then # Avoid recursion
		
			cols=$(zcat < "$filename" | tail -n +3 | awk -F'\t' '{ print NF }' | uniq | wc -l)
			if [[ "$cols" -gt 1 ]]; then
				STUDYNUMBER=${filename%%\/*} # Remove everything from the first slash >> https://unix.stackexchange.com/questions/268134/extract-a-specific-part-of-the-path-of-a-file
				echo "**ERROR** no new line for end-of-file for [ $STUDYNUMBER ]."
				echo "$STUDYNUMBER $filename" >> $OUTDIR/"${TODAY}"."${STAIN}".appendgct.log
		
			else	
				if [[ $i -eq 0 ]] ;  then
					echoitalic " First file no. $i: [ ${filename} ] ..."
					### DEBUG
					### echo "DEBUG: check head first file"
					### zcat "$filename" | tail -n +3 | head -1
					zcat < "$filename" | tail -n +3 > "$OutFileName" # Copy header if it is the first file
				
				else
					echoitalic " File no. $i: [ ${filename} ] ..."
					### DEBUG
					### echo "DEBUG: check head next file"
					### zcat "$filename" | tail -n +4 | head -1
					zcat < "$filename" | tail -n +4 >> "$OutFileName" # Append from the 2nd line each file
					
					### DEBUG
					### ls -lh "$OutFileName"
					
				fi
			fi
		fi
		i=$(( i + 1 )) # Increase the counter
	done

	echo ""
	echoitalic "Gzipping the shizzle."
	gzip -vf $OUTDIR/"${TODAY}"."${STAIN}".ImageExp.gct
	### DEBUG
	### echo "DEBUG: check heads and tails of concatenated output file"
	### zcat "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".ImageExp.gct.gz | head -3
	### zcat "${TODAY}"."${STAIN}"."${STUDYTYPE}"."${IMAGETYPE}".ImageExp.gct.gz | tail
	
	echo ""
	echoitalic "Checking the log -- note: no results is a good thing."
	cat $OUTDIR/"${TODAY}"."${STAIN}".appendgct.log
	
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
