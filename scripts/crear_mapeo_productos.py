#!/usr/bin/env python3
"""
Script para crear un mapeo entre nombres de productos del CSV y meshes del ACTUAL.glb
Genera un archivo JSON con el diccionario de mapeo para usar en el frontend
"""

import csv
import json
import re
from pathlib import Path
from pygltflib import GLTF2

def extraer_nombres_meshes(ruta_glb):
    """Extrae los nombres únicos de mallas del GLB (excluyendo Cube/Cubo)"""
    nombres_meshes = []
    try:
        gltf_model = GLTF2().load(ruta_glb)
        if gltf_model.nodes:
            for nodo in gltf_model.nodes:
                if nodo.name:
                    # FILTRO: Omitir Cube/Cubo
                    if 'cube' not in nodo.name.lower() and 'cubo' not in nodo.name.lower():
                        nombres_meshes.append(nodo.name)
    except Exception as e:
        print(f" Error al cargar GLB: {e}")
    
    return nombres_meshes

def normalizar_nombre(nombre):
    """Normaliza un nombre para comparación (minúsculas, sin espacios, sin caracteres especiales)"""
    texto = nombre.lower()
    # Reemplazar espacios y caracteres especiales con _
    texto = re.sub(r'[^a-z0-9_]', '', texto)
    return texto

def extraer_nombre_base(nombre):
    """Extrae el nombre base sin sufijos numéricos (.001, .002, etc.)"""
    # Remover sufijos como .001, .002, Cylinder.001, etc.
    # Pero mantener los guiones bajos
    nombre_sin_sufijo = re.sub(r'\.\d+$', '', nombre)  # Remover .XXX al final
    return nombre_sin_sufijo

def encontrar_mesh_mejor_coincidencia(nombre_producto, nombres_meshes):
    """
    Busca la mejor coincidencia entre un nombre de producto y los nodos del GLB
    Retorna el nombre BASE del nodo (sin sufijos .001, .002, etc.)
    """
    nombre_normalizado = normalizar_nombre(nombre_producto)
    palabras_producto = nombre_normalizado.split('_')
    
    # NIVEL 1: Búsqueda exacta (texto idéntico)
    for mesh_name in nombres_meshes:
        if mesh_name == nombre_producto:
            # Retornar nombre base sin sufijos numéricos
            return extraer_nombre_base(mesh_name)
    
    # NIVEL 2: Búsqueda normalizada (ignorando espacios y caracteres especiales)
    for mesh_name in nombres_meshes:
        if normalizar_nombre(mesh_name) == nombre_normalizado:
            # Retornar nombre base del nodo encontrado
            return extraer_nombre_base(mesh_name)
    
    # NIVEL 3: Búsqueda por nombre substring
    for mesh_name in nombres_meshes:
        mesh_normalizado = normalizar_nombre(mesh_name)
        if mesh_normalizado in nombre_normalizado or nombre_normalizado in mesh_normalizado:
            if len(mesh_normalizado) > 3:  # Evitar coincidencias muy cortas
                return extraer_nombre_base(mesh_name)
    
    # NIVEL 4: Búsqueda por palabras clave (múltiples palabras coincidentes)
    mejores_coincidencias = []
    for mesh_name in nombres_meshes:
        mesh_normalizado = normalizar_nombre(mesh_name)
        palabras_mesh = mesh_normalizado.split('_')
        
        # Contar palabras coincidentes
        coincidencias = sum(1 for p in palabras_producto if p in palabras_mesh and len(p) > 2)
        if coincidencias >= 2:  # Requiere al menos 2 palabras coincidentes
            mejores_coincidencias.append((mesh_name, coincidencias))
    
    if mejores_coincidencias:
        mejores_coincidencias.sort(key=lambda x: x[1], reverse=True)
        return extraer_nombre_base(mejores_coincidencias[0][0])
    
    # NIVEL 5: Buscar nodos que compartan la primera palabra significativa
    primera_palabra = next((p for p in palabras_producto if len(p) > 3), None)
    if primera_palabra:
        for mesh_name in nombres_meshes:
            mesh_normalizado = normalizar_nombre(mesh_name)
            if mesh_normalizado.startswith(primera_palabra):
                return extraer_nombre_base(mesh_name)
    
    return None

def crear_mapeo(csv_path, glb_path, salida_json):
    """Crea el mapeo entre productos del CSV y meshes del GLB"""
    
    print("\n" + "="*70)
    print(" CREANDO MAPEO DE PRODUCTOS A MESHES")
    print("="*70 + "\n")
    
    # Cargar meshes disponibles
    nombres_meshes = extraer_nombres_meshes(glb_path)
    print(f" Se encontraron {len(nombres_meshes)} mallas en ACTUAL.glb")
    
    # Cargar productos del CSV
    productos = []
    mapeo = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nombre_producto = row.get('Nombre', '').strip()
                if nombre_producto:
                    productos.append(nombre_producto)
                    
                    # Buscar mesh coincidente
                    mesh_encontrado = encontrar_mesh_mejor_coincidencia(nombre_producto, nombres_meshes)
                    
                    mapeo[nombre_producto] = mesh_encontrado
                    
                    if mesh_encontrado:
                        print(f" {nombre_producto:40s} → {mesh_encontrado}")
                    else:
                        print(f"  {nombre_producto:40s} → [NO ENCONTRADO]")
    
    except Exception as e:
        print(f" Error al leer CSV: {e}")
        return
    
    # Guardar mapeo en JSON
    try:
        with open(salida_json, 'w', encoding='utf-8') as f:
            json.dump(mapeo, f, ensure_ascii=False, indent=2)
        
        print(f"\n Mapeo guardado en: {salida_json}")
        print(f" Total de productos: {len(productos)}")
        print(f" Encontrados: {sum(1 for v in mapeo.values() if v is not None)}")
        print(f" No encontrados: {sum(1 for v in mapeo.values() if v is None)}")
        
    except Exception as e:
        print(f" Error al guardar JSON: {e}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    csv_path = base_dir / 'data' / 'catalogo_productos_unico.csv'
    glb_path = base_dir / 'assets' / '3d' / 'ACTUAL.glb'
    salida_json = base_dir / 'assets' / '3d' / 'mapeo_productos.json'
    
    crear_mapeo(str(csv_path), str(glb_path), str(salida_json))
