# DSM2DTM
A) This is a Python based implementation of "ADVANCED DTM GENERATION FROM VERY HIGH RESOLUTION SATELLITE STEREO IMAGES" by Perko et al (2015).
https://www.isprs-ann-photogramm-remote-sens-spatial-inf-sci.net/II-3-W4/165/2015/isprsannals-II-3-W4-165-2015.pdf

B)This runs on Python 2.7

C) To run:
python get_nDSM.py  --inputDSMpath 'path/for_trial.tif'  --outputnDSMpath 'outfilesample.tif'  --img_resolution 30  --neighborhood_kernel 300  --height_threshold 3  --slope_threshold 60

D) Help options:
python get_nDSM.py -h

Varibale decription
 img_resolution is the resolution in meters. For SRTM it should be 90. Regarding other optional arguments:
  -
  --inputDSMpath INPUTDSMPATH
                        full path to DSM file which needs to be converted.
                        e.g. \home\AW3D.tif
  --outputnDSMpath OUTPUTNDSMPATH
                        full path to output nDSM file after converted e.g.
                        \home\AW3Dout.tif
  --img_resolution IMG_RESOLUTION
                        image resolution in meter
  --neighborhood_kernel NEIGHBORHOOD_KERNEL
                        how far (in meter) should the kernel size be considered.
                        Recommended - Lower distance for higher resolution.
  --height_threshold HEIGHT_THRESHOLD
                        minimum height difference (in meter) between ground
                        and building. Generally height of 1 storey building.
  --slope_threshold SLOPE_THRESHOLD
                        minimum slope between a building and ground pixel (in
                        degrees)

E) Please also ensure that following modules are present:
Rasterio               #(Install by: pip install rasterio)
Cv2
Scipy
Numpy
Math
Matplotlib
