#!/usr/bin/python3
import copy
from colorama import Fore, Back, Style
import cv2
import argparse
import json
import numpy as np
from time import time, ctime, sleep


def colormask(img):
    mask_R = cv2.inRange(img, (0, 0, 0), (0, 0, 255))
    mask_G = cv2.inRange(img, (0, 0, 0), (0, 255, 0))
    mask_B = cv2.inRange(img, (0, 0, 0), (255, 0, 0))

    mask = cv2.bitwise_or(mask_R, mask_G)
    mask = cv2.bitwise_or(mask, mask_B)

    return mask

def paintMode():
    parser = argparse.ArgumentParser(description="PSR AR Paint")
    parser.add_argument('-j', '--json', type=str, help='Path to JSON file')
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
    # <===========================================  INITIALIZATION  =========================================>

    parameters = {'color': (0, 0, 255), 'radius': 5}
    previous_point_canvas = None
    previous_point_frame = None
    rules()

    # <======================================  GET LIMITS ON JSON FILE  ====================================>

    args = paintMode()

    lim_R, lim_G, lim_B = JsonReader(args['json'])

    # <===========================================  VIDEO CAPTURE  =========================================>

    capture = cv2.VideoCapture(0)
    _, frame = capture.read()

    windows = ['Camera', 'Segmented image', 'Largest Component', 'Canvas']
    positions = [(0, 0), (0, 600), (650, 0), (1200, 0)]
    canvas = 255 * np.ones((1000, 1000, 3))
    canvas_frame = 255 * np.ones(frame.shape)
    h_canvas, w_canvas, _ = canvas.shape
    h_frame, w_frame, _ = frame.shape

    for window, position in zip(windows, positions): # Showing and positioning windows
        cv2.namedWindow(window)
        cv2.moveWindow(window, position[0], position[1])

    kernel = np.ones((2, 2), np.uint8) # for pre-processing images
    cv2.imshow(windows[3], canvas)

    while True:
        # <===========================================  FRAME CAPTURE  ===========================================>
        _, frame = capture.read()

        frame_GUI = copy.deepcopy(frame)
        frame_GUI = cv2.flip(frame_GUI, 1)
        frame_draw = copy.deepcopy(frame_GUI)
        frame_largest = np.zeros(frame.shape)

        cv2.imshow(windows[0], frame_GUI)

    # <=============================================  SEGMENTATION  ===========================================>

        mask = cv2.inRange(frame_GUI, (lim_B['min'], lim_G['min'], lim_R['min']),
            (lim_B['max'], lim_G['max'], lim_R['max']))

    # <============================================  PRE-PROCESSING  ===========================================>

        mask_dilation = cv2.dilate(mask, kernel, iterations=2)
        mask_closing = cv2.morphologyEx(mask_dilation, cv2.MORPH_CLOSE, kernel)

        cv2.imshow(windows[1], mask_closing)

    # <========================================  FINDING CELLPHONE SCREEN  =====================================>

        contours, hierarchy = cv2.findContours(mask_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0: # Finds contour with maximum area and draws it on window "Largest Component"

            area = max(contours, key=cv2.contourArea)
            area_condition = cv2.contourArea(area)

            areas = [cv2.contourArea(c) for c in contours]
            max_index = np.argmax(areas)
            cnt_max = contours[max_index]
            mask_largest = cv2.fillPoly(frame_largest, pts=[cnt_max], color=(255, 255, 255))
            cv2.imshow(windows[2], mask_largest)
    # <=============================================  CANVAS DRAWING  =========================================>
            if area_condition > 350:  # Area must be at least 350 pixels
                M = cv2.moments(cnt_max)    # Finds the object's moments
                cX = int(M['m10']/M['m00']) # With the moments, calculates the object's centroid
                cY = int(M['m01'] / M['m00'])

                x = int((cX / w_frame) * w_canvas)  # Because of differences in canvas and frame sizes,
                y = int((cY / h_frame) * h_canvas)  # it is needed to adjust the painting points

                cv2.circle(canvas, (x, y), parameters['radius'], parameters['color'], -1)  # Draws a filled circle

                if previous_point_canvas is not None:
                    cv2.line(canvas, previous_point_canvas, (x, y), parameters['color'], 2 * parameters['radius'])
                    # Draws a line
                if not args['draw_on_video']:
                    cv2.imshow(windows[3], canvas)
                elif args['draw_on_video']:
                    cv2.circle(canvas_frame, (cX, cY), parameters['radius'], parameters['color'], -1)
                    if previous_point_frame is not None:
                        cv2.line(canvas_frame, previous_point_frame, (cX, cY), parameters['color'],
                                 2 * parameters['radius'])

                previous_point_canvas = (x, y)
                previous_point_frame = (cX, cY)
            else:
                if args['use_shake_prevention']:
                    previous_point_canvas = None
                    previous_point_frame = None
                else:
                    previous_point_canvas = previous_point_canvas
                    previous_point_frame = previous_point_frame
        else:
            if args['use_shake_prevention']:
                previous_point_canvas = None
                previous_point_frame = None
            else:
                previous_point_canvas = previous_point_canvas
                previous_point_frame = previous_point_frame
            cv2.imshow(windows[2], frame_largest)

        if args['draw_on_video']:
            mask_frame = colormask(canvas_frame)
            frame_draw[mask_frame > 0] = canvas_frame[mask_frame > 0]
            cv2.imshow(windows[3], frame_draw)
        elif not args['draw_on_video']:
            cv2.imshow(windows[3], canvas)

        key = cv2.waitKey(1)  # keyboard command
        parameters = keyboardCommands(key, parameters, frame)
        if key == 113:  # Press 'q' to close the windows
            cv2.destroyAllWindows()
            break

    # <==============================================  KEYBOARD COMMANDS  =====================================>

def keyboardCommands(key, parameters, canvas):
    if key == 114:    # Press 'r' to paint red
        parameters['color'] = (0, 0, 255)
        print('Brush is now ' + Back.RED + ' red.' + Style.RESET_ALL)

    elif key == 103:  # Press 'g' to paint green
        parameters['color'] = (0, 255, 0)
        print('Brush is now ' + Back.GREEN + ' green.' + Style.RESET_ALL)

    elif key == 98:  # Press 'b' to paint blue
        parameters['color'] = (255, 0, 0)
        print('Brush is now ' + Back.BLUE + ' blue.' + Style.RESET_ALL)

    elif key == 43:  # Press '+' to get bigger radius
        parameters['radius'] += 1
        print('Brush size is now ' + str(parameters['radius']))

    elif key == 45:  # Press '-' to get smaller radius
        if parameters['radius'] > 1:
            parameters['radius'] -= 1
            print('Brush size is now ' + str(parameters['radius']))
    elif key == 99:  # Press 'c' to clear the window
        canvas = canvas.fill((255, 255, 255))
        print('You cleared the window.')

    elif key == 119:  # Press 'w' to write the drawn image
        cv2.imwrite('drawing ' + ctime() + '.png', canvas)
        print('You saved the drawing.')


    return parameters


    # <==================================================  RULES  =========================================>

def rules():
    print(Back.MAGENTA + 'RULES: ' + Style.RESET_ALL)
    print('Press ' + Fore.BLUE + 'b' + Style.RESET_ALL + ' to paint blue.')
    print('Press ' + Fore.GREEN + 'g' + Style.RESET_ALL + ' to paint green.')
    print('Press ' + Fore.RED + 'r' + Style.RESET_ALL + ' to paint red.')
    print('Press ' + Fore.YELLOW + '+' + Style.RESET_ALL + ' to get bigger radius.')
    print('Press ' + Fore.YELLOW + '-' + Style.RESET_ALL + ' to get smaller radius.')
    print('Press ' + Back.YELLOW + Fore.BLACK + 'C' + Style.RESET_ALL + ' to clear the window.')
    print('Press ' + Fore.LIGHTBLUE_EX + 'W' + Style.RESET_ALL + ' to write the drawn image.')
    print('Press ' + Back.RED + Fore.YELLOW + 'q' + Style.RESET_ALL + ' to close all windows.')


if __name__ == "__main__":
    main()

