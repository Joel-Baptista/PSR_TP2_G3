#!/usr/bin/python3
import copy
import math

import cv2
import numpy as np


def r_rect(event, x, y, flags, param):
    global mouse_coordinates
    mouse_coordinates = (x, y)


def drawFigure(coordinates, canvas, canvas_save, mode):
    if mode['figure'] == 'r':

        if mode['first'] and not mode['second']:
            canvas_save = cv2.rectangle(canvas_save, coordinates['1'], coordinates['mouse'], (255, 0, 0), 3)
        if mode['first'] and mode['second']:
            canvas = cv2.rectangle(canvas_save, coordinates['1'], coordinates['2'], (255, 0, 0), 3)
            mode['first'] = False
            mode['second'] = False

    elif mode['figure'] == 'o':

        if mode['first'] and not mode['second']:
            ix = coordinates['1'][0]
            x = coordinates['mouse'][0]
            iy = coordinates['1'][1]
            y = coordinates['mouse'][1]

            r = int(math.sqrt(((ix - x) ** 2) + ((iy - y) ** 2)))

            canvas_save = cv2.circle(canvas_save, coordinates['1'], r, (255, 0, 0), 3)

        if mode['first'] and mode['second']:

            ix = coordinates['1'][0]
            x = coordinates['2'][0]
            iy = coordinates['1'][1]
            y = coordinates['2'][1]

            r = int(math.sqrt(((ix - x) ** 2) + ((iy - y) ** 2)))

            canvas= cv2.circle(canvas_save, coordinates['1'], r, (255, 0, 0), 3)

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
                                      0, 360, (255, 0, 0), 3)

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
                                      0, 360, (255, 0, 0), 3)

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
                                      0, 360, (255, 0, 0), 3)

            mode['first'] = False
            mode['second'] = False
            mode['third'] = False

    return canvas, canvas_save, mode


def main():
    global mouse_coordinates
    mouse_coordinates = None

    coordinates = {'1': None, '2': None, '3': None, 'mouse': None}

    mode_square = {'first': False, 'second': False, 'figure': 'r'}
    mode_circle = {'first': False, 'second': False, 'figure': 'o'}
    mode_elipse = {'first': False, 'second': False, 'third': False, 'figure': 'e'}

    canvas = 255 * np.ones((1000, 1000, 3))
    canvas_draw = 255 * np.ones((1000, 1000, 3))

    cv2.namedWindow('image')
    cv2.setMouseCallback('image', r_rect)

    while True:
        coordinates['mouse'] = mouse_coordinates

        cond = (mode_square['first'] and not mode_square['second']) or \
               (mode_circle['first'] and not mode_circle['second']) or \
               (mode_elipse['first'] and not mode_elipse['second']) or \
               (mode_elipse['first'] and mode_elipse['second'] and not mode_elipse['third'])


        if cond:
            cv2.imshow('image', canvas_draw)
        else:
            cv2.imshow('image', canvas)

        canvas_draw = copy.deepcopy(canvas)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('r'):

            if not mode_square['first']:

                coordinates['1'] = coordinates['mouse']

                mode_square['first'] = True
                mode_circle['first'] = False
                mode_elipse['first'] = False

            elif mode_square['first'] and not mode_square['second']:

                coordinates['2'] = coordinates['mouse']
                mode_square['second'] = True

        elif k == ord('o'):

            if not mode_circle['first']:

                coordinates['1'] = coordinates['mouse']

                mode_circle['first'] = True
                mode_square['first'] = False
                mode_elipse['first'] = False

            elif mode_circle['first'] and not mode_circle['second']:
                coordinates['2'] = coordinates['mouse']
                mode_circle['second'] = True

        elif k == ord('e'):

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

        elif k == 113:
            break

        if mode_square['first']:
            canvas, canvas_draw, mode_square = \
                drawFigure(coordinates, canvas, canvas_draw, mode_square)

        if mode_circle['first']:
            canvas, canvas_draw, mode_circle = \
                drawFigure(coordinates, canvas, canvas_draw, mode_circle)

        if mode_elipse['first']:
            canvas, canvas_draw, mode_elipse = \
                drawFigure(coordinates, canvas, canvas_draw, mode_elipse)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()