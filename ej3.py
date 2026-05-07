import cv2 as cv
import numpy as np
import os

video_path = 'videos/bouncing.mp4.mp4'

if not os.path.exists(video_path):
    print(f"Error: No se encuentra {video_path}")
    exit()

cap = cv.VideoCapture(video_path)

# Sustractor para detectar el movimiento
fgbg = cv.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. Obtener la máscara de movimiento
    fgmask = fgbg.apply(frame)

    # 2. Limpieza de ruido (Teoria: Blur filters para mejorar deteccion de bordes) [cite: 4]
    fgmask = cv.medianBlur(fgmask, 5)
    _, fgmask = cv.threshold(fgmask, 200, 255, cv.THRESH_BINARY)

    # 3. Encontrar contornos en la máscara 
    contornos, _ = cv.findContours(fgmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # 4. Dibujar los contornos sobre el frame original 
    for c in contornos:
        if cv.contourArea(c) > 500: # Filtro para ignorar ruidos muy pequeños
            cv.drawContours(frame, [c], -1, (0, 255, 0), 2)

    cv.imshow('Objeto en Movimiento - Contornos', frame)
    cv.imshow('Mascara Binaria', fgmask)

    if cv.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
