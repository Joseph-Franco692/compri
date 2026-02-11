import os
import csv

# --- CONFIGURACIÓN ---
DATASET_DIR = 'dataset'
NOMBRE_CSV = 'catalogo_productos_unico.csv'

# --- TUS DATOS ---
metadatos = {
    "Achiote_Palma_de_Oro": {
        "nombre_real": "Achiote en Pasta Palma de Oro",
        "categoria": "supermercado",
        "subcategoria": "condimentos",
        "tags": "achiote,cocina,sazonador",
        "descripcion": "Pasta de achiote ideal para dar color y sabor a las comidas tradicionales.",
        "id_interno": 0,
        "ubicacion": "Pasillo 2 - Condimentos",
        "precio": 1.50
    },
    "Alcohol_medico_LOV": {
        "nombre_real": "Alcohol Antiséptico LOV 70%",
        "categoria": "farmacia",
        "subcategoria": "primeros auxilios",
        "tags": "alcohol,desinfeccion,salud",
        "descripcion": "Alcohol etílico al 70% para desinfección de heridas y superficies.",
        "id_interno": 1,
        "ubicacion": "Pasillo 8 - Farmacia",
        "precio": 2.00
    },
    "Arroz_El_Artesanal": {
        "nombre_real": "Arroz El Artesanal Premium",
        "categoria": "supermercado",
        "subcategoria": "despensa",
        "tags": "arroz,granos,basico",
        "descripcion": "Arroz de grano largo y seleccionado, ideal para acompañar tus comidas diarias.",
        "id_interno": 2,
        "ubicacion": "Pasillo 1 - Granos",
        "precio": 4.50
    },
    "base_inalambrica": {
        "nombre_real": "Base de Carga Inalámbrica Genérica",
        "categoria": "tecnologia",
        "subcategoria": "accesorios",
        "tags": "cargador,inalambrico,tech",
        "descripcion": "Base de carga inalámbrica estándar Qi para smartphones compatibles.",
        "id_interno": 3,
        "ubicacion": "Pasillo 10 - Tecnología",
        "precio": 15.00
    },
    "Bbq_original": {
        "nombre_real": "Salsa BBQ Original",
        "categoria": "supermercado",
        "subcategoria": "salsas",
        "tags": "bbq,barbacoa,aderezo",
        "descripcion": "Salsa barbacoa sabor original, perfecta para carnes y parrillas.",
        "id_interno": 4,
        "ubicacion": "Pasillo 3 - Salsas",
        "precio": 3.25
    },
    "Cerveza_Corona": {
        "nombre_real": "Cerveza Corona Extra 355ml",
        "categoria": "licores",
        "subcategoria": "cervezas",
        "tags": "alcohol,cerveza,bebida",
        "descripcion": "Cerveza tipo pilsener, ligera y refrescante. Importada.",
        "id_interno": 5,
        "ubicacion": "Pasillo 9 - Licores",
        "precio": 1.75
    },
    "Cerveza_Stella": {
        "nombre_real": "Cerveza Stella Artois 330ml",
        "categoria": "licores",
        "subcategoria": "cervezas",
        "tags": "alcohol,cerveza,premium",
        "descripcion": "Cerveza lager premium de origen belga con sabor equilibrado.",
        "id_interno": 6,
        "ubicacion": "Pasillo 9 - Licores",
        "precio": 2.10
    },
    "Criollita_Maggi": {
        "nombre_real": "Sazonador La Criollita Maggi",
        "categoria": "supermercado",
        "subcategoria": "condimentos",
        "tags": "maggi,sazonador,especias",
        "descripcion": "Mezcla de especias criollas para realzar el sabor de sopas y guisos.",
        "id_interno": 7,
        "ubicacion": "Pasillo 2 - Condimentos",
        "precio": 0.50
    },
    "Desinfectante_Tips_manzana": {
        "nombre_real": "Desinfectante Tips Aroma Manzana",
        "categoria": "limpieza",
        "subcategoria": "pisos",
        "tags": "limpieza,desinfectante,hogar",
        "descripcion": "Limpiador desinfectante líquido con fragancia a manzana verde.",
        "id_interno": 8,
        "ubicacion": "Pasillo 6 - Limpieza",
        "precio": 1.80
    },
    "Facundo_frejol_rojo": {
        "nombre_real": "Fréjol Rojo Facundo",
        "categoria": "supermercado",
        "subcategoria": "enlatados",
        "tags": "frejol,granos,conserva",
        "descripcion": "Fréjoles rojos listos para servir, en conserva.",
        "id_interno": 9,
        "ubicacion": "Pasillo 4 - Enlatados",
        "precio": 1.25
    },
    "Jabon_Lavatodo": {
        "nombre_real": "Jabón en Barra Lavatodo",
        "categoria": "limpieza",
        "subcategoria": "ropa",
        "tags": "jabon,lavanderia,barra",
        "descripcion": "Jabón multiusos en barra, efectivo contra manchas difíciles.",
        "id_interno": 10,
        "ubicacion": "Pasillo 6 - Lavandería",
        "precio": 0.85
    },
    "Lata_vino_Anthony": {
        "nombre_real": "Vino en Lata Anthony's",
        "categoria": "licores",
        "subcategoria": "vinos",
        "tags": "vino,lata,bebida",
        "descripcion": "Vino tinto joven presentado en lata para consumo individual práctico.",
        "id_interno": 11,
        "ubicacion": "Pasillo 9 - Licores",
        "precio": 3.50
    },
    "Maiz_dulce_Gustadina": {
        "nombre_real": "Maíz Dulce Gustadina",
        "categoria": "supermercado",
        "subcategoria": "enlatados",
        "tags": "maiz,choclo,ensalada",
        "descripcion": "Granos de maíz dulce tierno en conserva, ideal para ensaladas.",
        "id_interno": 12,
        "ubicacion": "Pasillo 4 - Enlatados",
        "precio": 1.10
    },
    "Mayonesa_Alacena": {
        "nombre_real": "Mayonesa Alacena Receta Casera",
        "categoria": "supermercado",
        "subcategoria": "salsas",
        "tags": "mayonesa,aderezo,crema",
        "descripcion": "Mayonesa con toque de limón y sabor a receta casera.",
        "id_interno": 13,
        "ubicacion": "Pasillo 3 - Salsas",
        "precio": 2.40
    },
    "mouse_logitech": {
        "nombre_real": "Mouse Óptico Logitech",
        "categoria": "tecnologia",
        "subcategoria": "perifericos",
        "tags": "mouse,computacion,oficina",
        "descripcion": "Ratón óptico alámbrico USB, diseño ergonómico básico.",
        "id_interno": 14,
        "ubicacion": "Pasillo 10 - Tecnología",
        "precio": 12.00
    },
    "Mr_musculo_spray": {
        "nombre_real": "Mr Músculo Cocina Spray",
        "categoria": "limpieza",
        "subcategoria": "cocina",
        "tags": "desengrasante,limpieza,spray",
        "descripcion": "Desengrasante potente en spray para superficies de cocina.",
        "id_interno": 15,
        "ubicacion": "Pasillo 6 - Limpieza",
        "precio": 3.80
    },
    "Papel_higienico_Elite": {
        "nombre_real": "Papel Higiénico Elite Doble Hoja",
        "categoria": "limpieza",
        "subcategoria": "baño",
        "tags": "papel,higiene,baño",
        "descripcion": "Papel higiénico suave y resistente, paquete de 4 rollos.",
        "id_interno": 16,
        "ubicacion": "Pasillo 7 - Papel y Aseo",
        "precio": 2.50
    },
    "Papel_higienico_Elite2": {
        "nombre_real": "Papel Higiénico Elite Ultra",
        "categoria": "limpieza",
        "subcategoria": "baño",
        "tags": "papel,higiene,premium",
        "descripcion": "Variante premium con mayor suavidad y absorción.",
        "id_interno": 17,
        "ubicacion": "Pasillo 7 - Papel y Aseo",
        "precio": 3.00
    },
    "Quita_manchas_supermaxi": {
        "nombre_real": "Quitamanchas Marca Supermaxi",
        "categoria": "limpieza",
        "subcategoria": "ropa",
        "tags": "quitamanchas,ropa,lavado",
        "descripcion": "Aditivo para el lavado que ayuda a remover manchas difíciles en ropa blanca y color.",
        "id_interno": 18,
        "ubicacion": "Pasillo 6 - Lavandería",
        "precio": 4.20
    },
    "Salsa_de_tomate_picante_Los_Andes": {
        "nombre_real": "Salsa de Tomate Picante Los Andes",
        "categoria": "supermercado",
        "subcategoria": "salsas",
        "tags": "ketchup,picante,tomate",
        "descripcion": "Salsa de tomate con un toque picante de ají natural.",
        "id_interno": 19,
        "ubicacion": "Pasillo 3 - Salsas",
        "precio": 1.60
    },
    "Sardina_Real": {
        "nombre_real": "Sardinas Real en Salsa de Tomate",
        "categoria": "supermercado",
        "subcategoria": "enlatados",
        "tags": "pescado,sardina,proteina",
        "descripcion": "Sardinas seleccionadas en salsa de tomate, fuente de Omega 3.",
        "id_interno": 20,
        "ubicacion": "Pasillo 4 - Enlatados",
        "precio": 1.85
    },
    "Sazonador_Azafran_Condimensa": {
        "nombre_real": "Sazonador Azafrán Condimensa",
        "categoria": "supermercado",
        "subcategoria": "condimentos",
        "tags": "especias,colorante,azafran",
        "descripcion": "Condimento a base de azafrán para dar color amarillo y sabor a arroces y sopas.",
        "id_interno": 21,
        "ubicacion": "Pasillo 2 - Condimentos",
        "precio": 1.20
    },
    "Servilleta_Familia": {
        "nombre_real": "Servilletas Familia Acolchadas",
        "categoria": "hogar",
        "subcategoria": "cocina",
        "tags": "servilletas,papel,mesa",
        "descripcion": "Servilletas de papel blancas, suaves y absorbentes para mesa.",
        "id_interno": 22,
        "ubicacion": "Pasillo 7 - Papel y Aseo",
        "precio": 1.50
    },
    "suavizante_gama": {
        "nombre_real": "Suavizante de Ropa Gama",
        "categoria": "limpieza",
        "subcategoria": "ropa",
        "tags": "suavizante,aroma,lavado",
        "descripcion": "Suavizante textil que deja la ropa con aroma fresco y tacto suave.",
        "id_interno": 23,
        "ubicacion": "Pasillo 6 - Lavandería",
        "precio": 3.50
    },
    "telefono_infinix": {
        "nombre_real": "Smartphone Infinix Hot",
        "categoria": "tecnologia",
        "subcategoria": "celulares",
        "tags": "celular,movil,android",
        "descripcion": "Teléfono inteligente con sistema Android y cámara de alta resolución.",
        "id_interno": 24,
        "ubicacion": "Pasillo 10 - Tecnología",
        "precio": 180.00
    },
    "tomatodo": {
        "nombre_real": "Tomatodo Deportivo Plástico",
        "categoria": "hogar",
        "subcategoria": "accesorios",
        "tags": "botella,agua,deporte",
        "descripcion": "Botella reutilizable para agua, material resistente y tapa segura.",
        "id_interno": 25,
        "ubicacion": "Pasillo 5 - Hogar",
        "precio": 5.00
    },
    "Vinagre_blanco_SNOB": {
        "nombre_real": "Vinagre Blanco Snob",
        "categoria": "supermercado",
        "subcategoria": "despensa",
        "tags": "vinagre,cocina,limpieza",
        "descripcion": "Vinagre blanco destilado, ideal para ensaladas o usos de limpieza.",
        "id_interno": 26,
        "ubicacion": "Pasillo 3 - Aderezos",
        "precio": 0.90
    }
}

