#!/usr/bin/python3
import argparse
import numpy as np
import json
from functools import partial
import cv2
from colorama import Back, Fore


def onTrackBars(_, window_name):
    minB = cv2.getTrackbarPos('minB', window_name)
    maxB = cv2.getTrackbarPos('maxB', window_name)
    minG = cv2.getTrackbarPos('minG', window_name)
    maxG = cv2.getTrackbarPos('maxG', window_name)
    minR = cv2.getTrackbarPos('minR', window_name)
    maxR = cv2.getTrackbarPos('maxR', window_name)

    limits = {'B': {'min': minB, 'max': maxB},
              'G': {'min': minG, 'max': maxG},
              'R': {'min': minR, 'max': maxR}}

    mins = np.array([limits['B']['min'], limits['G']['min'], limits['R']['min']])
    maxs = np.array([limits['B']['max'], limits['G']['max'], limits['R']['max']])


def main():

    # --------------------INITIALIZATION-------------------------

    capture = cv2.VideoCapture(0)
    # Window name definition
    window_name_ori = 'Camera'
    window_name_seg = 'Segmented image'

    if capture.isOpened() is True:
        print(Back.GREEN + 'Starting video' + Back.RESET)
        print(Fore.LIGHTYELLOW_EX + 'Press w to exit and save' + Fore.RESET)
        print(Fore.RED + 'Press q to exit without saving the threshold' + Fore.RESET)

    # Show image
    cv2.namedWindow(window_name_ori, cv2.WINDOW_NORMAL)
    cv2.namedWindow(window_name_seg, cv2.WINDOW_NORMAL)

    onTrackbar_partial = partial(onTrackBars, window_name=window_name_seg)

    # Create all trackbar
    cv2.createTrackbar('minB', window_name_seg, 0, 255, onTrackbar_partial)
    cv2.createTrackbar('maxB', window_name_seg, 0, 255, onTrackbar_partial)
    cv2.createTrackbar('minG', window_name_seg, 0, 255, onTrackbar_partial)
    cv2.createTrackbar('maxG', window_name_seg, 0, 255, onTrackbar_partial)
    cv2.createTrackbar('minR', window_name_seg, 0, 255, onTrackbar_partial)
    cv2.createTrackbar('maxR', window_name_seg, 0, 255, onTrackbar_partial)

    while capture.isOpened():
        # Get an image from the camera and show
        _, frame = capture.read()
        cv2.imshow(window_name_ori, frame)
        key = cv2.waitKey(1)  # Wait a key to stop the program

        # ranges = {'limits': {'B': {'max': maxB, 'min': minB},
        #                      'G': {'max': maxG, 'min': minG},
        #                      'R': {'max': maxR, 'min': minR}}}
        ranges = {'limits': {'B': {'max': 255, 'min': 0},
                             'G': {'max': 255, 'min': 0},
                             'R': {'max': 255, 'min': 229}}}

        mins = np.array([ranges['limits']['B']['min'], ranges['limits']['G']['min'], ranges['limits']['R']['min']])
        maxs = np.array([ranges['limits']['B']['max'], ranges['limits']['G']['max'], ranges['limits']['R']['max']])

        cv2.namedWindow(window_name_seg)

        key = cv2.waitKey(1)
        # Keyboard inputs to finish the cycle
        if key == ord('q'):
            print(Fore.RED + 'You pressed "q" so you quit the program' + Fore.RESET)
            break
    # ------------------TERMINATING-------------------------------------

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()