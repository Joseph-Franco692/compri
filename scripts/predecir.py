import tensorflow as tf
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import os
import random
import matplotlib.pyplot as plt
import csv
import textwrap # Para que el texto largo no se salga de la imagen

# --- CONFIGURACIÓN ---
DATASET_DIR = 'dataset'
CSV_FILE = 'catalogo_productos_unico.csv' # Asegúrate de que este archivo existe

# --- 1. CARGAR RECURSOS Y CSV ---
print(" Cargando recursos...")

# A. Cargar Modelo
try:
    if os.path.exists('mi_modelo_pro.keras'):
        model = tf.keras.models.load_model('mi_modelo_pro.keras')
    elif os.path.exists('mi_modelo.keras'):
        model = tf.keras.models.load_model('mi_modelo.keras')
    else:
        raise FileNotFoundError("No hay modelo .keras")

    # B. Cargar Nombres de Clases
    with open('clases.txt', 'r') as f:
        class_names = [line.strip() for line in f.readlines()]

    # C. Cargar Catálogo (CSV) en memoria
    catalogo_info = {}
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # TRUCO: Usamos la ruta de la imagen para identificar la clase
                # Ejemplo ruta: dataset/Sardina_Real/foto.jpg
                # Extraemos "Sardina_Real"
                ruta = row['Imagen_Referencia'] # o 'Ruta_Imagen' según tu csv
                if ruta and '/' in ruta:
                    partes = ruta.split('/')
                    # Asumimos estructura dataset/CLASE/foto
                    if len(partes) >= 2:
                        nombre_carpeta = partes[1] 
                        catalogo_info[nombre_carpeta] = row
    else:
        print(" ADVERTENCIA: No encontré el archivo CSV. Solo mostraré predicciones básicas.")

except Exception as e:
    print(f" Error cargando recursos: {e}")
    exit()

def mostrar_resultado_con_datos(img_input, clase_detectada, valor_confianza):
    """
    Muestra la imagen y le pega los datos del CSV abajo
    """
    # Buscar info en el catálogo cargado
    info = catalogo_info.get(clase_detectada)
    
    plt.figure(figsize=(12, 7)) # Hacemos la imagen un poco más grande

    # --- 1. IMAGEN DEL USUARIO ---
    plt.subplot(1, 2, 1)
    plt.imshow(img_input)
    plt.title(f"TU FOTO\nConfianza: {valor_confianza:.1f}%", fontsize=10)
    plt.axis('off')

    # --- 2. IMAGEN DE REFERENCIA (DATASET) ---
    plt.subplot(1, 2, 2)
    ruta_clase = os.path.join(DATASET_DIR, clase_detectada)
    
    if os.path.exists(ruta_clase):
        fotos = [f for f in os.listdir(ruta_clase) if f.lower().endswith(('jpg', 'png', 'jpeg', 'webp'))]
        if fotos:
            img_ref = Image.open(os.path.join(ruta_clase, random.choice(fotos)))
            plt.imshow(img_ref)
            plt.title(f"MATCH: {clase_detectada}", color='green', fontsize=12, weight='bold')
        else:
            plt.text(0.5, 0.5, "Carpeta vacía", ha='center')
    else:
        plt.text(0.5, 0.5, "Sin referencia", ha='center')
    plt.axis('off')

    # --- 3. TEXTO INFORMATIVO DEL CSV (Parte inferior) ---
    if info:
        texto_info = (
            f" PRODUCTO: {info.get('Nombre', 'N/A')}\n"
            f" PRECIO: ${info.get('Precio', '0.00')}\n"
            f" UBICACIÓN: {info.get('Ubicacion', 'N/A')}\n"
            f" DESCRIPCIÓN: {textwrap.fill(info.get('Descripcion', ''), width=80)}" 
        )
        color_texto = 'black'
        caja_color = '#f0f0f0' # Gris clarito
    else:
        texto_info = f" No hay información en el CSV para: {clase_detectada}"
        color_texto = 'red'
        caja_color = '#ffe6e6'

    # Escribimos el texto en la figura
    plt.figtext(0.5, 0.05, texto_info, ha="center", fontsize=11, 
                bbox={"facecolor": caja_color, "alpha": 0.8, "pad": 10}, fontname='Consolas')

    plt.tight_layout(rect=[0, 0.2, 1, 1]) # Ajustamos márgenes para dejar espacio al texto

    # Guardar y abrir
    nombre_archivo = "resultado_detalle.png"
    plt.savefig(nombre_archivo)
    print(f"\n Resultado con detalles guardado en '{nombre_archivo}'")
    
    try:
        os.startfile(nombre_archivo)
    except:
        print("No se pudo abrir automáticamente.")

def predecir_url(url_imagen):
    print(f"\n Procesando URL...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_imagen, headers=headers)
        img_original = Image.open(BytesIO(response.content)).convert('RGB')
        
        # Predicción
        img_model = img_original.resize((224, 224))
        img_array = tf.keras.utils.img_to_array(img_model)
        img_array = tf.expand_dims(img_array, 0)

        predictions = model.predict(img_array, verbose=0)
        score = tf.nn.softmax(predictions[0])
        
        confidence = 100 * np.max(score) 
        predicted_class = class_names[np.argmax(score)]
        
        UMBRAL = 85.0 

        if confidence >= UMBRAL:
            print(f" ¡MATCH ENCONTRADO! Es: {predicted_class}")
            
            # Buscamos datos extra en consola también
            if predicted_class in catalogo_info:
                dato = catalogo_info[predicted_class]
                print(f"   -> Nombre: {dato['Nombre']}")
                print(f"   -> Precio: ${dato['Precio']}")
                print(f"   -> Pasillo: {dato['Ubicacion']}")
            
            mostrar_resultado_con_datos(img_original, predicted_class, confidence)
        else:
            print(f" NO RECONOCIDO. (Parece {predicted_class}: {confidence:.1f}%)")
            mostrar_resultado_con_datos(img_original, predicted_class, confidence)

    except Exception as e:
        print(f" Error: {e}")

# --- EJECUCIÓN ---
url = "https://promartecuador.vtexassets.com/arquivos/ids/228373-800-600?v=638672766164170000&width=800&height=600&aspect=true"
predecir_url(url)