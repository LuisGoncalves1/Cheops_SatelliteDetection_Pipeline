Line_brightness = 10000; NLines = 100 # Choose the brightness of the line you want to test on all arrays, and the number of lines per array

import os
from astropy.io import fits
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

def DetermineSpread(ImageData):
    mask1 = ImageData < 500
    mask2 = ImageData > -500
    mask3 = ImageData != 0
    mask = (mask1) & (mask2) & (mask3)
    Image = ImageData[mask]

    hist, bin_edges = np.histogram(Image,bins=100)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    peak_idx = np.argmax(hist)
    peak_value = bin_centers[peak_idx]
    left_side_data = Image[Image<peak_value] 
    std = np.sqrt(np.sum( (left_side_data - peak_value) **2) / (len(left_side_data) -1) )
    return std


np.set_printoptions(linewidth=np.inf)
Folder = 'data/user/che_data_dev/repo'
files = np.array(sorted(os.listdir(Folder)))
PSF_file = fits.open('PSF2020_2.fits')
PSF = PSF_file[1].data[0]
PSF_file.close()



with open('Ignorar.txt','r') as t:
    SkipFiles = []
    while True:
        linha = t.readline()
        if linha == '':
            break
        SkipFiles.append(linha.strip())
    SkipFiles = np.array(SkipFiles)

for Progress,dataFolder in enumerate(files):
    print(dataFolder, Progress, len(files), end='\r') 

    if dataFolder in SkipFiles:
        continue
    FileFolder = f"{Folder}/{dataFolder}/L1/SCI_COR_SubArray"
    try:
        file1 = sorted(os.listdir(FileFolder))[-1]
    except:
        continue

    file = f'{FileFolder}/{file1}'
    myFits = fits.open(file)
    header = myFits[1].header
    Images = myFits[1].data / header['NEXP']

    
    # This process selects a not terrible image
    skip = False
    Frame = int(len(Images)/2)
    while True:
        if Frame > len(Images)-1:
            skip = True
            break
        Image = Images[Frame]
        Image -= np.nanmedian(Image)
        parametro = DetermineSpread(Image)
        
        if (parametro > 40):
            Frame += 5
            continue
        else:
            break

        
    for i in range(NLines):
        Image_line = Image.copy()
        Image_line, IP, params = AddLine(Image_line,Line_brightness,PSF,nLines=1,maxIP = 0.9)

        print('here')
        time.sleep(500)
        # DO something with the Image_line

    del Image

    myFits.close()
    
