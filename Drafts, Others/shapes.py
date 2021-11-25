#!/usr/bin/python3
import cv2
import numpy as np
import math
import colorama
from colorama import Fore, Back, Style

drawing = False
xi, yi = -1, -1
r = 0
p1 = None
p2 = None
def r_rect(event, x, y, flags, params):
    global p1, p2, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        p1 = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        drawing = True
        p2 = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        #cv2.rectangle(canvas, (xi, yi), (x, y), (0, 255, 0), -1)

def c_circle(event, x, y, canvas):
    global xi, yi, drawing, r

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        xi, yi = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        drawing = True

    elif event == cv2.EVENT_LBUTTONUP:
        r = int(math.sqrt(((xi - x) ** 2) + ((yi - y) ** 2)))
        #cv2.circle(canvas, (xi, yi), r, (0, 0, 255), thickness=1)
        drawing = False

    return canvas


canvas = 255 * np.ones((1000, 1000, 3))
cv2.imshow('Frame', canvas)



while True:
    t = cv2.waitKey(1)
    if t != -1:
        if t == ord('r'):
            cv2.setMouseCallback("Frame", r_rect)
        elif t == ord('c'):

            canvas = cv2.setMouseCallback('Frame', c_circle)
    if p1 and p2:
        cv2.rectangle(canvas, p1, p2, (0, 255, 0))
    if xi and yi:
        cv2.circle(canvas, (xi, yi), r, (0, 0, 255), 1)

    cv2.imshow("Frame", canvas)

    key = cv2.waitKey(10)
    if key == 113:
        print(Back.LIGHTYELLOW_EX + Fore.BLACK + 'You pressed "q" so you quit the program.'+ Style.RESET_ALL)

        break


cv2.destroyAllWindows()