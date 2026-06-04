import os
import sys
import cv2
import csv
import json
import numpy as np
import tensorflow as tf
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, make_response
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import requests
from fpdf import FPDF
import datetime


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from scripts import entrenar

app = Flask(__name__)
app.secret_key = 'compriayuda_secret_key_2026'
CORS(app)

# --- CONFIGURACIÓN ---
CSV_PATH = BASE_DIR / 'data' / 'catalogo_productos_unico.csv'
CLASS_PATH = BASE_DIR / 'data' / 'clases.txt'
DATASET_DIR = BASE_DIR / 'data' / 'dataset' 
MODEL_FILENAME = BASE_DIR / 'models' / 'mi_modelo_pro.keras'
CREDENTIALS_PATH = BASE_DIR / 'data' / 'credenciales.json'

# Variables Globales
model = None
class_names = []
catalogo = {}


CLASS_MAPPING = {
    "Alcohol lic": "Alcohol_medico_LOV",
    "Bbq original": "Bbq_original",
    "PRODUCTOMEGA.MOV": "Jabon_Lavatodo",
    "Sardina real": "Sardina_Real",
    "aproducto1": "suavizante_gama",
    "aproducto10": "Arroz_El_Artesanal",
    "aproducto11": "Criollita_Maggi",
    "aproducto12": "Achiote_Palma_de_Oro",
    "aproducto13": "Sazonador_Azafran_Condimensa",
    "aproducto14": "Salsa_de_tomate_picante_Los_Andes",
    "aproducto16": "Mayonesa_Alacena",
    "aproducto17": "Vinagre_blanco_SNOB",
    "aproducto18": "Cerveza_Corona",
    "aproducto19": "Cerveza_Stella",
    "aproducto2": "Quita_manchas_supermaxi",
    "aproducto20": "Lata_vino_Anthony",
    "aproducto3": "Mr_musculo_spray",
    "aproducto4": "Desinfectante_Tips_manzana",
    "aproducto5": "Papel_higienico_Elite",
    "aproducto6": "Papel_higienico_Elite2",
    "aproducto7": "Servilleta_Familia",
    "aproducto8": "Facundo_frejol_rojo",
    "aproducto9": "Maiz_dulce_Gustadina",
    "base-inalambricaaa": "base_inalambrica",
    "mouse_logitech": "mouse_logitech",
    "telefono_infinix": "telefono_infinix",
    "tomatodo": "tomatodo",
}

# ==========================================
# 1. FUNCIONES AUXILIARES
# ==========================================

def cargar_recursos():
    """Carga el modelo y CSV en memoria."""
    global model, class_names, catalogo
    print(" Cargando recursos...")

    # A. Cargar Clases
    if os.path.exists(CLASS_PATH):
        with open(CLASS_PATH, 'r') as f:
            class_names = [line.strip() for line in f.readlines()]
    
    # B. Cargar Modelo
    if os.path.exists(MODEL_FILENAME):
        try:
            model = tf.keras.models.load_model(MODEL_FILENAME)
            print(f"Modelo cargado: {MODEL_FILENAME}")
        except Exception as e: print(f"Error modelo: {e}")
    else:
        print(" No hay modelo entrenado aún.")

    # C. Cargar CSV
    catalogo = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ruta = row.get('Imagen_Referencia', '')
                if ruta and '/' in ruta:
                    try:
                        nombre_carpeta = ruta.split('/')[1] 
                        catalogo[nombre_carpeta] = row
                        print(f" Cargado: {nombre_carpeta} -> {ruta}")
                    except Exception as e:
                        print(f" Error al procesar: {ruta} - {e}")
        print(f" Total productos en catálogo: {len(catalogo)}")
    else:
        print(f" CSV no encontrado: {CSV_PATH}")
    print(" Recursos listos.")


def _to_float(val, default=0.0):
    try:
        return float(val)
    except Exception:
        return default

def procesar_video(video_path, nombre_carpeta):
    """Extrae fotos del video usando OpenCV"""
    output_folder = os.path.join(DATASET_DIR, nombre_carpeta)
    if not os.path.exists(output_folder): os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    count = 0
    saved = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        # Guardar 1 de cada 5 frames para variedad
        if count % 5 == 0:
            cv2.imwrite(f"{output_folder}/{nombre_carpeta}_{saved}.jpg", frame)
            saved += 1
        count += 1
    cap.release()
    return saved, f"dataset/{nombre_carpeta}/{nombre_carpeta}_0.jpg"

# Carga inicial
cargar_recursos()

# ==========================================
# 2. RUTAS WEB
# ==========================================

@app.route('/')
def home(): return render_template('index.html')

