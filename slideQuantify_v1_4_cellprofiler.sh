#!/bin/bash
#
# Description: Runs CellProfiler as part of a slideQuantify job-session.
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
	echoerror "- Argument #1  -- path_to CellProfiler pipeline, e.g. FIBRIN.cppipe."
	echoerror "- Argument #2  -- name of the stain as it appears in the filenames, e.g. FIBRIN. [OPTIONAL]"
	echoerror "- Argument #3  -- slidenumber being processed (should contain no spaces). [OPTIONAL]"
	echoerror ""
	echoerror "An example command would be: slideQuantify_cellprofiler [arg1: path_to_cellprofiler_pipeline] [arg2: STAIN] [arg3: slide_number] "
	echoerror ""
	echoerror "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	# The wrong arguments are passed, so we'll exit the script now!
	exit 1
}

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echobold "                           slideQuantify: CellProfiler"
echo ""
echoitalic "* Written by  : Sander W. van der Laan; Tim Bezemer; Tim van de Kerkhof"
echoitalic "                Yipei Song"
echoitalic "* E-mail      : s.w.vanderlaan-2@umcutrecht.nl"
echoitalic "* Last update : 2021-11-25"
echoitalic "* Version     : 2.1.0"
echo ""
echoitalic "* Description : This script will start the quantification for a given stain"
echoitalic "                in a given project directory using CellProfiler *after* "
echoitalic "                processing with masking, tiling, and normalizing."
echoitalic "                This is SLURM based."
echo ""
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

echo ""
### REQUIRED | GENERALS	
PIPELINE="$1" # Depends on arg1

### OPTIONAL | GENERALS	 
### https://stackoverflow.com/questions/9332802/how-to-write-a-bash-script-that-takes-optional-input-arguments
STAIN=${2-unknown} # Depends on arg2
SLIDE_NUM=${3-unknown} # Depends on arg2

### START of if-else statement for the number of command-line arguments passed ###
if [[ $# -lt 1 ]]; then 
	echo "Oh, computer says no! Number of arguments found \"$#\"."
	script_arguments_error "You must supply correct (number of) arguments when running *** slideQuantify_4_cellprofiler ***!"
		
else
	
	# Reference
	# https://stackoverflow.com/questions/8903239/how-to-calculate-time-elapsed-in-bash-script
	SECONDS=0
	# do some work

	# we check wether there is output already; if so, we exit
	if [[ -d cp_output ]]; then 
		echo "..... CellProfiler was already run, or at least there is a cp_output-directory."
		exit
	
	else
		# creating necessary output directory
		echo "..... > making output directory..."
		mkdir -pv cp_output
	
	fi

	echo "..... Starting CellProfiler run."

	### Loading the CellProfiler-Anaconda3.8 environment
	### You need to also have the conda init lines in your .bash_profile/.bashrc file
	echo "..... > loading required anaconda environment containing the CellProfiler installation..."
	eval "$(conda shell.bash hook)"
	conda activate cp4
	
	echo "..... > checking CellProfiler version..."
	cellprofiler --version	

	# running cellprofiler
	echo "..... Running CellProfiler using $PIPELINE for [ $SLIDE_NUM ] samples stained with [ $STAIN ]."
	cellprofiler -c -r -p $PIPELINE --file-list files2cp.txt -o cp_output/;

	echo "..... CellProfiler successfully finished."
	
	duration=$SECONDS
	echo "[ $(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed ]"
	
### END of if-else statement for the number of command-line arguments passed ###
fi

script_copyright_message

