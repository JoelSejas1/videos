import cv2 as cv
import numpy as np
import os

image_path = 'videos/monedas_2.jpg'

if not os.path.exists(image_path):
    exit()

img = cv.imread(image_path)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Desenfoque moderado para no perder el borde real [cite: 10, 22]
blur = cv.GaussianBlur(gray, (13, 13), 0)

# Canny con umbral mas bajo para capturar mejor el borde [cite: 41, 44]
edges = cv.Canny(blur, 30, 150)

# Cerrar el contorno para que sea una sola linea solida
kernel = np.ones((5, 5), np.uint8)
closed = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel)

contornos, _ = cv.findContours(closed.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

count = 0
for c in contornos:
    area = cv.contourArea(c)
    # Ajuste de area: si no detecta nada, baja este valor a 500
    if area > 900:
        cv.drawContours(img, [c], -1, (0, 255, 0), 3)
        count += 1

# Texto mas grande y en una posicion mas visible
print(f"Monedas detectadas: {count}")
cv.putText(img, f"Conteo: {count}", (50, 100), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

cv.imshow('Resultado', img)
cv.imshow('Bordes', closed)
cv.waitKey(0)
cv.destroyAllWindows()
