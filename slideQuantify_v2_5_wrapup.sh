#!/bin/bash
#
# Description: Wraps up a slideToolKit-CellProfiler analysis for a given slide as part 
#              of a slideQuantify job-session.
# 
# The MIT License (MIT)
# Copyright (c) 2014-2021, Bas G.L. Nelissen, Sander W. van der Laan, 
# UMC Utrecht, Utrecht, the Netherlands.
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

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
	echoerror "- Argument #1  -- Study number of slide being processed, e.g. AE21."
	echoerror "- Argument #2  -- name of the stain as it appears in the filenames, e.g. FIBRIN."
	echoerror "- Argument #3  -- output filename where the CellProfiler results are stored, e.g. Image.csv (delimiter is assumed '_')."
	echoerror "- Argument #4  -- SlideToolkit directory."
	echoerror "- Argument #  -- Tiles directory."
	echoerror ""
	echoerror "An example command would be: slideQuantify_wrapup [args: AE21] [arg2: STAIN] [arg3: Image.csv] [arg4: /path/to/dir] [arg5: /path/to/dir] "
	echoerror ""
	echoerror "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	# The wrong arguments are passed, so we'll exit the script now!
	exit 1
}

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echobold "                           slideQuantify: Wrap Up"
echo ""
echoitalic "* Written by  : Sander W. van der Laan; Tim Bezemer; Tim van de Kerkhof"
echoitalic "                Yipei Song, Tim Peters"
echoitalic "* E-mail      : s.w.vanderlaan-2@umcutrecht.nl"
echoitalic "* Last update : 2023-02-09"
echoitalic "* Version     : 2.2.0"
echo ""
echoitalic "* Description : This script will start the wrap up of a slideToolKit analysis."
echoitalic "                This is SLURM based."
echo ""
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

echo ""
### REQUIRED | GENERALS	
STUDY_NUM="$1" # Depends on arg1
STAIN="$2" # Depends on arg2
OUTPUTFILENAME="$3" # Depends on arg3
SLIDETOOLKITDIR="$4" # Depends on arg5
TILESDIR="$5" # Depends on arg6

### Loading the CellProfiler-Anaconda3.8 environment
### You need to also have the conda init lines in your .bash_profile/.bashrc file
echo "..... > loading required anaconda environment containing the CellProfiler installation..."
eval "$(conda shell.bash hook)"
conda activate cp427
echo Loaded conda environment: $CONDA_PREFIX
echo ""

cd ./slideToolkit

### START of if-else statement for the number of command-line arguments passed ###
if [[ $# -lt 5 ]]; then 
	echo "Oh, computer says no! Number of arguments found \"$#\"."
	script_arguments_error "You must supply correct (number of) arguments when running *** slideQuantify_wrapup ***!"
		
else
	
	# Reference
	# https://stackoverflow.com/questions/8903239/how-to-calculate-time-elapsed-in-bash-script
	SECONDS=0
	# do some work
	
	# Collecting all the data
	echo "..... Creating [ results.txt ] and collecting data."
	if [ ! -f ./results.csv ]
	then
		# echo ${STAIN}
		# echo "test: CD68"
		if [ ${STAIN} == HE ]; then
			tee results.csv <<< 'Study_number, Stain, STAIN_count_or_area_per_Total_Tissue_area, STAIN_count_or_area, Total_Tissue_area'
		elif [ ${STAIN} == SMA ]; then
			tee results.csv <<< 'Study_number, Stain, FilterObjects, HE_nuclei_count, Total_DAB_object_area, Total_HE_nuclei_area, Total_Tissue_area'
		elif [ ${STAIN} == CD68 ]; then
			tee results.csv <<< 'Study_number, Stain, FilterObjects, HE_nuclei_count, Total_DAB_object_area, Total_HE_nuclei_area, Total_Tissue_area'
		elif [ ${STAIN} == CD66b ]; then
			tee results.csv <<< 'Study_number, Stain, Total_Filtered_Objects, Total_Tissue_area'
		elif [ ${STAIN} == CD34_DAB ]; then
			tee results.csv <<< 'Study_number, Stain, FilterObjects, HE_nuclei_count, Total_DAB_object_area, Total_HE_nuclei_area, Total_Tissue_area'
		elif [ ${STAIN} == CD34_LRP ]; then
			tee results.csv <<< 'Study_number, Stain, FilterObjects, HE_nuclei_count, Total_LRP_object_area, Total_HE_nuclei_area, Total_Tissue_area'
		else
			tee results.csv <<< 'Study_number, Stain, STAIN_count_or_area_per_Total_Tissue_area, STAIN_count_or_area, Total_Tissue_area'
		fi
	fi
	
	# Moving into the cellprofiler output directory for the given $SLIDE_NUM
	cd ./cp_output/${STUDY_NUM}/

	### DEBUG
	echo "Original study number: $STUDY_NUM"
	SCRIPT_NAME="Colsums_${STAIN}.R"
	
	# echo $STUDY_NUM, $STAIN, $(Rscript ${SLIDETOOLKITDIR}/utilities/$SCRIPT_NAME $STAIN $OUTPUTFILENAME) >> ../../results.csv
	tee -a ../../results.csv <<< "$STUDY_NUM, $STAIN, $(Rscript ${SLIDETOOLKITDIR}/utilities/$SCRIPT_NAME $STAIN $OUTPUTFILENAME)"
	# cat ../../results.txt | wc -l
	
	# moving up to the PROJECT directory again
	cd ../../

	### OLD - we may want to keep tiles as these are most time consuming to create
	### echo "..... Removing overlay images:"
	### echo "Randomly grab x (50) overlay images, and remove the rest."
	### ### ls cp_output/*.png | shuf -n $(expr $(ls cp_output/*.png | wc -l) - $RANDOM_SAMPLE) | xargs rm -v;
	### 
	### echo "..... Removing tiling directory and its contents."
	### echo "Randomly grab x (50) overlay images, and remove the rest"
	### ### ls *tiles/*.png | shuf -n $(expr $(ls *tiles/*.png | wc -l) - $RANDOM_SAMPLE) | xargs rm -v;
	### 
	### if [ -f *.ndpi ]; then 
	### 	echo "..... Removing intermediate tif- & png-files converted from NDPI-files.";
	### 	### We used to work at 40x
	### 	### rm -v *x40*.tif; 
	### 	### rm -v *x40*.png; 
	### 	### Remember - we work at 20x
	### 	### rm -v *x20*.tif; 
	### 	### rm -v *x20*.png; 
	### fi;


	### OLD - These files are each a couple KB big, so gzipping doesnt really make sense
	echo "..... Gzipping list of files to process.";
	gzip -v $TILESDIR/${STUDY_NUM}.*/files2cp.txt;
	# gzip -d $TILESDIR/${STUDY_NUM}*/files2cp.txt.gz;
	
	echo "..... Gzipping result files.";
	gzip -vf cp_output/${STUDY_NUM}/$STAIN*.gct;
	# gzip -d cp_output/${STUDY_NUM}*/$STAIN*.gct.gz;
	gzip -vf cp_output/${STUDY_NUM}/$STAIN*.csv;
	# gzip -d cp_output/${STUDY_NUM}*/$STAIN*.csv.gz;
	
	echo "..... Wrapping up this slideToolKit run successfully finished."
	
	duration=$SECONDS
	echo "[ $(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed ]"
	
### END of if-else statement for the number of command-line arguments passed ###
fi

script_copyright_message

