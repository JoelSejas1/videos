import cv2 as cv
import numpy as np
import os

image_path = 'videos/figuras.png'

if not os.path.exists(image_path):
    print("Error: No se encuentra figuras.png")
    exit()

img = cv.imread(image_path)
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
_, thresh = cv.threshold(gray, 240, 255, cv.THRESH_BINARY_INV)

contornos, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

for c in contornos:
    # 1. Detectar Forma
    epsilon = 0.04 * cv.arcLength(c, True)
    approx = cv.approxPolyDP(c, epsilon, True)
    
    x, y, w, h = cv.boundingRect(approx)
    forma = "Desconocido"
    vertices = len(approx)

    if vertices == 3:
        forma = "Triangulo"
    elif vertices == 4:
        aspect_ratio = float(w)/h
        forma = "Cuadrado" if aspect_ratio >= 0.95 and aspect_ratio <= 1.05 else "Rectangulo"
    elif vertices == 5:
        forma = "Pentagono"
    else:
        forma = "Circulo"

    # 2. Detectar Color
    # Tomamos una pequeña region interna para promediar el color
    mask = np.zeros(gray.shape, np.uint8)
    cv.drawContours(mask, [c], -1, 255, -1)
    color_medio = cv.mean(img, mask=mask)[:3]
    
    # Identificacion basica de color por componentes BGR
    b, g, r = color_medio
    if r > g and r > b:
        color_str = "Rojo"
    elif g > r and g > b:
        color_str = "Verde"
    elif b > r and b > g:
        color_str = "Azul"
    elif r > 200 and g > 200 and b < 100:
        color_str = "Amarillo"
    else:
        color_str = "Color"

    # 3. Mostrar resultados
    cv.drawContours(img, [c], -1, (0, 0, 0), 2)
    label = f"{forma} {color_str}"
    cv.putText(img, label, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

cv.imshow('Deteccion de Figuras y Colores', img)
cv.waitKey(0)
cv.destroyAllWindows()
