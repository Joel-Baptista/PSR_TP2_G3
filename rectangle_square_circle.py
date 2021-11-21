#!/usr/bin/python3
import cv2
import numpy as np
import math

drawing = False
xi, yi = -1, -1
r = 0
p1 = None
p2 = None
t = cv2.waitKey(1)

def r_rect(event, x, y):
    global p1, p2, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        if drawing is False:
            drawing = True
            p1 = (x, y)
        else:
            drawing = False

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing is True:
            p2 = (x, y)

def c_circle(event, x, y):
    global xi, yi, drawing, r

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        # we take note of where that mouse was located
        xi, yi = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        drawing == True

    elif event == cv2.EVENT_LBUTTONUP:
        r = int(math.sqrt(((xi - x) ** 2) + ((yi - y) ** 2)))
        cv2.circle(capture, (xi, yi), r, (0, 0, 255), thickness=1)
        drawing = False


capture = cv2.VideoCapture(0)
cv2.namedWindow("Frame")
if t != -1:
    if t == ord('r'):
        cv2.setMouseCallback("Frame", r_rect)
    elif t == ord('c'):
        # Connects the mouse button to our callback function
        cv2.setMouseCallback('Frame', c_circle)

while True:
    _, frame = capture.read()

    if p1 and p2:
        cv2.rectangle(frame, p1, p2, (0, 255, 0))
    if xi and yi:
        cv2.circle(frame, (xi, yi), r, (0, 0, 255), 1)

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(10)
    if key == 27:
        break

capture.release()
cv2.destroyAllWindows()