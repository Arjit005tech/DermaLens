"""
evaluate.py
------------
Runs the trained model against the held-out test set (images it has
never seen, not even during validation) and produces:
  - Overall accuracy
  - Per-class precision, recall, F1-score
  - A confusion matrix (as text and as a saved image)

This is the real way to understand model weaknesses - not by testing
one photo at a time, but by seeing systematically which classes get
confused with which. Run this any time after training to get an
honest picture of where the model actually struggles.

Run:
    cd model
    python evaluate.py
"""

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
DATA_DIR = "data"
MODEL_PATH = "dermalens_model.h5"
CLASS_NAMES_PATH = "class_names.json"


def main():
    with open(CLASS_NAMES_PATH) as f:
        class_names = json.load(f)

    model = tf.keras.models.load_model(MODEL_PATH)

    test_ds = tf.keras.utils.image_dataset_from_directory(
        f"{DATA_DIR}/test",
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=False,  # keep order so predictions line up with labels
    )
    assert test_ds.class_names == class_names, (
        "Class order mismatch between class_names.json and the test "
        "folder - check nothing was renamed."
    )

    test_ds_prepped = test_ds.map(lambda x, y: (preprocess_input(x), y))

    print("Running predictions on the test set...")
    y_true = []
    y_pred = []
    for images, labels in test_ds_prepped:
        preds = model.predict(images, verbose=0)
        y_pred.extend(np.argmax(preds, axis=1))
        y_true.extend(np.argmax(labels.numpy(), axis=1))

    print("\n=== Classification report ===")
    print(classification_report(y_true, y_pred, target_names=class_names,
                                 digits=3))

    overall_acc = np.mean(np.array(y_true) == np.array(y_pred))
    print(f"Overall test accuracy: {overall_acc:.3f}\n")

    cm = confusion_matrix(y_true, y_pred)
    print("=== Confusion matrix (rows = actual, columns = predicted) ===")
    print("Classes:", class_names)
    print(cm)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                   display_labels=class_names)
    fig, ax = plt.subplots(figsize=(7, 7))
    disp.plot(ax=ax, cmap="Blues", xticks_rotation=45)
    plt.tight_layout()
    plt.savefig("confusion_matrix.png")
    print("\nSaved confusion_matrix.png - open this to see it visually.")


if __name__ == "__main__":
    main()
