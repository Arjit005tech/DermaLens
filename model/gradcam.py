"""
gradcam.py
----------
Grad-CAM heatmap generation for the trained MobileNetV2 classifier.
Used by the backend at inference time to produce the "AI attention"
overlay shown in the frontend report view.
"""

import numpy as np
import tensorflow as tf
import cv2


def find_last_conv_layer(model):
    """Locate the last convolutional layer inside the MobileNetV2 base,
    since our model is a Functional wrapper around it."""
    base = model.get_layer(index=1)  # the MobileNetV2 functional submodel
    for layer in reversed(base.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            return base, layer.name
    raise ValueError("No Conv2D layer found in base model")


def make_gradcam_heatmap(img_array, model, last_conv_layer_name=None):
    """
    img_array: preprocessed (1, 224, 224, 3) float array, already run
               through mobilenet_v2.preprocess_input.
    Returns: heatmap as a (H, W) float array normalized to [0, 1].
    """
    base, conv_name = find_last_conv_layer(model)
    if last_conv_layer_name:
        conv_name = last_conv_layer_name

    grad_model = tf.keras.models.Model(
        [base.inputs], [base.get_layer(conv_name).output, base.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, base_output = grad_model(img_array)
        # re-run the head on base_output to get final predictions
        x = base_output
        for layer in model.layers[2:]:
            x = layer(x)
        preds = x
        pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy(), int(pred_index.numpy())


def overlay_heatmap(original_bgr_img, heatmap, alpha=0.4):
    """
    original_bgr_img: original image as read by cv2 (H, W, 3) BGR, any size.
    heatmap: output of make_gradcam_heatmap, shape (h, w) in [0,1].
    Returns: BGR image (same size as original) with heatmap overlaid.
    """
    heatmap_resized = cv2.resize(heatmap, (original_bgr_img.shape[1],
                                            original_bgr_img.shape[0]))
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    overlaid = cv2.addWeighted(heatmap_color, alpha, original_bgr_img,
                                1 - alpha, 0)
    return overlaid
