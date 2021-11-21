#!/usr/bin/python3

# ----------------------------------------------------------------------------------------------------------------------
# Authors: Beatriz Borges, Joel Baptista, José Cozinheiro e Tiago Fonte
# Course: PSR
# Class: Aula 7
# Date: 17 Nov. 2021
# Description: Avaliação 2 (PSR Augmented Reality Paint) - Color Segmentation File
# ----------------------------------------------------------------------------------------------------------------------

# Importing Packages
import cv2
import numpy as np
import json
from colorama import Back, Fore

# <=================================================  Global Variables  ===============================================>

global minimumb, maximumb, minimumg, maximumg, minimumr, maximumr

minimumb = 0
maximumb = 255
minimumg = 0
maximumg = 255
minimumr = 0
maximumr = 255


# Define trackbars' functions
def ontrackbarminb(minb):
    global minimumb
    minimumb = minb


def ontrackbarmaxb(maxb):
    global maximumb
    maximumb = maxb


def ontrackbarming(ming):
    global minimumg
    minimumg = ming


def ontrackbarmaxg(maxg):
    global maximumg
    maximumg = maxg


def ontrackbarminr(minr):
    global minimumr
    minimumr = minr


def ontrackbarmaxr(maxr):
    global maximumr
    maximumr = maxr


def main():

    # <================================================  INITIALIZATION  ==============================================>

    capture = cv2.VideoCapture(0)

    # Display Initial Relevant Info
    if capture.isOpened() is True:
        print('\n' + Back.GREEN + 'Starting video' + Back.RESET)
        print('\n' + Fore.CYAN + 'Press w to exit and save color limits to file' + Fore.RESET)
        print(Fore.RED + 'Press q to exit without saving the threshold' + Fore.RESET)

    # Create Window (600 x 600) to display Normal Image
    cv2.namedWindow('Original', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Original', 600, 600)

    # Create Window to display Segmented Image
    window_name = 'Segmented'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # <==================================================  TRACKBARS  ================================================>

    # Implement a Set of Trackbars in Order to User be Able to Control Values (0 - 255) of Binarization Threshold
    cv2.createTrackbar('min B', window_name, 0, 255, ontrackbarminb)
    cv2.createTrackbar('max B', window_name, 0, 255, ontrackbarmaxb)
    cv2.createTrackbar('min G', window_name, 0, 255, ontrackbarming)
    cv2.createTrackbar('max G', window_name, 0, 255, ontrackbarmaxg)
    cv2.createTrackbar('min R', window_name, 0, 255, ontrackbarminr)
    cv2.createTrackbar('max R', window_name, 0, 255, ontrackbarmaxr)

    # Set Maximum Trackbars to a Default Beginning Position of 255
    cv2.setTrackbarPos('max B', window_name, 255)
    cv2.setTrackbarPos('max G', window_name, 255)
    cv2.setTrackbarPos('max R', window_name, 255)

    # Trackbars Init
    ontrackbarminb(0)
    ontrackbarmaxb(255)
    ontrackbarming(0)
    ontrackbarmaxg(255)
    ontrackbarminr(0)
    ontrackbarmaxr(255)

    # <==========================================  COLOR SEGMENTATION RESULTS  ========================================>

    # Real-time Update of Trackbars' Values
    while capture.isOpened():
        _, frame = capture.read()  # Get an Image from the Camera
        cv2.imshow('Original', frame)  # Display Image from the Camera

        # Achieve Ranges for each Value of RGB Channels
        ranges = {'limits': {'B': {'min': minimumb, 'max': maximumb},
                             'G': {'min': minimumg, 'max': maximumg},
                             'R': {'min': minimumr, 'max': maximumr}}}

        # Convert Ranges Dictionary into Numpy Arrays
        mins = np.array([ranges['limits']['B']['min'], ranges['limits']['G']['min'], ranges['limits']['R']['min']])
        maxs = np.array([ranges['limits']['B']['max'], ranges['limits']['G']['max'], ranges['limits']['R']['max']])

        # Create Mask for Color Segmentation
        mask = cv2.inRange(frame, mins, maxs)

        # Apply and show Created Mask in Color Segmentation Window (600 x 600)
        cv2.imshow('Segmented', mask)
        cv2.namedWindow('Segmented', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Segmented', 600, 600)

        # <======================================  SAVE / NOT SAVE PROGRESS  =========================================>

        key = cv2.waitKey(1)  # Wait a Key to stop the Program

        # Use "q" or "Q" (Quit) Key to End the Program without saving the JSON File
        if key == 113 or key == 81:
            print('\nProgram ending without saving progress')
            break

        # Use "w" or "W" (Write) Key to End the Program saving and writing the JSON File
        elif key == 119 or key == 87:
            file_name = 'limits.json'
            with open(file_name, 'w') as file_handle:
                print('\nWriting color limits to file ' + file_name)
                print(ranges)
                json.dump(ranges, file_handle)
            break

    # <=================================================  TERMINATING  ===============================================>

    capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
