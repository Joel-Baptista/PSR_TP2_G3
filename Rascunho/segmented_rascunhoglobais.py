#!/usr/bin/python3

# ---------------------------------------------------------------------
# Authors: Beatriz Borges, Joel Baptista, José Cozinheiro e Tiago Fonte
# Course: PSR
# Class: Aula 7
# Date: 17 Nov. 2021
# Description: Avaliação 2 (PSR Augmented Reality Paint)
# ---------------------------------------------------------------------

import cv2
import numpy as np
import json
from colorama import Back, Fore


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
    global minimumb, maximumb, minimumg, maximumg, minimumr, maximumr

    minimumb = 0
    maximumb = 255
    minimumg = 0
    maximumg = 255
    minimumr = 0
    maximumr = 255

    capture = cv2.VideoCapture(0)
    window_name_original = 'Camera'

    if capture.isOpened() is True:
        print('\n' + Back.GREEN + 'Starting video' + Back.RESET)
        print('\n' + Fore.CYAN + 'Press w to exit and save color limits to file' + Fore.RESET)
        print(Fore.RED + 'Press q to exit without saving the threshold' + Fore.RESET)

    cv2.namedWindow(window_name_original, cv2.WINDOW_NORMAL)

    window_name = 'Segmented'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    cv2.createTrackbar('min B', window_name, 0, 255, ontrackbarminb)
    cv2.createTrackbar('max B', window_name, 0, 255, ontrackbarmaxb)
    cv2.createTrackbar('min G', window_name, 0, 255, ontrackbarming)
    cv2.createTrackbar('max G', window_name, 0, 255, ontrackbarmaxg)
    cv2.createTrackbar('min R', window_name, 0, 255, ontrackbarminr)
    cv2.createTrackbar('max R', window_name, 0, 255, ontrackbarmaxr)

    cv2.setTrackbarPos('max B', window_name, 255)
    cv2.setTrackbarPos('max G', window_name, 255)
    cv2.setTrackbarPos('max R', window_name, 255)

    ontrackbarminb(0)
    ontrackbarmaxb(255)
    ontrackbarming(0)
    ontrackbarmaxg(255)
    ontrackbarminr(0)
    ontrackbarmaxr(255)

    while capture.isOpened():
        _, frame = capture.read()
        cv2.imshow(window_name_original, frame)

        ranges = {'limits': {'B': {'min': minimumb, 'max': maximumb},
                             'G': {'min': minimumg, 'max': maximumg},
                             'R': {'min': minimumr, 'max': maximumr}}}

        mins = np.array([ranges['limits']['B']['min'], ranges['limits']['G']['min'], ranges['limits']['R']['min']])
        maxs = np.array([ranges['limits']['B']['max'], ranges['limits']['G']['max'], ranges['limits']['R']['max']])

        mask = cv2.inRange(frame, mins, maxs)

        cv2.imshow(window_name, mask)
        key = cv2. waitKey(1)

        if key == ord('q'):
            print('Program ending')
            break

        elif key == ord('w'):
            file_name = '../limits.json'
            with open(file_name, 'w') as file_handle:
                print('\nWriting color limits to file ' + file_name)
                print(ranges)
                json.dump(ranges, file_handle)
            break


if __name__ == '__main__':
    main()
