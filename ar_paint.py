#!/usr/bin/python3
import copy
from colorama import Fore, Back, Style
import cv2
from collections import deque
import argparse
import json
import numpy as np
import os
from datetime import datetime
from time import time, ctime, sleep
import math

# ----------------------------------------------------------------------------------------------------------------------
# Authors: Beatriz Borges, Joel Baptista, José Cozinheiro e Tiago Fonte
# Course: PSR
# Class: Aula 7
# Date: 17 Nov. 2021
# Description: Avaliação 2 (PSR Augmented Reality Paint) - ar_paint File
# ----------------------------------------------------------------------------------------------------------------------


def colormask(img):
    mask_R = cv2.inRange(img, (0, 0, 0), (0, 0, 255))
    mask_G = cv2.inRange(img, (0, 0, 0), (0, 255, 0))
    mask_B = cv2.inRange(img, (0, 0, 0), (255, 0, 0))

    mask = cv2.bitwise_or(mask_R, mask_G)
    mask = cv2.bitwise_or(mask, mask_B)

    return mask


def paintMode():
    parser = argparse.ArgumentParser(description="PSR AR Paint")
    parser.add_argument('-j', '--json', type=str, help='Path to JSON file (Uses limits.json by default)', default= 'limits.json')
    parser.add_argument('-usp',
                        '--use_shake_prevention',
                        help="Use Shake Detection",
                        action="store_true")

    parser.add_argument('-video',
                        '--draw_on_video',
                        help="Use Video Stream as Paint Screen",
                        action="store_true")

    parser.add_argument('-unp',
                        '--use_numeric_paint',
                        help="Use Numeric Paint",
                        action="store_true")
    parser.add_argument('-inp',
                        '--image_numeric_paint',
                        help="Path to Image on Numeric Paint Mode (No Effect without Use Numeric Paint Argument",
                        default='numeric_paint_images/pinguim.png')

    parser.add_argument('-mm',
                        '--mouse_mode',
                        help="Use Mouse to Paint",
                        action="store_true")

    parser.add_argument('-deluxe',
                        '--extra',
                        help="Try one of our Extra Functionalities on White Canvas Mode, have fun!",
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


def MouseCallBack(event, x, y, flags, param):
    global mouse_position, is_clicked
    mouse_position = (x, y)
    if event == cv2.EVENT_LBUTTONDOWN:
        is_clicked = True
    elif event == cv2.EVENT_MOUSEMOVE and is_clicked:
        is_clicked = True
    elif event == cv2.EVENT_LBUTTONUP:
        is_clicked = False


def colorDetection(image, parameters, centroid):

    B, G, R = cv2.split(image)
    mask = np.zeros(image.shape[:2])
    mask = cv2.circle(mask, centroid, 20, 255, -1)

    r = np.average(R[mask > 0])/255
    b = np.average(B[mask > 0])/255
    g = np.average(G[mask > 0])/255

    color = (b, g, r)

    parameters['color'] = color

    print('Brush is now ' + Back.GREEN + ' personalized color.' + Style.RESET_ALL)

    return parameters


def main():

    # <===========================================  INITIALIZATION  =========================================>

    print(Fore.RED + "\nPSR " + Style.RESET_ALL +
          'Augmented Reality Paint, Beatriz Borges, Joel Baptista, José Cozinheiro, Tiago Fonte, November 2021\n')

    parameters = {'color': (0, 0, 255), 'radius': 5}
    previous_point_canvas = None
    previous_point_frame = None

    global mouse_coordinates
    mouse_coordinates = None

    global mouse_position
    mouse_position = (0, 0)

    global is_clicked
    is_clicked = False

    coordinates = {'1': None, '2': None, '3': None, 'mouse': None}

    mode_square = {'first': False, 'second': False, 'figure': 's'}
    mode_circle = {'first': False, 'second': False, 'figure': 'o'}
    mode_elipse = {'first': False, 'second': False, 'third': False, 'figure': 'e'}

    key = -1

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    # <======================================  GET LIMITS ON JSON FILE  ====================================>

    args = paintMode()

    lim_R, lim_G, lim_B = JsonReader(args['json'])

    # <======================================  MODES INFO ==================================================>

    if args['use_shake_prevention']:
        print('\nYou are using ' + Fore.CYAN + 'Shaking Prevention Mode' + Fore.RESET)

    if args['draw_on_video']:
        print('\nYou are using ' + Fore.CYAN + 'Stream on Video Mode' + Fore.RESET)

    if args['use_numeric_paint']:
        print('\nYou are using ' + Fore.CYAN + 'Numeric Paint Mode' + Fore.RESET)
        print('Index 1 must be Paint with ' + Back.RED + 'Red' + Back.RESET + ' Color')
        print('Index 2 must be Paint with ' + Back.GREEN + 'Green' + Back.RESET + ' Color')
        print('Index 3 must be Paint with ' + Back.BLUE + 'Blue' + Back.RESET + ' Color')
        print('Index 4 must be Paint with ' + Back.WHITE + 'White' + Back.RESET + ' Color')

    rules()

    if args['draw_on_video'] and args['use_numeric_paint']:
        print('\n' + 'Numeric paint not supported')
    # <===========================================  VIDEO CAPTURE  =========================================>

    capture = cv2.VideoCapture(0)
    _, frame = capture.read()

    windows = ['Camera', 'Segmented image', 'Largest Component', 'Canvas']
    positions = [(0, 0), (0, 600), (650, 0), (850, 0)]

    if args['use_numeric_paint']:
        path = args['image_numeric_paint']
        canvas = cv2.imread(path, cv2.IMREAD_COLOR)
    else:
        canvas = 255 * np.ones((1000, 1000, 3))
        if args['extra']:
            paint = cv2.rectangle(canvas, (100, 30), (225, 135), (0, 0, 0), 2)
            paint = cv2.rectangle(canvas, (325, 30), (450, 135), colors[0], -1)
            paint = cv2.rectangle(canvas, (550, 30), (675, 135), colors[1], -1)
            paint = cv2.rectangle(canvas, (775, 30), (900, 135), colors[2], -1)
            cv2.putText(paint, "CLEAR ALL", (120, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(paint, "BLUE", (360, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(paint, "GREEN", (585, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(paint, "RED", (820, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            canvas_original = copy.deepcopy(canvas)

    canvas_frame = 255 * np.ones(frame.shape)
    h_canvas, w_canvas, _ = canvas.shape
    h_frame, w_frame, _ = frame.shape

    if not args['draw_on_video']:
        initial_draw = copy.deepcopy(canvas)
    else:
        initial_draw = np.ones(frame.shape) * 255

    for window, position in zip(windows, positions): # Showing and positioning windows
        cv2.namedWindow(window)
        cv2.moveWindow(window, position[0], position[1])

    kernel = np.ones((2, 2), np.uint8) # for pre-processing images
    cv2.imshow(windows[3], canvas)

    # mouse call back

    if args['mouse_mode']:
        cv2.setMouseCallback(windows[3], MouseCallBack)
    else:
        is_clicked = True

    while True:

        # <===========================================  FRAME CAPTURE  ===========================================>

        _, frame = capture.read()

        frame_GUI = copy.deepcopy(frame)
        frame_GUI = cv2.flip(frame_GUI, 1)
        frame_largest = np.zeros(frame.shape)
        frame_draw = copy.deepcopy(frame_GUI)

    # <=============================================  SEGMENTATION  ===========================================>

        mask = cv2.inRange(frame_GUI, (lim_B['min'], lim_G['min'], lim_R['min']),
            (lim_B['max'], lim_G['max'], lim_R['max']))

    # <============================================  PRE-PROCESSING  ===========================================>

        mask_dilation = cv2.dilate(mask, kernel, iterations=2)
        mask_closing = cv2.morphologyEx(mask_dilation, cv2.MORPH_CLOSE, kernel)

        cv2.imshow(windows[1], mask_closing)

    # <========================================  FINDING CELLPHONE SCREEN  =====================================>

        contours, hierarchy = cv2.findContours(mask_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if args['mouse_mode']:
            contours_len = 1
        else:
            contours_len = len(contours)

        if contours_len > 0: # Finds contour with maximum area and draws it on window "Largest Component"
            if is_clicked:
                if args['mouse_mode']:
                    area_condition = 400
                else:
                    area = max(contours, key=cv2.contourArea)
                    area_condition = cv2.contourArea(area)

                    areas = [cv2.contourArea(c) for c in contours]
                    max_index = np.argmax(areas)
                    cnt_max = contours[max_index]
                    mask_largest = cv2.fillPoly(frame_largest, pts=[cnt_max], color=(255, 255, 255))
                    cv2.imshow(windows[2], mask_largest)


    # <=============================================  CANVAS DRAWING  =========================================>

                if area_condition > 350:  # Area must be at least 350 pixels
                    if args['mouse_mode']:
                        cX = 0
                        x = mouse_position[0]
                        cY = 0
                        y = mouse_position[1]
                    else:
                        M = cv2.moments(cnt_max)  # Finds the object's moments
                        cX = int(M['m10'] / M['m00'])  # With the moments, calculates the object's centroid
                        cY = int(M['m01'] / M['m00'])

                        x = int((cX / w_frame) * w_canvas)  # Because of differences in canvas and frame sizes,
                        y = int((cY / h_frame) * h_canvas)  # it is needed to adjust the painting points

                    cv2.add(frame_GUI, (-10, 60, -10, 0), dst=frame_GUI, mask=mask)
                    cv2.putText(frame_GUI, '+', (cX - 15, cY + 8), cv2.FONT_HERSHEY_SIMPLEX, 1, parameters['color'], 2)
                    cv2.imshow(windows[0], frame_GUI)

                    if key == 112 and not args['draw_on_video']:  # Press 'p' to paint personalized color
                        parameters = colorDetection(frame_GUI, parameters, (cX, cY))

                    if args['use_shake_prevention']:
                        if args['draw_on_video'] and previous_point_frame is not None:
                            dist = math.sqrt((previous_point_frame[0] - cX) ** 2 + (previous_point_frame[1] - cY) ** 2)
                            if dist > 75:
                                previous_point_frame = None
                        if not args['draw_on_video'] and previous_point_canvas is not None:
                            dist = math.sqrt((previous_point_canvas[0] - x) ** 2 + (previous_point_canvas[1] - y) ** 2)
                            if dist > 150:
                                previous_point_canvas = None

                    center = (x, y)

                    if args['extra']:
                        if 30 <= center[1] <= 135:
                            if 100 <= center[0] <= 225:
                                canvas = copy.deepcopy(canvas_original)
                                print('<=======You cleared the window===========>')
                            elif 330 <= center[0] <= 450:
                                parameters['color'] = (255, 0, 0)
                                print('Brush is now ' + Back.BLUE + ' blue.' + Style.RESET_ALL)
                            elif 550 <= center[0] <= 675:
                                parameters['color'] = (0, 255, 0)
                                print('Brush is now ' + Back.GREEN + ' green.' + Style.RESET_ALL)
                            elif 775 <= center[0] <= 900:
                                parameters['color'] = (0, 0, 255)
                                print('Brush is now ' + Back.RED + ' red.' + Style.RESET_ALL)

                    cond = (mode_square['first'] and not mode_square['second']) or \
                           (mode_circle['first'] and not mode_circle['second']) or \
                           (mode_elipse['first'] and not mode_elipse['second']) or \
                           (mode_elipse['first'] and mode_elipse['second'] and not mode_elipse['third']) or \
                           (key == 115) or (key == 111) or (key == 101) # key = 's' or 'e' or 'o'

                    if not cond:

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
                        previous_point_canvas = None
                        previous_point_frame = None

                        if not args['draw_on_video']:
                            if cond:
                                cv2.imshow(windows[3], initial_draw)
                            coordinates['mouse'] = (x, y)
                            final_draw = copy.deepcopy(canvas)
                            initial_draw = copy.deepcopy(canvas)
                        else:
                            if cond:
                                frame_aux = copy.deepcopy(frame_draw)
                                mask_frame = colormask(initial_draw)
                                frame_aux[mask_frame > 0] = initial_draw[mask_frame > 0]
                                cv2.imshow(windows[3], frame_aux)

                            coordinates['mouse'] = (cX, cY)
                            final_draw = copy.deepcopy(canvas_frame)
                            initial_draw = copy.deepcopy(canvas_frame)

                        if key == ord('s'):

                            print("\nYou draw a square.")

                            if not mode_square['first']:

                                coordinates['1'] = coordinates['mouse']

                                mode_square['first'] = True
                                mode_circle['first'] = False
                                mode_elipse['first'] = False

                            elif mode_square['first'] and not mode_square['second']:

                                coordinates['2'] = coordinates['mouse']
                                mode_square['second'] = True

                        elif key == ord('o'):

                            print("\nYou draw a circle.")

                            if not mode_circle['first']:

                                coordinates['1'] = coordinates['mouse']

                                mode_circle['first'] = True
                                mode_square['first'] = False
                                mode_elipse['first'] = False

                            elif mode_circle['first'] and not mode_circle['second']:
                                coordinates['2'] = coordinates['mouse']
                                mode_circle['second'] = True

                        elif key == ord('e'):

                            print("\nYou draw an elipse.")

                            if not mode_elipse['first']:

                                coordinates['1'] = coordinates['mouse']

                                mode_elipse['first'] = True
                                mode_square['first'] = False
                                mode_circle['first'] = False

                            elif mode_elipse['first'] and not mode_elipse['second']:
                                coordinates['2'] = coordinates['mouse']
                                mode_elipse['second'] = True

                            elif mode_elipse['first'] and mode_elipse['second'] and not mode_elipse['third']:
                                coordinates['3'] = coordinates['mouse']
                                mode_elipse['third'] = True

                        if mode_square['first']:
                            final_draw, initial_draw, mode_square = \
                                drawFigure(coordinates, final_draw, initial_draw, mode_square, parameters['color'], 2*parameters['radius'])

                        if mode_circle['first']:
                            final_draw, initial_draw, mode_circle = \
                                drawFigure(coordinates, final_draw, initial_draw, mode_circle, parameters['color'], 2*parameters['radius'])

                        if mode_elipse['first']:
                            final_draw, initial_draw, mode_elipse = \
                                drawFigure(coordinates, final_draw, initial_draw, mode_elipse, parameters['color'], 2*parameters['radius'])

                        if not (mode_square['first'] or mode_circle['first'] or mode_elipse['first']):
                            if not args['draw_on_video']:
                                canvas = copy.deepcopy(final_draw)
                            else:
                                canvas_frame = copy.deepcopy(final_draw)
                else:
                    cv2.imshow(windows[0], frame_GUI)

        else:
            cv2.imshow(windows[2], frame_largest)
            cv2.imshow(windows[0], frame_GUI)

        cv2.imshow(windows[0], frame_GUI)
        key = cv2.waitKey(1)  # keyboard command

        if args['draw_on_video']:
            mask_frame = colormask(canvas_frame)
            frame_draw[mask_frame > 0] = canvas_frame[mask_frame > 0]
            cv2.imshow(windows[3], frame_draw)
            parameters, canvas_frame, previous_point_frame = \
                keyboardCommands(key, parameters, canvas_frame, frame_draw, previous_point_frame, args)
        elif not args['draw_on_video']:
            cv2.imshow(windows[3], canvas)
            parameters, canvas, previous_point_canvas = \
                keyboardCommands(key, parameters, canvas, canvas, previous_point_canvas, args)

        if key == 113 or key == 81:  # Press 'q' to close the windows
            print("\nExiting Program.")
            cv2.destroyAllWindows()
            break

    # <==============================================  KEYBOARD COMMANDS  =====================================>


def keyboardCommands(key, parameters, canvas, image, previous_point, args):
    if key == 114 or key == 82:    # Press 'r' to paint red
        parameters['color'] = (0, 0, 255)
        print('Brush is now ' + Back.RED + 'red.' + Style.RESET_ALL)

    elif key == 103 or key == 71:  # Press 'g' to paint green
        parameters['color'] = (0, 255, 0)
        print('Brush is now ' + Back.GREEN + 'green.' + Style.RESET_ALL)

    elif key == 98 or key == 66:  # Press 'b' to paint blue
        parameters['color'] = (255, 0, 0)
        print('Brush is now ' + Back.BLUE + 'blue.' + Style.RESET_ALL)

    elif key == 43:  # Press '+' to get bigger radius
        parameters['radius'] += 1
        print('Brush size is now ' + str(parameters['radius']))

    elif key == 45:  # Press '-' to get smaller radius
        if parameters['radius'] > 1:
            parameters['radius'] -= 1
            print('Brush size is now ' + str(parameters['radius']))

    elif key == 120 or key == 88:   # Press 'x' to erase lines
        parameters['color'] = (255, 255, 255)
        print('You are now using the eraser')

    elif key == 99 or key == 67:  # Press 'c' to clear the window
        if args['use_numeric_paint']:
            path = args['image_numeric_paint']
            canvas = cv2.imread(path, cv2.IMREAD_COLOR)
        else:
            if args['draw_on_video']:
                canvas = 255 * np.ones(image.shape)
            else:
                canvas = 255 * np.ones((1000, 1000, 3))
        print('<=======You cleared the window===========>')
        previous_point = None

    elif key == 119 or key == 87:  # Press 'w' to write the drawn image
        today = datetime.now()
        try:
            os.makedirs('Drawings/' + today.strftime('%d %m %Y'))
            print("\nToday's Directory Created")
        except FileExistsError:
            print("\nToday's Directory already exists")
        path = ('Drawings/' + today.strftime('%d %m %Y'))

        cv2.imwrite(os.path.join(path, 'drawing ' + ctime() + '.png'), image)
        print('You saved the drawing.')

    return parameters, canvas, previous_point

    # <==================================================  RULES  =========================================>

def rules():
    print('\n' + Back.MAGENTA + 'RULES: ' + Style.RESET_ALL)
    print('Press ' + Fore.BLUE + 'b or B' + Style.RESET_ALL + ' to paint blue.')
    print('Press ' + Fore.GREEN + 'g or G' + Style.RESET_ALL + ' to paint green.')
    print('Press ' + Fore.RED + 'r or R' + Style.RESET_ALL + ' to paint red.')
    print('Press ' + Fore.WHITE + 'p or P' + Style.RESET_ALL + ' to paint screen color.')
    print('Press ' + Fore.YELLOW + '+' + Style.RESET_ALL + ' to get bigger radius.')
    print('Press ' + Fore.YELLOW + '-' + Style.RESET_ALL + ' to get smaller radius.')
    print('Press ' + Fore.YELLOW + 'x or X' + Style.RESET_ALL + ' to erase.')
    print('Press ' + Back.YELLOW + 'c or C' + Style.RESET_ALL + ' to clear the window.')
    print('Press ' + Fore.LIGHTBLUE_EX + 'w or W' + Style.RESET_ALL + ' to write/save the drawn image'
                                                                      '(Drawings Directory.')
    print('Press ' + Back.CYAN + 'e or E' + Style.RESET_ALL + ' to draw an Elipse (2 clicks).')
    print('Press ' + Back.CYAN + 'o or O' + Style.RESET_ALL + ' to draw a Circle (1 click).')
    print('Press ' + Back.CYAN + 's or S' + Style.RESET_ALL + ' to draw a Square (1 click).\n')


def drawFigure(coordinates, canvas, canvas_save, mode, color, thinkness):
    if mode['figure'] == 's':

        if mode['first'] and not mode['second']:
            canvas_save = cv2.rectangle(canvas_save, coordinates['1'], coordinates['mouse'], color, thinkness)
        if mode['first'] and mode['second']:
            canvas = cv2.rectangle(canvas_save, coordinates['1'], coordinates['2'], color, thinkness)
            mode['first'] = False
            mode['second'] = False

    elif mode['figure'] == 'o':

        if mode['first'] and not mode['second']:
            ix = coordinates['1'][0]
            x = coordinates['mouse'][0]
            iy = coordinates['1'][1]
            y = coordinates['mouse'][1]

            r = int(math.sqrt(((ix - x) ** 2) + ((iy - y) ** 2)))

            canvas_save = cv2.circle(canvas_save, coordinates['1'], r, color, thinkness)

        if mode['first'] and mode['second']:

            ix = coordinates['1'][0]
            x = coordinates['2'][0]
            iy = coordinates['1'][1]
            y = coordinates['2'][1]

            r = int(math.sqrt(((ix - x) ** 2) + ((iy - y) ** 2)))

            canvas = cv2.circle(canvas_save, coordinates['1'], r, color, thinkness)

            mode['first'] = False
            mode['second'] = False

    elif mode['figure'] == 'e':

        if mode['first'] and not mode['second'] and not mode['third']:
            x1 = coordinates['1'][0]
            y1 = coordinates['1'][1]

            x2 = coordinates['mouse'][0]
            y2 = coordinates['mouse'][1]

            axesLength = (abs(x1 - x2), abs(y1 - y2))

            canvas_save = cv2.ellipse(canvas_save, coordinates['1'], axesLength, 0,
                                      0, 360, color, thinkness)

        if mode['first'] and mode['second'] and not mode['third']:
            x1 = coordinates['1'][0]
            y1 = coordinates['1'][1]

            x2 = coordinates['2'][0]
            y2 = coordinates['2'][1]

            x3 = coordinates['mouse'][0]
            y3 = coordinates['mouse'][1]

            axesLength = (abs(x1 - x2), abs(y1 - y2))

            if (x1 - x3) != 0:
                angle = np.arctan((y1 - y3)/(x1 - x3)) * (180/math.pi)
            else:
                angle = 90

            canvas_save = cv2.ellipse(canvas_save, coordinates['1'], axesLength, angle,
                                      0, 360, color, thinkness)

        if mode['first'] and mode['second'] and mode['third']:
            x1 = coordinates['1'][0]
            y1 = coordinates['1'][1]

            x2 = coordinates['2'][0]
            y2 = coordinates['2'][1]

            x3 = coordinates['3'][0]
            y3 = coordinates['3'][1]

            axesLength = (abs(x1 - x2), abs(y1 - y2))

            if (x1 - x3) != 0:
                angle = np.arctan((y1 - y3) / (x1 - x3)) * (180 / math.pi)
            else:
                angle = 90

            canvas = cv2.ellipse(canvas_save, coordinates['1'], axesLength, angle,
                                      0, 360, color, thinkness)

            mode['first'] = False
            mode['second'] = False
            mode['third'] = False

    return canvas, canvas_save, mode


if __name__ == "__main__":
    main()
