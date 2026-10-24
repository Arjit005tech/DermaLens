import os
import sys
import json
import uuid
from pathlib import Path
from typing import Optional

import numpy as np
import cv2
import tensorflow as tf
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.schemas import Report, User
from routers.auth import get_current_user
from recommendations import get_recommendation, DISCLAIMER
from symptom_adjustment import adjust_probabilities

# Make the sibling `model/` directory importable (gradcam.py lives there)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "model"))
from gradcam import make_gradcam_heatmap, overlay_heatmap  # noqa: E402
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input  # noqa: E402

router = APIRouter(prefix="/analyze", tags=["analyze"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MODEL_PATH = os.getenv("MODEL_PATH", "../model/dermalens_model.h5")
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", "../model/class_names.json")

_model = None
_class_names = None
_face_cascade = None


def get_face_cascade():
    """
    Lazy-loads OpenCV's built-in face detector (Haar cascade - ships
    with opencv-python, no extra download needed). Used to crop the
    photo to just the face before classification, so the model can't
    be misled by background color/lighting instead of actual skin.
    """
    global _face_cascade
    if _face_cascade is None:
        cascade_path = (
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        _face_cascade = cv2.CascadeClassifier(cascade_path)
    return _face_cascade


def crop_to_face(img_bgr):
    """
    Detects the largest face in the image and returns a cropped,
    padded version. If no face is detected (e.g. a close-up clinical
    photo of just skin, with no full face visible), returns the
    original image unchanged - this keeps the old clinical-photo
    workflow working exactly as before.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = get_face_cascade().detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
    )

    if len(faces) == 0:
        return img_bgr, False  # no face found - use original image

    # pick the largest detected face (in case of multiple)
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

    # pad around the detected box by 30% so we keep some context
    # (chin, forehead) instead of an overly tight crop
    pad_x, pad_y = int(w * 0.3), int(h * 0.3)
    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(img_bgr.shape[1], x + w + pad_x)
    y2 = min(img_bgr.shape[0], y + h + pad_y)

    return img_bgr[y1:y2, x1:x2], True


def get_model():
    """Lazy-load the model on first request instead of at import time,
    so the API can still start up (e.g. for docs/testing) before the
    model file exists."""
    global _model, _class_names
    if _model is None:
        if not Path(MODEL_PATH).exists():
            raise HTTPException(
                status_code=503,
                detail=(
                    "Model not found. Train it first with model/train.py, "
                    "then set MODEL_PATH in .env."
                ),
            )
        _model = tf.keras.models.load_model(MODEL_PATH)
        with open(CLASS_NAMES_PATH) as f:
            _class_names = json.load(f)
    return _model, _class_names


@router.post("")
async def analyze_image(
    file: UploadFile = File(...),
    sensation: Optional[str] = Form(None),
    moist_area: Optional[str] = Form(None),
    duration: Optional[str] = Form(None),
    pattern: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Upload a JPEG or PNG image")

    model, class_names = get_model()

    # Read upload into memory (not saved to disk yet - we save the
    # face-cropped version below instead, once we know what it is)
    ext = ".jpg" if "jpeg" in file.content_type else ".png"
    file_id = uuid.uuid4().hex
    contents = await file.read()

    # Load for inference
    img_bgr = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

    # Crop to face if one is detected, to remove background influence
    cropped_bgr, face_found = crop_to_face(img_bgr)

    img_resized = cv2.resize(cropped_bgr, (224, 224))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_array = np.expand_dims(img_rgb.astype(np.float32), axis=0)
    img_array = preprocess_input(img_array)

    preds = model.predict(img_array, verbose=0)[0]
    image_only_probs = {
        class_names[i]: round(float(p), 4) for i, p in enumerate(preds)
    }

    # If any questionnaire answer was provided, adjust the probabilities
    # using symptom-based heuristics; otherwise use the raw CNN output
    questionnaire_used = any([sensation, moist_area, duration, pattern])
    if questionnaire_used:
        final_probs = adjust_probabilities(
            image_only_probs, sensation, moist_area, duration, pattern
        )
    else:
        final_probs = image_only_probs

    predicted_class = max(final_probs, key=final_probs.get)
    confidence = final_probs[predicted_class]
    pred_index = class_names.index(predicted_class)

    # Grad-CAM heatmap - generated on the SAME cropped image the model
    # actually saw, so the overlay lines up with what influenced the
    # prediction, and there's no leftover background to mislead the
    # visualization either.
    heatmap, _ = make_gradcam_heatmap(img_array, model)
    overlaid = overlay_heatmap(cropped_bgr, heatmap)
    heatmap_path = UPLOAD_DIR / f"{file_id}_heatmap.jpg"
    cv2.imwrite(str(heatmap_path), overlaid)

    # Save the cropped version as the "original" shown in the UI, so
    # original and heatmap visibly correspond to the same framing
    original_path = UPLOAD_DIR / f"{file_id}_original{ext}"
    cv2.imwrite(str(original_path), cropped_bgr)

    recommendation = get_recommendation(predicted_class)

    report = Report(
        user_id=current_user.id,
        predicted_class=predicted_class,
        confidence=confidence,
        original_image_path=f"/uploads/{original_path.name}",
        heatmap_image_path=f"/uploads/{heatmap_path.name}",
        recommendation=recommendation,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "image_only_probabilities": image_only_probs,
        "final_probabilities": {k: round(v, 4) for k, v in final_probs.items()},
        "questionnaire_used": questionnaire_used,
        "recommendation": recommendation,
        "disclaimer": DISCLAIMER,
        "original_image_url": report.original_image_path,
        "heatmap_image_url": report.heatmap_image_path,
        "face_detected": face_found,
    }
