#!/usr/bin/python3
import cv2
import numpy as np
import math
drawing = False
p1 = None
p2 = None

def r_rect(event, x, y):
    global p1, p2, drawing
    # Keyboard commands
    choice = cv2.waitKey(1)

    if choice != -1:
        if choice == ord('r'):
            if event == cv2.EVENT_LBUTTONDOWN:
                if drawing is False:
                    drawing = True
                    p1 = (x, y)
                else:
                    drawing = False

            elif event == cv2.EVENT_MOUSEMOVE:
                if drawing is True:
                    p2 = (x, y)

capture = cv2.VideoCapture(0)

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", r_rect)

while True:
    _, frame = capture.read()

    if p1 and p2:
        cv2.rectangle(frame, p1, p2, (0, 255, 0))

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

capture.release()
cv2.destroyAllWindows()
