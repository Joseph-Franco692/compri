# CompriAyuda 🛒

Sistema inteligente de asistencia en supermercado con reconocimiento de productos por IA, buscador manual, mapa de ubicación y visualización 3D del local.

---

## 📋 Requisitos Previos

- **Python** 3.10 - 3.13
- **pip** (incluido con Python)
- **Git** (para clonar el repositorio)

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Damniansz/CompriAyuda.git
cd CompriAyuda
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Preparar el Dataset

Las carpetas de imágenes del dataset no se incluyen en el repositorio por su peso. Debes colocarlas manualmente:

```
data/
  dataset/
    Cerveza_Corona/
    Chips/
    ... (cada producto con sus imágenes)
```

### 5. Entrenar el modelo (si no tienes `mi_modelo_pro.keras`)

Desde el panel de Admin en la web, o manualmente:

```bash
python -c "from scripts.entrenar import reentrenar_modelo; reentrenar_modelo()"
```

El modelo se guarda en `models/mi_modelo_pro.keras`.

---

## 🚀 Ejecución

```bash
python app/app.py
```

El servidor arranca en **http://localhost:5000**

---

## 🗂️ Estructura del Proyecto

```
CompriAyuda/
├── app/
│   ├── app.py                  # Servidor Flask principal
│   ├── static/
│   │   ├── css/                # Estilos (index, admin, login, buscar, mapa)
│   │   ├── js/                 # Scripts frontend (login.js)
│   │   └── img/                # Logo e imágenes estáticas
│   └── templates/              # HTML (index, admin, login, buscar, mapa)
├── assets/
│   └── 3d/                     # Modelo 3D del supermercado (.glb) y mapeo
├── data/
│   ├── catalogo_productos_unico.csv  # Catálogo de productos
│   ├── clases.txt              # Clases del modelo entrenado
│   ├── credenciales.json       # Credenciales del admin
│   └── dataset/                # Imágenes de entrenamiento (NO en Git)
├── models/                     # Modelos .keras entrenados (NO en Git)
├── scripts/
│   ├── entrenar.py             # Script de entrenamiento del modelo
│   ├── predecir.py             # Script de predicción standalone
│   ├── video.py                # Extracción de frames de video
│   ├── generar_csv.py          # Generador del CSV del catálogo
│   ├── crear_mapeo_productos.py # Mapeo productos ↔ mallas 3D
│   ├── extraer_meshes.py       # Extracción de meshes del modelo 3D
│   └── actualizar_csv.py       # Actualización del catálogo
├── requirements.txt            # Dependencias Python
├── .gitignore                  # Archivos excluidos de Git
└── README.md                   # Este archivo
```

---

## 🌐 Rutas Principales

| Ruta | Descripción |
|------|-------------|
| `/` | Página principal - Scanner de productos con IA |
| `/buscar` | Buscador manual de productos |
| `/mapa` | Mapa 2D de ubicación en el supermercado |
| `/login` | Login del panel de administración |
| `/admin` | Panel admin (agregar productos, re-entrenar modelo) |
| `/modelo3d.html` | Vista 3D interactiva del supermercado |

---

## 🔑 Credenciales Admin

Las credenciales se encuentran en `data/credenciales.json`:

```json
{
  "usuarios": [
    { "usuario": "admin", "password": "admin123" }
  ]
}
```

---

## 🤖 Modelo de IA

- **Arquitectura**: MobileNetV2 (Transfer Learning)
- **Entrada**: Imágenes de 224×224 px
- **Entrenamiento**: 2 fases (feature extraction + fine-tuning)
- **Precisión**: ~99% en validación (27+ clases)

---

## 🛠️ Tecnologías

- **Backend**: Flask (Python)
- **IA**: TensorFlow / Keras (MobileNetV2)
- **Frontend**: HTML, CSS (Material Design 3), JavaScript
- **3D**: Three.js con modelo GLB
- **CV**: OpenCV (procesamiento de video)
