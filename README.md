Some files are to be run on python wherever is desired (local or datalabs) (.py) while others are built to be run on datalabs (jupyter notebook) to access the structure of data. In this read me file we explain the utility of the different files:

Description of files:

Dataset_LineDetections.ipynb  : To be run on datalabs. Detects all lines in the Cheops data set saved in data labs. 

FullArrayCompleteness.ipynb   : To be run on datalabs. Perfoms the completeness analysis for the full arrays.

SubArrayCompleteness.ipynb    : To be run on datalabs. Perfoms the completeness analysis for the sub arrays.

ImageSimulator.py             : To be run wherever desired. Adds lines to a selected image for different brightness levels.

ImageSimulator_AllBackgrounds.py : To be run on datalabs. Simulates NLines images with lines, of a given brightness, for all backgrounds in the CHEOPS database. 




Assisting Files:

PSF2020_2.fits        : CHEOPS PSF which is used by the codes
