"""
symptom_adjustment.py
----------------------
Combines the CNN's image-based prediction with a short symptom
questionnaire, using dermatology-informed heuristic rules to nudge
the probabilities - NOT a learned/trained fusion model.

WHY RULE-BASED, NOT A TRAINED MULTIMODAL MODEL:
A true multimodal model (image + symptoms jointly learned) needs a
dataset where every training image has matching symptom labels. Public
dermatology datasets don't include that, so training one isn't
possible without collecting your own labeled data. This rule-based
layer is an honest, defensible middle ground: it uses real dermatology
knowledge to adjust the CNN's output, while being transparent that the
adjustment is heuristic, not learned. Document this distinction
clearly in your report - it's a strength, not a shortcut, when
explained this way.
"""

CLASSES = ["acne", "eczema", "fungal_infection", "healthy"]


def adjust_probabilities(probs: dict, sensation: str | None,
                          moist_area: str | None, duration: str | None,
                          pattern: str | None) -> dict:
    """
    probs: dict of {class_name: probability} from the CNN, must sum to ~1.
    sensation: "itchy" | "painful" | "burning" | "none" | None
    moist_area: "yes" | "no" | None
    duration: "days" | "weeks" | "months" | None
    pattern: "comes_and_goes" | "constant" | None

    Returns a new dict of adjusted, re-normalized probabilities.
    Any field left as None is simply skipped (questionnaire is optional).
    """
    adjusted = dict(probs)

    if sensation == "itchy":
        adjusted["eczema"] *= 1.35
        adjusted["fungal_infection"] *= 1.20
    elif sensation == "painful":
        adjusted["acne"] *= 1.30
    elif sensation == "burning":
        adjusted["fungal_infection"] *= 1.30

    if moist_area == "yes":
        adjusted["fungal_infection"] *= 1.40

    if duration == "months":
        adjusted["eczema"] *= 1.20
    elif duration == "days":
        adjusted["fungal_infection"] *= 1.10
        adjusted["acne"] *= 1.05

    if pattern == "comes_and_goes":
        adjusted["eczema"] *= 1.15

    total = sum(adjusted.values())
    if total > 0:
        adjusted = {k: v / total for k, v in adjusted.items()}

    return adjusted