# --- LÓGICA DE EJECUCIÓN (MODIFICADA) ---
print(" Iniciando generación de Catálogo Único...")

# Nota: Cambié 'Ruta_Imagen' por 'Imagen_Referencia' para que tenga más sentido
encabezados = ['Nombre', 'Categoria', 'Subcategoria', 'Slug', 'Imagen_Referencia', 'Descripcion', 'ID', 'Ubicacion', 'Precio']

try:
    with open(NOMBRE_CSV, mode='w', newline='', encoding='utf-8') as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=encabezados)
        writer.writeheader()
        
        contador_productos = 0

        # Verifica si existe la carpeta dataset
        if not os.path.exists(DATASET_DIR):
            print(f" ERROR: No encuentro la carpeta '{DATASET_DIR}'.")
        else:
            # Recorremos cada carpeta dentro de dataset
            for nombre_carpeta in os.listdir(DATASET_DIR):
                ruta_carpeta = os.path.join(DATASET_DIR, nombre_carpeta)

                if os.path.isdir(ruta_carpeta):
                    # Buscamos si tenemos datos para esta carpeta en el diccionario
                    datos = metadatos.get(nombre_carpeta)

                    if datos:
                        # Buscamos SOLO LA PRIMERA imagen válida
                        imagen_encontrada = "Sin imagen"
                        files = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                        
                        if files:
                            # Agarramos la primera foto de la lista como "Portada"
                            imagen_encontrada = f"{DATASET_DIR}/{nombre_carpeta}/{files[0]}"
                        else:
                             print(f" AVISO: La carpeta '{nombre_carpeta}' no tiene fotos. Se dejará sin referencia.")
                        
                        # Creamos LA ÚNICA fila para este producto
                        fila = {
                            'Nombre': datos['nombre_real'],
                            'Categoria': datos['categoria'],
                            'Subcategoria': datos['subcategoria'],
                            'Slug': datos['tags'],
                            'Imagen_Referencia': imagen_encontrada, # Solo una ruta
                            'Descripcion': datos['descripcion'],
                            'ID': datos['id_interno'],
                            'Ubicacion': datos['ubicacion'],
                            'Precio': datos['precio']
                        }
                        writer.writerow(fila)
                        contador_productos += 1
                        print(f" Producto agregado: {datos['nombre_real']}")

                    else:
                        print(f" AVISO: La carpeta '{nombre_carpeta}' existe pero NO está en tu diccionario.")

    print(f"\n ¡TERMINADO! Se generó '{NOMBRE_CSV}' con {contador_productos} productos únicos.")

except Exception as e:
    print(f" Ocurrió un error inesperado: {e}")