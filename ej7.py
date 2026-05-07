import cv2 as cv
import numpy as np
import serial
import RPi.GPIO as GPIO

# Configuracion de LEDs en Raspberry
LED1 = 17 
LED2 = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup([LED1, LED2], GPIO.OUT)

try:
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
except:
    print("Error UART")

cap = cv.VideoCapture(0)
fgbg = cv.createBackgroundSubtractorMOG2(varThreshold=50)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv.flip(frame, 1)
    width = frame.shape[1]
    tercio = width // 3

    mask = fgbg.apply(frame)
    mask = cv.medianBlur(mask, 5)
    contornos, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    # Filtrar contornos por area
    objetos_validos = [c for c in contornos if cv.contourArea(c) > 2000]
    num_objetos = len(objetos_validos)

    # Control de LEDs segun cantidad de objetos
    GPIO.output(LED1, num_objetos >= 1)
    GPIO.output(LED2, num_objetos >= 2)

    if num_objetos == 0:
        # MODO BUSQUEDA: Giro lento
        ser.write(b'buscar\n')
        cv.putText(frame, "Buscando...", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        # Seguimiento del objeto mas grande
        c = max(objetos_validos, key=cv.contourArea)
        M = cv.moments(c)
        cx = int(M["m10"] / M["m00"])
        
        cv.drawContours(frame, [c], -1, (0, 255, 0), 2)

        if cx < tercio:
            ser.write(b'izq\n')
        elif cx > tercio * 2:
            ser.write(b'der\n')
        else:
            ser.write(b'fwd\n')

    cv.imshow('Final Lab 9', frame)
    if cv.waitKey(30) & 0xFF == ord('q'): break

cap.release()
GPIO.cleanup()
ser.close()
