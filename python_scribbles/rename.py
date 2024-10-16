import pandas as pd
import numpy as np
import glob
import os

TNUMDF = pd.read_csv("TNUM_CONSENT.csv")
tifdict = {}
origdict = {}
for tif in glob.glob("*.tif"):
	newtif = tif[:4].replace(" ","-") + tif[4:].replace(" ","_")
	if "_" in newtif:
		tnum = newtif[newtif.index("T"):newtif.index("_")]	
	else:
		tnum = newtif[newtif.index("T"):newtif.index(".")]
	tifdict[newtif] = tnum
	origdict[newtif] = tif

for tifname,tnumber in tifdict.items():
	index = TNUMDF.index[TNUMDF['T_NUMBER']==tnumber]
	if index.any():
		index = (index[0])
		AE = "AE"+str(TNUMDF.get_value(index,col="STUDY_NUMBER"))
		newname = (AE+"."+tifname)
		origname = origdict[tifname]
		os.rename(origname,newname)
	else:
		pass
