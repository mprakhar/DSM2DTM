#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Prakhar'
# Created 8/08/2017
# Last edit 8/05/2018

# Purpose: To use  obtain normalizedDSM (nDSM) and DTM from DSM using the classDSM.py using regular method of running in Pycharm

# import library for reading raster images
import rasterio as rio
import numpy as np
import math as math
from matplotlib import pyplot as plt
from scipy.interpolate import griddata
import cv2 as cv
import argparse
import datetime

#improt the classDSM
#import classDSM as genDSM
import classDSM_v2_20180705 as genDSM
# ===============++++++++++   ------- to RUN THE CODE type -----   +++++===========
 
def param_init(inputDSMpath, img_resolution, neighborhood_kernel, height_threshold, slope_thresold, outputnDSMpath  ):


	# open the AW3D raster stored in DSMpath as an array DSMarr.
	DSMpath = inputDSMpath
	DSMarr = rio.open(DSMpath).read(1)

	#set the DSMarr as an object of genDSM
	obj = genDSM.DSMtrans(DSMarr)
	obj.resolution = img_resolution
	obj.Ext = neighborhood_kernel
	obj.dThrHeightDiff = height_threshold
	obj.dThrSlope  = slope_thresold

	#set the outpath
	nDSMpath = outputnDSMpath


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
	(DEMarr, nDSMarr) = obj.ground()

	#these arrays can be saved with same georeference as input DSM. Here we are saving the building height nDSM into nDSMpath
	#get aLL ttributes of thwe source
	src = rio.open(DSMpath)
	# context manager.
	with rio.Env():
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




param_init(
	inputDSMpath=r r"E:\OneDrive\AQM_Research\Codes_W\Yangon_DSM\for_labserver\notebook\Yangon_inner_AW3D_30m.tif"
	, img_resolution=30
	, neighborhood_kernel=300
	, height_threshold=3
	, slope_thresold=30
	,
	outputnDSMpath=r"\\Yangon_inner_AW3D_30moutput.tif"

)

