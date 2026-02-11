import cv2
import os

# Configuración
nombre_producto = "aproducto20"
nombre ="aproducto20.MOV"
video_path = f"mega/{nombre}"
output_folder = f"dataset/{nombre_producto}"

os.makedirs(output_folder, exist_ok=True)
cap = cv2.VideoCapture(video_path)
count = 0
frame_rate = 15 # Guardar 1 foto cada 10 frames

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    if count % frame_rate == 0:
        # Guardamos la imagen
        filename = f"{output_folder}/{nombre_producto}_{count}.jpg"
        cv2.imwrite(filename, frame)
    count += 1

cap.release()
print(f" ¡Listo! Imágenes extraídas en {output_folder}")