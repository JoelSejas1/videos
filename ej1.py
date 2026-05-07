import cv2 as cv
import numpy as np
import os

video_path = 'videos/bouncing.mp4.mp4'

if not os.path.exists(video_path):
    print(f"Error: El archivo {video_path} no existe en esta carpeta.")
    exit()

cap = cv.VideoCapture(video_path)

fgbg_mog2 = cv.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
fgbg_knn = cv.createBackgroundSubtractorKNN(history=500, dist2Threshold=400.0, detectShadows=True)

if not cap.isOpened():
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    fgmask_mog2 = fgbg_mog2.apply(frame)
    fgmask_knn = fgbg_knn.apply(frame)

    fgmask_mog2 = cv.medianBlur(fgmask_mog2, 5)

    cv.imshow('Original', frame)
    cv.imshow('MOG2', fgmask_mog2)
    cv.imshow('KNN', fgmask_knn)

    if cv.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
