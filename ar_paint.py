#!/usr/bin/python3
import copy

import cv2
import argparse
import json
import numpy as np


def JsonReader(json_file): # Read and format json file information
    f = open(json_file)
    data = json.load(f) # All information of json file
    limits = data['dependencies'] # Just limits info

    B = {'max': limits['B']['max'], 'min': limits['B']['min']}
    G = {'max': limits['G']['max'], 'min': limits['G']['min']}
    R = {'max': limits['R']['max'], 'min': limits['R']['min']}

    return R, G, B


def main():

    # <======================GET LIMITS ON JSON FILE==================================>

    parser = argparse.ArgumentParser(description='JSON file with limits information')
    parser.add_argument('-j', '--json', type=str, help='Path to JSON file')
    args = vars(parser.parse_args())

    lim_R, lim_G, lim_B = JsonReader(args['json'])

    #  <===================== Video Capture =================================>

    capture = cv2.VideoCapture(0)
    _, frame = capture.read()

    windows = ['Camera', 'Segmented image', 'Largest Component', 'Canvas']
    positions = [(0, 0), (0, 600), (650, 0), (1200, 0)]
    canvas = 255*np.ones(frame.shape)

    for window, position in zip(windows, positions): # Showing and positioning windows
        cv2.namedWindow(window)
        cv2.moveWindow(window, position[0], position[1])

    kernel = np.ones((2, 2), np.uint8) # for pre-processing images
    while True:

        # ---------------------- Frame Capture -------------------------
        _, frame = capture.read()
        cv2.imshow(windows[0], frame)

        frame_GUI = copy.deepcopy(frame)
        frame_largest = np.zeros(frame.shape)

        # ---------------------- Segmentation -------------------------
        mask = cv2.inRange(frame_GUI, (lim_B['min'], lim_G['min'], lim_R['min']),
            (lim_B['max'], lim_G['max'], lim_R['max']))

        # ---------------------- Pre-processing -------------------------
        mask_dilation = cv2.dilate(mask, kernel, iterations=2)
        mask_closing = cv2.morphologyEx(mask_dilation, cv2.MORPH_CLOSE, kernel)

        cv2.imshow(windows[1], mask_closing)

        # ---------------------- Finding Cellphone Screen -------------------------
        contours, hierarchy = cv2.findContours(mask_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0: # Finds contour with maximum area and draws it on window "Largest Component"
            areas = [cv2.contourArea(c) for c in contours]
            max_index = np.argmax(areas)
            cnt_max = contours[max_index]
            mask_largest = cv2.fillPoly(frame_largest, pts=[cnt_max], color=(255, 255, 255))

            cv2.imshow(windows[2], mask_largest)
            #  <===================== Canvas Drawing =================================>
            M = cv2.moments(cnt_max)
            cX = int(M['m10']/M['m00'])
            cY = int(M['m01'] / M['m00'])

            cv2.imshow(windows[3], canvas)

            cv2.circle(canvas, (cX, cY), 7, (0, 0, 255), -1)

        key = cv2.waitKey(1)
        if key != -1:
            break



if __name__ == "__main__":
    main()
