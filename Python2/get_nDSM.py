# this is an example of how to obtain normalizedDSM (nDSM) and DTM from DSM using the classDSM.py

# import library for reading raster images
import rasterio as rio
import numpy as np
import math as math
from matplotlib import pyplot as plt
from scipy.interpolate import griddata
import cv2 as cv
import argparse

#improt the classDSM
from classDSM import DSMtrans as genDSM

# ===============++++++++++   ------- to RUN THE CODE type -----   +++++===========
'''
python get_nDSM.py  --inputDSMpath '/mnt/usr1/home/prakhar/Research/AQM_research/Data/Data_raw/AW3D/for_trial.tif'  --outputnDSMpath 'outfilesample.tif'  --img_resolution 30  --neighborhood_kernel 300  --height_threshold 3  --slope_threshold 60

'''

#getting infor from the parser
parser = argparse.ArgumentParser()
parser.add_argument("--inputDSMpath", help="full path to DSM file while needs to be converted. e.g. \home\AW3D.tif")
parser.add_argument("--outputnDSMpath", help="full path to output nDSM file after converted   e.g. \home\AW3Dout.tif")
parser.add_argument("--img_resolution", help="image resolution in meter")
parser.add_argument("--neighborhood_kernel", help="how far (in metres) should the kernel be considered")
parser.add_argument("--height_threshold", help=" minimum height difference (in meter) between ground and building. Generally height of 1 storey ")
parser.add_argument("--slope_threshold", help="minimum slope between a building and ground pixel (in degrees) ")

a = parser.parse_args()

# open the AW3D raster stored in DSMpath as an array DSMarr.
DSMpath = a.inputDSMpath
DSMarr = rio.open(DSMpath).read(1)

#set the DSMarr as an object of genDSM
obj1 = genDSM(DSMarr)
obj1.resolution = int(a.img_resolution)
obj1.Ext = int(a.neighborhood_kernel)
obj1.dThrHeightDiff = int(a.height_threshold)
obj1.dThrSlope  = int(a.slope_threshold)

#set the outpath
nDSMpath = a.outputnDSMpath


'''
 Following parameters can be set.
        obj.city = None
        obj.prod = None
        obj.DSM = DSM

        # constraints/ thresholds
        obj.resolution = 30 # resolution in metres of a pixel
        obj.Ext = 300  # Extent of neighbors in metres: for 10m _ 200; for 30m - 3000

        # extent of filter window; it should be around 90meters depending on the resolution; aster - 5, for 10m - 15
        obj.iExt = np.int(obj.Ext / (2 * obj.resolution)) * 2 + 1

        obj.dThrHeightDiff = 3  # meter
        obj.dThrSlope = 60  # degrees using 60 degress for 30m as difficult to identify ground terrain otherwise

        # 8 directions
        obj.scanlines = [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]]
        obj.scannum = [0, 1, 2, 3, 4, 5, 6, 7]  # keyname for scanlines

#ALthough the default parameters set have been tested in Yangon, they can be further refined else the used as it is.
'''


# running the ground function generates the DTM and nDSM arrays
(DEMarr, nDSMarr) = obj1.ground()

#these arrays can be saved with same georeference as input DSM. Here we are saving the building height nDSM into nDSMpath
#get aLL ttributes of thwe source
src = rio.open(DSMpath)
# context manager.
with rio.drivers():
	# Write the product as a raster band to a new 8-bit file. For
	# the new file's profile, we start with the meta attributes of
	# the source file, but then change the band count to 1, set the
	# dtype to uint8, and specify LZW compression.
	profile = src.profile
	profile.update(
		dtype=rio.float32,
		count=1,
		compress='lzw')

	with rio.open(nDSMpath, 'w', **profile) as dst:
		dst.write(nDSMarr.astype(rio.float32), 1)

print 'output saved'