@app.route('/mapa')
def mapa(): return render_template('mapa.html')

@app.route('/login')
def login_page():
    if session.get('admin_logged'):
        return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json()
    usuario = data.get('usuario', '')
    password = data.get('password', '')
    try:
        with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as f:
            creds = json.load(f)
        for u in creds.get('usuarios', []):
            if u['usuario'] == usuario and u['password'] == password:
                session['admin_logged'] = True
                return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Usuario o contraseña incorrectos'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/auth/logout')
def auth_logout():
    session.pop('admin_logged', None)
    return redirect(url_for('login_page'))

@app.route('/admin')
def admin():
    if not session.get('admin_logged'):
        return redirect(url_for('login_page'))
    return render_template('admin.html')

@app.route('/modelo3d.html')
def serve_3d():
    return send_from_directory(str(BASE_DIR / 'assets' / '3d'), 'modelo3d.html')

@app.route('/dataset/<path:filename>')
def serve_ds(filename):
    return send_from_directory(str(DATASET_DIR), filename)

@app.route('/<path:filename>')
def serve_files(filename):
    # IMPORTANTE: Agregamos .glb para que cargue el modelo 3D y soportamos mayúsculas/minúsculas
    allowed = ['.obj', '.mtl', '.jpg', '.png', '.jpeg', '.bmp', '.gif', '.glb'] 
    
    # Verificar extensión (case-insensitive)
    if any(filename.lower().endswith(e) for e in allowed):
        base_dir = BASE_DIR
        if filename.lower().endswith('.glb'):
            base_dir = BASE_DIR / 'assets' / '3d'
        return send_from_directory(str(base_dir), filename)
    return "No permitido", 404


