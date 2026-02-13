import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from pathlib import Path

# ================= CONFIGURACIÓN =================
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data' / 'dataset'
MODEL_NAME = BASE_DIR / 'models' / 'mi_modelo_pro.keras'
CLASES_FILE = BASE_DIR / 'data' / 'clases.txt'

def reentrenar_modelo():
    print("\n INICIANDO RE-ENTRENAMIENTO (MODO CALIDAD ALTA)...")

    # ================= 1. CARGA DE DATOS =================
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE
    )

    class_names = train_ds.class_names
    print(f" Clases encontradas: {class_names}")

    with open(CLASES_FILE, 'w') as f:
        for name in class_names:
            f.write(name + '\n')
    
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # ================= 2. DATA AUGMENTATION =================

    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
        layers.RandomContrast(0.2),
    ])

    # ================= 3. MODELO (Transfer Learning) =================
    
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False 

    model = models.Sequential([
        layers.Input(shape=IMG_SIZE + (3,)),
        data_augmentation,
        layers.Rescaling(1./127.5, offset=-1), 
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(len(class_names), activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    callbacks = [
        EarlyStopping(patience=5, restore_best_weights=True),
        ReduceLROnPlateau(patience=3, factor=0.3, min_lr=1e-6)
    ]

    # ================= 4. ENTRENAMIENTO – FASE 1 =================
    print(" Entrenando FASE 1 (Esto tomará tiempo)...")
    model.fit(train_ds, validation_data=val_ds, epochs=20, callbacks=callbacks)

    # ================= 5. FINE-TUNING – FASE 2 =================
    print(" Fine-tuning del modelo (FASE 2)...")
    
    base_model.trainable = True
    for layer in base_model.layers[:-50]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    model.fit(train_ds, validation_data=val_ds, epochs=20, callbacks=callbacks)

    # ================= 6. GUARDAR =================
    model.save(MODEL_NAME)
    print(f"\n Modelo actualizado y guardado como '{MODEL_NAME}'")
    
    return True

if __name__ == "__main__":
    reentrenar_modelo()