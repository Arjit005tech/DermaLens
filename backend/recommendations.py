"""
Simple rule-based recommendation lookup.

Deliberately NOT framed as "AI-generated" recommendations - it's a
lookup table curated from dermatology-adjacent public guidance. Being
honest about this in your README/demo is a strength, not a weakness:
it shows you understand the line between what your model actually does
(classification) and what's a supporting feature (guidance).
"""

RECOMMENDATIONS = {
    "acne": (
        "Consider a gentle salicylic-acid cleanser and non-comedogenic "
        "moisturizer. Avoid picking at lesions. See a dermatologist if "
        "acne is painful, cystic, or scarring."
    ),
    "hyperpigmentation": (
        "Daily broad-spectrum sunscreen (SPF 30+) is the single most "
        "effective preventive step. Vitamin C serums and niacinamide "
        "may help fade existing spots over time."
    ),
    "fungal_infection": (
        "Keep the area clean and dry. Over-the-counter antifungal creams "
        "(e.g. clotrimazole) are a common first step, but see a doctor "
        "if it spreads or does not improve within 2 weeks."
    ),
    "healthy": (
        "No concerning signs detected. Maintain a simple routine: "
        "cleanser, moisturizer, and daily sunscreen."
    ),
}

DISCLAIMER = (
    "This is an AI-assisted preliminary screening tool, not a medical "
    "diagnosis. Please consult a licensed dermatologist for confirmation "
    "and treatment."
)


def get_recommendation(predicted_class: str) -> str:
    return RECOMMENDATIONS.get(
        predicted_class,
        "No specific guidance available for this class yet.",
    )
