#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Prakhar'
# Created 8/08/2017
# Last edit 8/08/2017

# Purpose: Make a class which can provide object To obtain DTM and nDSM from DSM . Follows from algo in advanced DTM generation from very high resolution satellite stereo images
# (1) : Read Gauss smoothened image and generate hole DEM
# (2) : Fill holes using Krigging/TIN based interpolation and genrate proper DEM
# (3) : Genrate nDSM and built height estimation
# (4) : Using classified vector of Landsat built area, find heights
# (5) : reeample it to 750 m and pair with NL and plot NL vs Height


# Location of output: E:\Acads\Research\AQM\Data process\CSVOut; mostly in the Urban3D folder and Daraprocessed folder

# terminology used:
'''# output filenames produced

'''

import numpy as np
import math as math
from matplotlib import pyplot as plt
from scipy.interpolate import griddata
import cv2 as cv


# pvt imports

# * * *  * * # * * * *  * *# # * * * *  * * # * * * *  * * # * * *#    Step0: Initialize     * * *  * * # * * * *  * *# # * * * *  * * # * * * *  * * # * * * *  * *#

class DSMtrans():

    def __init__(self, DSM):

        self.city = None
        self.prod = None
        self.DSM = DSM

        # constraints/ thresholds
        self.resolution = 30 # resolution in metres of a pixel
        self.Ext = 300  # Extent of examining neighbors in metres: for 10m _ 200; for 30m - 3000

        # extent of filter window; it should be around 90meters depending on the resolution; aster - 5, for 10m - 15
        self.iExt = np.int(self.Ext / (2 * self.resolution)) * 2 + 1

        self.dThrHeightDiff = 3  # height difference in meter. >=threshold is non-ground
        self.dThrSlope = 60  # degrees using 60 degress for 30m as difficult to identify ground terrain otherwise

        # 8 directions
        self.scanlines = [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]]
        self.scannum = [0, 1, 2, 3, 4, 5, 6, 7]  # keyname for scanlines





    # * * *  * * # * * * *  * *# # * * * *  * * # * * * *  * * #   * *#    Step 1: prepare  DTM with holes  * * *  * * # * * * *  * *# # * * * *  * * # * * * *  * * # * * * *  * *#

    # function to do gaussian smoeethening on inital DSM to get approximate surface
    def Gaussiansmooth(self, DSM):
        # Gaussian blurre image
        DSMs = cv.GaussianBlur(src = DSM, ksize = (2*int(100/(2*self.resolution))+1, 2*int(100/(2*self.resolution))+1), sigmaX = 25, sigmaY = 25)

        return DSMs



    # function to generate neghbors in the direction of scan line
    def neighborhood(self, arr, dir, c0):

        dict_scannum = {
            0   : np.diag(arr),
            1   : arr[:,c0],
            2   : np.diag(np.fliplr(arr)),
            3   : np.fliplr(arr)[c0],
            4   : np.diag(arr)[::-1],
            5   : arr[:,c0][::-1],
            6   : np.diag(np.fliplr(arr))[::-1],
            7   : arr[c0]
        }

        return dict_scannum[dir]

    # actual function for DTM generation
    def DSM2DTM_scanline(self, DSM, DSMs):

        print ' Entered DSM2DTM scanline'
        # DSM - the DSM to be treated
        # DSMs - smoothened DSM
        iExt = self.iExt
        dThrHeightDiff = self.dThrHeightDiff
        dThrSlope = self.dThrSlope
        resolution = self.resolution

        # finding shape
        [m,n] = np.shape(DSM)

        #3 dim array with 8 2D bands will store the output of each pixel for each scanline
        oLabel = np.zeros([8, m,n])

        # running over thewhole imahe
        for x0 in range(0 + (iExt - 1) / 2 ,m - (iExt - 1) / 2):
            for y0 in range(0 + (iExt - 1) / 2, n - (iExt - 1) / 2):

                # temporary subsetting the region around the pix
                c0 =  (iExt-1)/2
                oDSM = DSM[x0 - c0:x0 + c0 + 1,y0 - c0:y0 + c0 + 1]
                oDSMs = DSMs[x0 - c0:x0 + c0 + 1,y0 - c0:y0 + c0 + 1]

                # running for each scanline
                for scn in self.scannum:

                    # scanline direction
                    [iX, iY] = self.scanlines[scn]

                    # local height difference
                    oDSMDiff = oDSM[c0,c0] - DSM[x0 + iX,y0 + iY]

                    # local terrain slope
                    oDSMsDiff = oDSMs[c0,c0] - DSMs[x0 + iX,y0 + iY]

                    # get neighborhood(our filter extent)
                    oNeigh = self.neighborhood(oDSM, scn, c0)

                    #slope corrected height values
                    oNeighCorr = oNeigh - (self.neighborhood(oDSMs, scn, c0) - oDSMs[c0, c0])

                    # slope corrected minimal terrain value
                    oMinNeigh = np.nanmin(oNeighCorr)

                    # difference to minimum
                    dHeightDiff = oDSM[c0, c0] - oMinNeigh

                    if (dHeightDiff > dThrHeightDiff):
                        #pixel is non - ground (0)
                        oLabel[scn, x0, y0] = 0

                    else :
                        # slope corrected height difference
                        dDelta = oDSMDiff - oDSMsDiff
                        dSignDelta = -np.sign(dDelta)
                        dSlopeLocal = math.atan2(abs(dDelta), resolution) * 180 / np.pi

                        #slope corrected angle
                        dSlope = dSlopeLocal * dSignDelta

                        if (dSlope > dThrSlope):
                            # pixel is non - ground (0)
                            oLabel[scn, x0, y0] = 0

                        else:
                            # assign as last label
                            oLabel[scn, x0, y0] = oLabel[scn, x0 - iX, y0 - iY]

                        if (dSlope < 0):
                            #pixel is ground (1)
                            oLabel[scn, x0][y0] = 1

        # with file('oLabel_try.txt', 'w') as outfile:
        #     for slice in oLabel:
        #         np.savetxt(outfile, slice)

        return oLabel
    # Function end

    # * * *  * * # * * * *  * *# # * * * *  * * # * * * *  * * #   * *#    Step 2: DEM   * * *  * * # * * * *  * *# # * * * *  * * # * * * *  * * # * * * *  * *#

    # Fnction to fill holes in DEM array f
    def fill_holes(self, f):
        print 'filling holes'
        # interpolating and filling holes
        # from stack overflow different results for 2d interpolation with scipy.interpolate-gridddata
        # http://stackoverflow.com/questions/40449024/different-results-for-2d-interpolation-with-scipy-interpolate-griddata

        # make mask of all values to be filled
        #mask = np.isnan(f)
        maskobj = np.ma.masked_where(f==0, f)
        mask = maskobj.mask

        # final shape
        lx, ly = f.shape
        x, y = np.mgrid[0:lx, 0:ly]

        # 'Fill it'
        z = griddata(np.array([x[~mask].ravel(), y[~mask].ravel()]).T, f[~mask].ravel(), (x, y), method='linear')

        return z


    # Master function to to run everything and get oytput

    def ground(self):

        DSM = self.DSM

        # get smoothenes DSM
        DSMs = self.Gaussiansmooth(DSM)

        # remove all -9999 values as nan
        #DSM[DSM<=-9999.0] = np.nan
        #DSMs[DSMs<=-9999.0] = np.nan

        # finally run function to find DSM from DEM
        oLabel = self.DSM2DTM_scanline(DSM, DSMs)

        # Now Checking which pixels have sum of scanline direction >=5. If yes then ground
        ground = DSM*(np.sum(oLabel, axis =0)>=5)

        # save ground as a raster
        # srs.arr_to_raster(ground, DSMpath, '//Urbanheights/DEMholes_try.tif')

        #ground[ground==0.0] = np.nan

        # filling holes in the DEM
        DEM = self.fill_holes(ground)

        # smoothening the DEM
        DEM = cv.GaussianBlur(src = DEM, ksize = (5,5), sigmaX = 5, sigmaY = 5)

        # Generate nDSM
        nDSM = DSM - DEM

        # not sure if this is correct but coverting all <0 pixels to ground
        nDSM[nDSM<=0] = 0

        # visualize nDSM
        plt.imshow(nDSM)

        print 'job done '

        return (DEM, nDSM)

    # fucntion end









