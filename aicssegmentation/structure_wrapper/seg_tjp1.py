import numpy as np
import os
from skimage.morphology import remove_small_objects, watershed, dilation, ball
from ..pre_processing_utils import intensity_normalization, image_smoothing_gaussian_slice_by_slice
from ..core.seg_dot import dot_3d
from ..core.vessel import vesselness3D
from skimage.feature import peak_local_max
from scipy.ndimage import distance_transform_edt
from skimage.measure import label


def TJP1_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [3, 17]  #TODO
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    vesselness_sigma = [1.5]
    vesselness_cutoff = 0.2
    minArea = 15
    ##########################################################################

    ###################
    # PRE_PROCESSING
    ###################
    # intenisty normalization (min/max)
    struct_img = intensity_normalization(struct_img, scaling_param=intensity_norm_param)
    
    # rescale if needed
    if rescale_ratio>0:
        struct_img = processing.resize(struct_img, [1, rescale_ratio, rescale_ratio], method="cubic")
        struct_img = (struct_img - struct_img.min() + 1e-8)/(struct_img.max() - struct_img.min() + 1e-8)
        gaussian_smoothing_truncate_range = gaussian_smoothing_truncate_range * rescale_ratio

    # smoothing with gaussian filter
    structure_img_smooth = image_smoothing_gaussian_slice_by_slice(struct_img, sigma=gaussian_smoothing_sigma, truncate_range=gaussian_smoothing_truncate_range)

    ###################
    # core algorithm
    ###################

    # vesselness 3d 
    response = vesselness3D(structure_img_smooth, sigmas=vesselness_sigma,  tau=1, whiteonblack=True)
    bw = response > vesselness_cutoff
    
    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)

    # output
    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    return seg



'''
drug:
0: vehicle
1: Brefeldin
2: Paclitaxol
3: Staurosporine
4: s-Nitro-Blebbistatin
5: Rapamycin
'''

def ZO1(img, drug_type):

    if drug_type==0:
        bw = Vehicle(img)
    elif drug_type==1:
        bw = Brefeldin(img)
    elif drug_type==2:
        bw = Paclitaxol(img)
    elif drug_type==3:
        bw = Staurosporine(img)
    elif drug_type==4:
        bw = Blebbistatin(img)
    elif drug_type==5:
        bw = Rapamycin(img)
    else:
        print('unsupported drug type')
        bw = None

    return bw 


def Vehicle(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.15
    minArea = 30
    dynamic_range = 6
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    #print(np.mean(struct_img))

    response = vesselness3D(struct_img, scale_range=(2,5), scale_step=1,  tau=1, whiteonblack=True)
    # range = (1,3) --> sigma = 1, 2 (3 is not included)

    # thresholding the response
    bw = response>thresh_3d
    bw = remove_small_objects(bw, min_size=minArea, connectivity=1, in_place=False)

    return bw

def Brefeldin(struct_img):
    bw = Vehicle(struct_img)

    return bw 

def Paclitaxol(struct_img):
    bw = Vehicle(struct_img)

    return bw 
    
def Staurosporine(struct_img):
    bw = Vehicle(struct_img)

    return bw 

def Blebbistatin(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.1
    minArea = 30
    dynamic_range = 6
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    #print(np.mean(struct_img))

    response = vesselness3D(struct_img, scale_range=(1,6), scale_step=2,  tau=1, whiteonblack=True)
    # range = (1,3) --> sigma = 1, 2 (3 is not included)

    # thresholding the response
    bw = response>thresh_3d
    bw = remove_small_objects(bw, min_size=minArea, connectivity=1, in_place=False)

    return bw

def Rapamycin(struct_img):
    bw = Vehicle(struct_img)

    return bw 