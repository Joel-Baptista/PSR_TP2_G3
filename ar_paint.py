#!/usr/bin/python3
import copy

import cv2
import argparse
import json
import numpy as np

def paintMode():
    parser = argparse.ArgumentParser(description="PARI AR Paint")
    parser.add_argument('-usp',
                        '--use_shake_prevention',
                        help="Use Shake Detection.",
                        action="store_true")
    parser.add_argument('-video',
                        '--draw_on_video',
                        help="Use video stream as paint screen",
                        action="store_true")
    args = vars(parser.parse_args())
    return args


def JsonReader(json_file): # Read and format json file information
    f = open(json_file)
    data = json.load(f) # All information of json file
    limits = data['limits'] # Just limits info

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

    cv2.imshow(windows[3], canvas)
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
        # <----------------------------------- Keyboard Commands ---------------------------------------->
        color = (255, 0, 0) #default color
        radius = 5          #default radius
        command = cv2.waitKey(1)  #keyboard command
        if command == 114:  # Press 'r' to paint red

            color = (0, 0, 255)
            del command

        elif command == 103:  # Press 'g' to paint green

            color = (0, 255, 0)
            del command

        elif command == 98:  # Press 'b' to paint blue

            color = (255, 0, 0)
            del command

        elif command == 43:  # Press '+' to get bigger radius
            radius += 1
            del command

        elif command == 45:  # Press '-' to get smaller radius
            if radius > 1:
                radius -= 1
            del command

        elif command == 119:  # Press 'w' to save sketch


        elif command == 113:  # Press 'q' to quit
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()