# ==========================================
# 3. RUTAS DE ADMIN (Backend)
# ==========================================

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    try:
        nombre = request.form.get('nombre')
        video = request.files.get('video')
        
        if not video or not nombre: 
            return jsonify({'success': False, 'error': 'Faltan datos'})
        
        nombre_safe = nombre.replace(" ", "_")
        
        # Guardar video temporal
        video.save("temp.mp4")
        
        # 1. Procesar video
        num_fotos, ruta_img = procesar_video("temp.mp4", nombre_safe)
        if os.path.exists("temp.mp4"): os.remove("temp.mp4")

        # 2. Guardar en CSV
        subcat = request.form.get('subcategoria')
        if not subcat: 
            subcat = "General"

        nueva_fila = [
            nombre, 
            request.form.get('categoria'), 
            subcat, 
            nombre.lower().replace(" ", "-"), 
            ruta_img, 
            request.form.get('descripcion'), 
            999, 
            request.form.get('ubicacion'), 
            request.form.get('precio'),
            # ✅ NUEVOS CAMPOS: COORDENADAS 3D
            request.form.get('pos_x', '0'),
            request.form.get('pos_y', '2'),
            request.form.get('pos_z', '0')
        ]
        
        with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(nueva_fila)

        # Recargar CSV en memoria
        cargar_recursos() 

        return jsonify({'success': True, 'message': f'Producto guardado. {num_fotos} fotos generadas.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/train_model', methods=['POST'])
def train_route():
    try:
        entrenar.reentrenar_modelo()
        cargar_recursos()
        return jsonify({'success': True, 'message': 'Modelo re-entrenado exitosamente.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==========================================
# 4. PREDICCIÓN (IA Scanner)
# ==========================================

@app.route('/predict', methods=['POST'])
def predict():
    if model is None: 
        return jsonify({'error': 'El modelo no está cargado.'}), 500

    try:
        file = request.files.get('file')
        url = request.form.get('url')
        
        img = None

        if file:
            img = Image.open(file.stream).convert('RGB')
        elif url:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            img = Image.open(BytesIO(response.content)).convert('RGB')
        else:
            return jsonify({'error': 'No se recibió imagen ni URL'}), 400

        # Pre-procesamiento
        img_resized = img.resize((224, 224))
        img_array = tf.keras.utils.img_to_array(img_resized)
        img_array = tf.expand_dims(img_array, 0)
        
        # NOTA: No normalizamos aquí porque el modelo tiene capa Rescaling interna.

        # Predicción
        predictions = model.predict(img_array, verbose=0)
        score = predictions[0]
        
        confidence = float(100 * np.max(score)) 
        predicted_class = class_names[np.argmax(score)]

        # DEBUG: Ver qué se está prediciendo y qué hay en el catálogo
        print(f" Clase predicha: {predicted_class}")
        print(f" Claves en catálogo: {list(catalogo.keys())}")
        
        # Buscar Info - intentar con nombre directo, luego con mapeo
        catalog_key = CLASS_MAPPING.get(predicted_class, predicted_class)
        info = catalogo.get(catalog_key, catalogo.get(predicted_class, {}))
        print(f"Mapeo: {predicted_class} -> {catalog_key}")
        print(f"Info encontrada: {info}")
        print(f"Imagen_Referencia: {info.get('Imagen_Referencia', 'NO ENCONTRADA')}")

        result = {
            'class': predicted_class,
            'confidence': round(confidence, 1),
            'nombre_real': info.get('Nombre', predicted_class),
            'precio': info.get('Precio', 'Consultar'),
            'ubicacion': info.get('Ubicacion', 'Desconocida'),
            'descripcion': info.get('Descripcion', 'Sin descripción disponible.'),
            'imagen_url': info.get('Imagen_Referencia', ''),
            # ENVIAMOS COORDENADAS AL FRONTEND
            'coords': {
                'x': _to_float(info.get('PosX', 0), 0.0),
                'y': _to_float(info.get('PosY', 2), 2.0),
                'z': _to_float(info.get('PosZ', 0), 0.0)
            }
        }

        return jsonify(result)

    except Exception as e:
        print(f"Error en predicción: {e}")
        return jsonify({'error': str(e)}), 500

# ==========================================
# 5. SERVIR IMÁGENES DEL DATASET
# ==========================================

@app.route('/get_image/<filename>')
def get_image(filename):
    """Sirve imágenes del dataset o carpeta de datos."""
    posibles_rutas = [
        BASE_DIR / 'data' / filename,  
        BASE_DIR / 'data' / 'dataset' / filename.replace('dataset/', ''),  
        BASE_DIR / filename,
        BASE_DIR / 'dataset' / filename,
        BASE_DIR / 'dataset' / 'images' / filename,
        BASE_DIR / 'app' / 'static' / 'images' / filename,
    ]
    
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return send_from_directory(str(ruta.parent), ruta.name)
    
    # Si no encuentra la imagen, retorna placeholder
    return send_from_directory(str(BASE_DIR / 'app' / 'static'), 'img/placeholder.png')

# ==========================================
# 5b. SERVIR MAPEO DE PRODUCTOS PARA 3D
# ==========================================

@app.route('/mapeo_productos.json')
def get_mapeo_productos():
    """Sirve el mapeo de productos a mallas del modelo 3D"""
    try:
        ruta_mapeo = BASE_DIR / 'assets' / '3d' / 'mapeo_productos.json'
        if os.path.exists(ruta_mapeo):
            with open(ruta_mapeo, 'r', encoding='utf-8') as f:
                import json
                mapeo = json.load(f)
            return mapeo
        else:
            return {'error': 'Mapeo no encontrado'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

# ==========================================
# 6. BUSCADOR MANUAL
# ==========================================

@app.route('/buscar')
def pagina_buscar():
    return render_template('buscar.html')

@app.route('/api/buscar_producto')
def api_buscar():
    query = request.args.get('q', '').lower()
    categoria_filtro = request.args.get('cat', '').lower()

    resultados = []
    
    if not query and not categoria_filtro:
        return jsonify([])

    for producto in catalogo.values():
        nombre_prod = producto.get('Nombre', '').lower()
        cat_prod = producto.get('Categoria', '').lower()
        
        agregar = False

        if query:
            if query in nombre_prod:
                agregar = True
        elif categoria_filtro:
            if categoria_filtro == cat_prod:
                agregar = True

        if agregar:
            resultados.append({
                'nombre': producto.get('Nombre'),
                'precio': producto.get('Precio'),
                'ubicacion': producto.get('Ubicacion'),
                'imagen': producto.get('Imagen_Referencia'),
                'desc': producto.get('Descripcion'),
                'coords': {
                    'x': _to_float(producto.get('PosX', 0), 0.0),
                    'y': _to_float(producto.get('PosY', 2), 2.0),
                    'z': _to_float(producto.get('PosZ', 0), 0.0)
                }
            })
    
    return jsonify(resultados)


    

@app.route('/api/generar_lista_pdf', methods=['POST'])
@app.route('/api/generar_lista_pdf', methods=['POST'])
def generar_lista_pdf():
    try:
        data = request.json
        productos = data.get('productos', [])
        
        class PDF(FPDF):
            def header(self):
                # Fondo oscuro superior (simulado con rectángulo)
                self.set_fill_color(40, 27, 33)  # Color oscuro similar al fondo
                self.rect(0, 0, 210, 45, 'F')
                
                # Logo/Título principal
                self.set_text_color(255, 255, 255)
                self.set_font('Arial', 'B', 24)
                self.cell(0, 15, '', 0, 1)  # Espacio superior
                self.cell(0, 12, 'COMPRI AYUDA', 0, 1, 'C')
                
                # Subtítulo
                self.set_font('Arial', 'I', 14)
                self.set_text_color(220, 130, 145)  # Color rosado/rojizo
                self.cell(0, 8, 'Lista de Compras', 0, 1, 'C')
                
                # Línea decorativa
                self.set_draw_color(220, 130, 145)
                self.set_line_width(0.8)
                self.line(15, 43, 195, 43)
                
                self.ln(8)
            
            def footer(self):
                self.set_y(-20)
                self.set_font('Arial', 'I', 9)
                self.set_text_color(128, 128, 128)
                self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')
                
                # Línea decorativa inferior
                self.set_y(-25)
                self.set_draw_color(220, 130, 145)
                self.set_line_width(0.5)
                self.line(15, self.get_y(), 195, self.get_y())
        
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=25)
        pdf.add_page()
        
        # Fecha y hora con estilo
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(80, 80, 80)
        fecha = datetime.datetime.now().strftime('%d de %B del %Y - %H:%M')
        
        # Traducir mes a español (básico)
        meses = {
            'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
            'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
            'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
            'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
        }
        for eng, esp in meses.items():
            fecha = fecha.replace(eng, esp)
        
        pdf.cell(0, 8, f"Generado: {fecha}", 0, 1, 'R')
        pdf.ln(3)
        
        # Información adicional
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, f"Total de productos: {len(productos)}", 0, 1, 'R')
        pdf.ln(5)
        
        # Encabezados de tabla con diseño mejorado
        pdf.set_fill_color(182, 74, 88)  # Color principal rojizo
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_draw_color(200, 200, 200)
        
        w_num = 12
        w_prod = 73
        w_precio = 30
        w_ubic = 65
        
        pdf.cell(w_num, 10, "#", 1, 0, 'C', True)
        pdf.cell(w_prod, 10, "Producto", 1, 0, 'C', True)
        pdf.cell(w_precio, 10, "Precio", 1, 0, 'C', True)
        pdf.cell(w_ubic, 10, "Ubicacion", 1, 1, 'C', True)
        
        # Productos con filas alternadas
        pdf.set_font("Arial", size=10)
        total = 0.0
        
        for idx, p in enumerate(productos, 1):
            # Alternar colores de fila
            if idx % 2 == 0:
                pdf.set_fill_color(245, 245, 245)
                fill = True
            else:
                fill = False
            
            pdf.set_text_color(50, 50, 50)
            
            nombre = str(p.get('nombre', 'Producto')).encode('latin-1', 'ignore').decode('latin-1')
            ubicacion = str(p.get('ubicacion', '')).encode('latin-1', 'ignore').decode('latin-1')
            precio_str = str(p.get('precio', '0')).replace('$', '').replace(',', '').strip()
            
            try:
                precio_val = float(precio_str)
            except:
                precio_val = 0.0
            total += precio_val
            
            # Número de ítem
            pdf.cell(w_num, 9, str(idx), 1, 0, 'C', fill)
            
            # Nombre del producto
            pdf.cell(w_prod, 9, nombre[:35], 1, 0, 'L', fill)
            
            # Precio con formato
            pdf.set_text_color(33, 150, 83) if precio_val > 0 else pdf.set_text_color(180, 180, 180)
            pdf.cell(w_precio, 9, f"${precio_val:.2f}", 1, 0, 'R', fill)
            
            # Ubicación
            pdf.set_text_color(50, 50, 50)
            pdf.cell(w_ubic, 9, ubicacion[:28], 1, 1, 'L', fill)
        
        # Espacio antes del total
        pdf.ln(8)
        
        # Caja de resumen con borde
        pdf.set_draw_color(182, 74, 88)
        pdf.set_line_width(0.8)
        
        # Fondo del total
        pdf.set_fill_color(250, 245, 245)
        summary_y = pdf.get_y()
        pdf.rect(15, summary_y, 180, 20, 'DF')
        
        # Texto del total
        pdf.set_xy(15, summary_y + 5)
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(182, 74, 88)
        pdf.cell(120, 10, "TOTAL ESTIMADO:", 0, 0, 'R')
        
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(182, 74, 88)
        pdf.cell(60, 10, f"${total:.2f}", 0, 1, 'R')
        
        # Nota al pie
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 8)
        pdf.set_text_color(120, 120, 120)
        pdf.multi_cell(0, 5, 
            "Nota: Los precios son estimados y pueden variar. "
            "Por favor verifique los precios actuales en tienda.", 
            0, 'C')
        
        response = make_response(pdf.output(dest='S').encode('latin-1'))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=lista_compri_ayuda.pdf'
        return response
        
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)