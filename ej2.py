import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)

fgbg = cv.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape
    centro_x = width // 2
    centro_y = height // 2

    fgmask = fgbg.apply(frame)
    
    fgmask = cv.medianBlur(fgmask, 5)
    
    _, fgmask = cv.threshold(fgmask, 200, 255, cv.THRESH_BINARY)

    # Revisar si hay movimiento en el pixel central (punto medio)
    if fgmask[centro_y, centro_x] == 255:
        cv.putText(frame, "Object Detected", (width - 250, height - 20), 
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Dibujar una pequeña cruz en el centro para referencia visual
    cv.line(frame, (centro_x - 10, centro_y), (centro_x + 10, centro_y), (0, 255, 0), 1)
    cv.line(frame, (centro_x, centro_y - 10), (centro_x, centro_y + 10), (0, 255, 0), 1)

    cv.imshow('Frame', frame)
    cv.imshow('Mascara', fgmask)

    if cv.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
