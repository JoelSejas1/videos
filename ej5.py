import cv2 as cv
import numpy as np
import serial
import time

# Configuracion UART para comunicacion con Tiva
try:
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
except:
    print("Error conectando con Tiva")

cap = cv.VideoCapture(0)
fgbg = cv.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.flip(frame, 1) # Espejo para facilitar direccion
    height, width, _ = frame.shape
    tercio = width // 3 # Dividimos la pantalla en 3 zonas

    fgmask = fgbg.apply(frame)
    fgmask = cv.medianBlur(fgmask, 5)
    _, fgmask = cv.threshold(fgmask, 200, 255, cv.THRESH_BINARY)

    contornos, _ = cv.findContours(fgmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    for c in contornos:
        if cv.contourArea(c) > 2000:
            M = cv.moments(c)
            if M["m00"] != 0:
                # Centro del objeto
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                cv.circle(frame, (cx, cy), 10, (0, 0, 255), -1)

                # Logica de movimiento segun la posicion X
                if cx < tercio:
                    print("Izquierda")
                    ser.write(b'motor1\n') # Solo motor 1 para girar
                elif cx > tercio * 2:
                    print("Derecha")
                    ser.write(b'motor2\n') # Solo motor 2 para girar
                else:
                    print("Centro - Avanzar")
                    ser.write(b'motor1\n')
                    ser.write(b'motor2\n')
            break # Seguir solo al primer objeto grande detectado

    cv.line(frame, (tercio, 0), (tercio, height), (255, 0, 0), 2)
    cv.line(frame, (tercio*2, 0), (tercio*2, height), (255, 0, 0), 2)
    
    cv.imshow('Tracker', frame)
    if cv.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
ser.close()
