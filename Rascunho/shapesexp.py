#!/usr/bin/python3
import math

import cv2
import numpy as np

drawing = False # true if mouse is pressed
mode1 = False # if True, draw rectangle. Press 'r' to toggle to curve
mode2 = False # if True, draw circle. Press 'c' to toggle to curve
ix, iy = -1, -1

# def c_circle(event, x, y, flags, param):
#
#     global ix, iy, drawing, mode2
#
#     if event == cv2.EVENT_LBUTTONDOWN:
#         drawing = True
#         ix, iy = x, y
#
#     elif event == cv2.EVENT_MOUSEMOVE:
#         if drawing == True:
#             if mode2 == True:
#                 cv2.circle(canvas, (x, y), 5, (0, 0, 255), -1)
#             else:
#                 cv2.rectangle(canvas, (ix, iy), (x, y), (255, 0, 0), -1)
#
#     elif event == cv2.EVENT_LBUTTONUP:
#         drawing = False
#         if mode2 == True:
#             cv2.circle(canvas, (x, y), 5, (0, 0, 255), -1)
#         else:
#             cv2.rectangle(canvas, (ix, iy), (x, y), (255, 0, 0), -1)


def r_rect(event, x, y, flags, param):
    global ix,iy,drawing,mode1
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            if mode1 == True:
                cv2.rectangle(canvas, (ix, iy), (x, y), (255, 0, 0), -1)
            else:
                r = int(math.sqrt(((ix - x) ** 2) + ((iy - y) ** 2)))
                cv2.circle(canvas, (ix, iy), r, (0, 0, 255), -1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode1 == True:
            cv2.rectangle(canvas, (ix, iy), (x, y), (255, 0, 0), -1)
        else:
            r = int(math.sqrt(((ix - x) ** 2) + ((iy - y) ** 2)))
            cv2.circle(canvas, (ix, iy), r, (0, 0, 255), -1)

canvas = 255 * np.ones((1000, 1000, 3))
cv2.namedWindow('image')
cv2.setMouseCallback('image', r_rect)

while(1):
    cv2.imshow('image', canvas)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('r'):
        mode1 = not mode1
    # elif k == ord('c'):
    #     mode2 = not mode2
    elif k == 113:
        break

cv2.destroyAllWindows()