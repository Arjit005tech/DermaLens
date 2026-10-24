"""
train.py
--------
Trains a skin-condition classifier using transfer learning on
MobileNetV2 (fast, deploys well) with a two-stage strategy:
  Stage 1: freeze the base, train only the new classification head.
  Stage 2: unfreeze the top layers of the base and fine-tune at a low LR.

Run:
    python train.py

Outputs:
    dermalens_model.h5      - final trained model
    class_names.json        - class index -> label mapping (used by API)
    training_history.png    - accuracy/loss curves
"""

import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
STAGE1_EPOCHS = 10
STAGE2_EPOCHS = 8
DATA_DIR = "data"


def build_datasets():
    train_ds = tf.keras.utils.image_dataset_from_directory(
        f"{DATA_DIR}/train", image_size=IMG_SIZE, batch_size=BATCH_SIZE,
        label_mode="categorical")
    val_ds = tf.keras.utils.image_dataset_from_directory(
        f"{DATA_DIR}/val", image_size=IMG_SIZE, batch_size=BATCH_SIZE,
        label_mode="categorical")
    class_names = train_ds.class_names

    augment = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.08),
        layers.RandomZoom(0.1),
        layers.RandomBrightness(0.15),
    ])

    def prep_train(x, y):
        x = augment(x)
        x = preprocess_input(x)
        return x, y

    def prep_val(x, y):
        x = preprocess_input(x)
        return x, y

    train_ds = train_ds.map(prep_train).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.map(prep_val).prefetch(tf.data.AUTOTUNE)
    return train_ds, val_ds, class_names


def compute_class_weights(class_names):
    """
    Counts images per class in data/train and returns a dict mapping
    class index -> weight, so under-represented classes (e.g. 'acne'
    with far fewer images than 'healthy') get penalized more heavily
    when the model gets them wrong. Without this, the model tends to
    just favor whichever class has the most images.
    """
    counts = {}
    for i, cls in enumerate(class_names):
        cls_dir = os.path.join(DATA_DIR, "train", cls)
        counts[i] = len([f for f in os.listdir(cls_dir)
                          if f.lower().endswith((".jpg", ".jpeg", ".png"))])

    total = sum(counts.values())
    num_classes = len(counts)
    weights = {i: total / (num_classes * c) for i, c in counts.items()}

    print("Class counts:", {class_names[i]: c for i, c in counts.items()})
    print("Class weights:", {class_names[i]: round(w, 2)
                              for i, w in weights.items()})
    return weights


def build_model(num_classes):
    base = MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False,
                        weights="imagenet")
    base.trainable = False  # Stage 1: frozen

    inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs)
    return model, base


def plot_history(h1, h2, out_path="training_history.png"):
    acc = h1.history["accuracy"] + h2.history["accuracy"]
    val_acc = h1.history["val_accuracy"] + h2.history["val_accuracy"]
    loss = h1.history["loss"] + h2.history["loss"]
    val_loss = h1.history["val_loss"] + h2.history["val_loss"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(acc, label="train")
    axes[0].plot(val_acc, label="val")
    axes[0].axvline(len(h1.history["accuracy"]) - 0.5, color="gray",
                     linestyle="--", label="fine-tune start")
    axes[0].set_title("Accuracy")
    axes[0].legend()

    axes[1].plot(loss, label="train")
    axes[1].plot(val_loss, label="val")
    axes[1].axvline(len(h1.history["loss"]) - 0.5, color="gray",
                     linestyle="--")
    axes[1].set_title("Loss")
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(out_path)
    print(f"Saved {out_path}")


def main():
    train_ds, val_ds, class_names = build_datasets()
    print("Classes:", class_names)

    class_weights = compute_class_weights(class_names)

    model, base = build_model(num_classes=len(class_names))

    # ---- Stage 1: train head only ----
    model.compile(optimizer=optimizers.Adam(1e-3),
                   loss="categorical_crossentropy",
                   metrics=["accuracy"])
    print("\n=== Stage 1: training classification head ===")
    history1 = model.fit(train_ds, validation_data=val_ds,
                          epochs=STAGE1_EPOCHS,
                          class_weight=class_weights)

    # ---- Stage 2: fine-tune top layers of base ----
    base.trainable = True
    fine_tune_at = len(base.layers) - 30  # unfreeze last 30 layers
    for layer in base.layers[:fine_tune_at]:
        layer.trainable = False

    model.compile(optimizer=optimizers.Adam(1e-5),
                   loss="categorical_crossentropy",
                   metrics=["accuracy"])
    print("\n=== Stage 2: fine-tuning ===")
    history2 = model.fit(train_ds, validation_data=val_ds,
                          epochs=STAGE2_EPOCHS,
                          class_weight=class_weights)

    model.save("dermalens_model.h5")
    with open("class_names.json", "w") as f:
        json.dump(class_names, f)

    plot_history(history1, history2)
    print("\nSaved dermalens_model.h5 and class_names.json")


if __name__ == "__main__":
    main()
