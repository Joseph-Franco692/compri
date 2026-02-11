#!/usr/bin/env python3
"""
Script para actualizar nombres en el CSV para que coincidan con los meshes del modelo.glb
"""

import csv

# Mapeo de nombres actuales en CSV a nombres de meshes en modelo.glb
MAPEO_NOMBRES = {
    "Alcohol Antiséptico LOV 70%": "Alcohol",
    "Base de Carga Inalámbrica Genérica": "Base_Inalambrica",
    "Cerveza Corona Extra 355ml": "cajas de corona",
    "Cerveza Stella Artois 330ml": "cajas de stella",
    "Desinfectante Tips Aroma Manzana": "desinfectante_manzana",
    "Jabón en Barra Lavatodo": "jabon_lavatodo",
    "Vino en Lata Anthony's": "Vino_anthony",
    "Mouse Óptico Logitech": "Logitech",
    "Mr Músculo Cocina Spray": "mr_musculo_spray",
    "Papel Higiénico Elite Doble Hoja": "Papel_Higenico",
    "Papel Higiénico Elite Ultra": "Papel_Higenico",
    "Quitamanchas Marca Supermaxi": "quitamanchas",
    "Servilletas Familia Acolchadas": "Servilletas_familia",
    "Suavizante de Ropa Gama": "suavizante_gama",
    "Smartphone Infinix Hot": "Celular_infinix",
    "Tomatodo Deportivo Plástico": "Tomatodo",
}

def actualizar_csv(ruta_csv):
    """Lee el CSV y actualiza los nombres según el mapeo"""
    
    try:
        # Leer el CSV
        filas = []
        with open(ruta_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Si el nombre está en el mapeo, actualizar
                nombre_actual = row['Nombre']
                if nombre_actual in MAPEO_NOMBRES:
                    nombre_nuevo = MAPEO_NOMBRES[nombre_actual]
                    print(f" Actualizando: '{nombre_actual}' → '{nombre_nuevo}'")
                    row['Nombre'] = nombre_nuevo
                else:
                    print(f"⚠️  Sin cambios: '{nombre_actual}' (no tiene mesh en modelo.glb)")
                filas.append(row)
        
        # Escribir el CSV actualizado
        with open(ruta_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Nombre', 'Categoria', 'Subcategoria', 'Slug', 'Imagen_Referencia', 
                         'Descripcion', 'ID', 'Ubicacion', 'Precio', 'PosX', 'PosY', 'PosZ']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filas)
        
        print(f"\n CSV actualizado exitosamente: {ruta_csv}")
        print(f" Total de productos: {len(filas)}")
        print(f"Actualizados: {len(MAPEO_NOMBRES)}")
        
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    actualizar_csv('catalogo_productos_unico.csv')
