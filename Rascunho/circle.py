#!/usr/bin/python3
import cv2
import numpy as np
import math

drawing = False  # Turns into true when is pressed
xi, yi = -1, -1
r = 0

def c_circle(event, x, y):
    global xi, yi, drawing, radius

    t = cv2.waitKey(1)

    if t != -1:
        if t == ord('c'):
            if event == cv2.EVENT_LBUTTONDOWN:
                drawing = True
                # we take note of where that mouse was located
                ix, iy = x, y

            elif event == cv2.EVENT_MOUSEMOVE:
                drawing == True

            elif event == cv2.EVENT_LBUTTONUP:
                r = int(math.sqrt(((xi - x) ** 2) + ((yi - y) ** 2)))
                cv2.circle(capture, (xi, yi), r, (0, 0, 255), thickness=1)
                drawing = False


# Create a black image
capture = cv2.VideoCapture(0)

# Name of the window
cv2.namedWindow('Frame')

cv2.setMouseCallback('Frame', c_circle)

while 1:
    _, frame = capture.read()

    if xi and yi:
        cv2.circle(frame, (xi, yi), r, (0, 0, 255), 1)

    cv2.imshow("Frame", frame)

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

capture.release()
cv2.destroyAllWindows()
