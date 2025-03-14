from astropy.io import fits
import matplotlib.pyplot as plt
# COMPLETENESS ANALYSIS

# This reads the PSF of CHEOPS which is required to create the line
PSF_file = fits.open('PSF2020_2.fits')
PSF = PSF_file[1].data[0]
PSF_file.close()

# These are the intensities of the line, which you can choose; around 4800 is when the images start to get into the noise
Brightness = [316, 428, 579, 784, 1062, 1438, 1947, 2636, 3569, 4832, 6443]; NLines = 500;



import numpy as np
import random
from scipy.signal import fftconvolve
import cv2

def AddLine(Image,Strength,PSF,nLines=1, maxIP = 1):
    mask = np.isnan(Image)
    if sum(sum(mask)) == 0:
        mask = Image == 0
    Image[mask] = 0
    Line = np.zeros(Image.shape, dtype=np.uint16)
    params = []
    for i in range(nLines):
        while True:
            start_point, end_point = generate_random_line(Image.shape[0])
            x1, y1 = start_point
            x2, y2 = end_point
            rho, theta = convert_to_rho_theta(x1, y1, x2, y2)
            IP = abs(rho - Image.shape[0]/2*np.cos(theta) - Image.shape[1]/2*np.sin(theta)) / 100
            if IP < maxIP:
                break
            
        IterLine = np.zeros(Image.shape, dtype=np.uint16)
        cv2.line(IterLine, start_point, end_point, Strength, 1)
        Line += IterLine
        params.append([rho,theta])
        
    Line = fftconvolve(Line, PSF, mode='same')
    Line[mask] = 0
    return Image + Line, IP, params

def generate_random_line(image_size):
    # Define the four sides of the image as options
    sides = [
        (0, random.randint(0, image_size-1)),  # Left side
        (random.randint(0, image_size-1), 0),  # Top side
        (image_size-1, random.randint(0, image_size-1)),  # Right side
        (random.randint(0, image_size-1), image_size-1)  # Bottom side
    ]
    
    # Choose the first point from any side
    x1, y1 = random.choice(sides)
    
    # Determine the index of the side to remove
    if x1 == 0:
        sides.pop(0)  # Remove the left side
    elif y1 == 0:
        sides.pop(1)  # Remove the top side
    elif x1 == image_size-1:
        sides.pop(2)  # Remove the right side
    else:
        sides.pop(3)  # Remove the bottom side
    
    # Choose the second point from the remaining three sides
    x2, y2 = random.choice(sides)
    
    return (x1, y1), (x2, y2)

def convert_to_rho_theta(x1, y1, x2, y2):
    # Calculate the angle theta
    theta = np.arctan2((y2 - y1), (x2 - x1))  + np.pi/2# Angle of the line in radians
    
    # Calculate rho using one point on the line (x1, y1)
    rho = x1 * np.cos(theta) + y1 * np.sin(theta)

    return rho, theta


# Read a Base Image
Image = 'CH_PR100002_TG000901_TU2020-04-18T19-03-30_SCI_COR_SubArray_V0300.fits'; Image = fits.open(Image); Image = Image[1].data[0]
for Brilho in Brightness:
    for i in range(NLines):
        Image_line, IP, params = AddLine(Image,Brilho,PSF,nLines=1,maxIP = 0.9)

        # This is to see the before and after of image addition; after you see the example just remove or indent
        fig,axis = plt.subplots(1,2); 
        axis[0].imshow(Image,cmap='gray',vmin=None or np.nanpercentile(Image,1),vmax=None or np.nanpercentile(Image, 85)); 
        axis[1].imshow(Image_line,cmap='gray',vmin=None or np.nanpercentile(Image_line,1),vmax=None or np.nanpercentile(Image_line, 85))
        plt.show()

