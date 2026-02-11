#!/usr/bin/env python3
"""
Script para extraer TODOS los nombres de mallas del archivo modelo.glb
Usa la librería pygltflib para leer correctamente archivos GLB/GLTF
"""

from pygltflib import GLTF2

def extraer_nombres_meshes(ruta_glb):
    """Lee un archivo GLB y extrae los nombres de todos los nodos"""
    
    try:
        # Cargar el archivo GLB
        gltf_model = GLTF2().load(ruta_glb)
        
        print("\n" + "="*70)
        print(" NOMBRES DE NODOS Y MESHES EN ACTUAL.glb")
        print("="*70 + "\n")
        
        # Extraer nombres de nodos
        if gltf_model.nodes:
            print(" NODOS EN LA ESCENA:\n")
            for i, nodo in enumerate(gltf_model.nodes):
                nombre = nodo.name if nodo.name else f"[Sin nombre - Índice {i}]"
                # FILTRO: Omitir Cube/Cubo
                if 'cube' not in nombre.lower() and 'cubo' not in nombre.lower():
                    print(f"   {i:2d}. {nombre}")
        
        # Extraer nombres de mallas (meshes)
        if gltf_model.meshes:
            print("\n MALLAS (MESHES) ENCONTRADAS:\n")
            for i, malla in enumerate(gltf_model.meshes):
                nombre = malla.name if malla.name else f"[Sin nombre - Índice {i}]"
                # FILTRO: Omitir Cube/Cubo
                if 'cube' in nombre.lower() or 'cubo' in nombre.lower():
                    continue
                primitivos = len(malla.primitives) if malla.primitives else 0
                print(f"   {i:2d}. {nombre:40s}  ({primitivos} primitivo{'s' if primitivos != 1 else ''})")
        
        # Información general
        print("\n\n INFORMACIÓN GENERAL:\n")
        print(f"   Total de nodos:    {len(gltf_model.nodes) if gltf_model.nodes else 0}")
        print(f"   Total de mallas:   {len(gltf_model.meshes) if gltf_model.meshes else 0}")
        print(f"   Total de texturas: {len(gltf_model.images) if gltf_model.images else 0}")
        print(f"   Total de materiales: {len(gltf_model.materials) if gltf_model.materials else 0}")
        
        print("\n" + "="*70)
        print("Script completado")
        print("="*70 + "\n")
        
    except FileNotFoundError:
        print(f" No se encontró el archivo: {ruta_glb}")
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extraer_nombres_meshes('assets/3d/ACTUAL.glb')
