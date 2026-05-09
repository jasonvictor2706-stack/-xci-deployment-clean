import numpy as np
import shap
from services.ml_service import MODEL, FEATURE_ORDER

# ─────────────────────────────────────────────
# TreeExplainer – computed once, reused per request
# ─────────────────────────────────────────────
print("[AgriSen] Initialising SHAP TreeExplainer...")
EXPLAINER = shap.TreeExplainer(MODEL)
print("[AgriSen] SHAP TreeExplainer ready")

# Human-readable labels for different languages
FEATURE_LABELS = {
    "en": {
        "N": "Nitrogen", "P": "Phosphorus", "K": "Potassium",
        "temperature": "Temperature", "humidity": "Humidity", "ph": "pH", "rainfall": "Rainfall"
    },
    "te": {
        "N": "నత్రజని", "P": "భాస్వరం", "K": "పొటాషియం",
        "temperature": "ఉష్ణోగ్రత", "humidity": "తేమ", "ph": "pH", "rainfall": "వర్షపాతం"
    },
    "hi": {
        "N": "नाइट्रोजन", "P": "फास्फोरस", "K": "पोटेशियम",
        "temperature": "तापमान", "humidity": "आर्द्रता", "ph": "pH", "rainfall": "वर्षा"
    }
}

CROP_NAMES = {
    "te": {
        "apple": "ఆపిల్", "banana": "అరటి", "blackgram": "మినుములు", "chickpea": "శనగలు", "coconut": "కొబ్బరి",
        "coffee": "కాఫీ", "cotton": "పత్తి", "grapes": "ద్రాక్ష", "jute": "జనపనార", "kidneybeans": "రాజ్మా",
        "lentil": "మసూర్ పప్పు", "maize": "మొక్కజొన్న", "mango": "మామిడి", "mothbeans": "మట్కి పప్పు",
        "mungbean": "పెసలు", "muskmelon": "కర్బూజా", "orange": "నారింజ", "papaya": "బొప్పాయి",
        "pigeonpeas": "కందులు", "pomegranate": "దానిమ్మ", "rice": "వరి", "watermelon": "పుచ్చకాయ"
    },
    "hi": {
        "apple": "सेब", "banana": "केला", "blackgram": "उड़द", "chickpea": "चना", "coconut": "नारियल",
        "coffee": "कॉफी", "cotton": "कपास", "grapes": "अंगूर", "jute": "जूट", "kidneybeans": "राजमा",
        "lentil": "मसूर", "maize": "मक्का", "mango": "आम", "mothbeans": "मोठ",
        "mungbean": "मूंग", "muskmelon": "खरबूजा", "orange": "संतरा", "papaya": "पपीता",
        "pigeonpeas": "अरहर", "pomegranate": "अनार", "rice": "चावल", "watermelon": "तरबूज"
    }
}

TRANSLATIONS = {
    "te": {
        "and_word": "మరియు",
        "sentence1": "ప్రస్తుత నేల మరియు వాతావరణ పరిస్థితులు దీనికి అనుకూలంగా ఉన్నందున {crop} సాగు సూచించబడింది.",
        "sentence1_fallback": "అందించిన నేల, వాతావరణ ఆధారంగా {crop} సూచించబడింది.",
        "sentence2": "{primary_factors} {crop} సాగుకు బలంగా మద్దతు ఇస్తున్నాయి{secondary_factors}",
        "sentence2_secondary": ", అలాగే {secondary_list} కూడా అనుకూలంగా ఉన్నాయి.",
        "sentence2_none": " స్థాయిలు.",
        "sentence3_two": "ఇతర పంటలైన {alt0} మరియు {alt1} పరిశీలించబడ్డాయి, కానీ వాటి అవసరాలు ప్రస్తుత వాతావరణంతో ఎక్కువగా సరిపోలడం లేదు.",
        "sentence3_one": "{alt0} వంటి మరొక పంటను అంచనా వేశాము, కానీ దానికి అవసరమైన పరిస్థితులు ప్రస్తుత వాతావరణానికి అనుకూలంగా లేవు.",
        "sentence3_none": ""
    },
    "hi": {
        "and_word": "और",
        "sentence1": "{crop} की सिफारिश इसलिए की जाती है क्योंकि वर्तमान मिट्टी और जलवायु परिस्थितियाँ इसकी इष्टतम वृद्धि आवश्यकताओं से मेल खाती हैं।",
        "sentence1_fallback": "प्रदान की गई मिट्टी और जलवायु मापदंडों के आधार पर {crop} की सिफारिश की जाती है।",
        "sentence2": "{primary_factors} {crop} की खेती का दृढ़ता से समर्थन करते हैं{secondary_factors}",
        "sentence2_secondary": ", जबकि {secondary_list} भी सकारात्मक योगदान देते हैं।",
        "sentence2_none": " स्तर।",
        "sentence3_two": "अन्य फसलों जैसे {alt0} और {alt1} का मूल्यांकन किया गया था, लेकिन उनकी आवश्यकताएं वर्तमान वातावरण के साथ कम संगत हैं।",
        "sentence3_one": "{alt0} जैसी एक अन्य फसल का मूल्यांकन किया गया, लेकिन इसकी आवश्यकताएं वर्तमान वातावरण के साथ कम संगत हैं।",
        "sentence3_none": ""
    },
    "en": {
        "and_word": "and",
        "sentence1": "{crop} is recommended because the current soil and climate conditions closely match its optimal growth requirements.",
        "sentence1_fallback": "{crop} is recommended based on the provided soil and climate parameters.",
        "sentence2": "{primary_factors} strongly support {crop} cultivation{secondary_factors}",
        "sentence2_secondary": ", while {secondary_list} also contribute positively.",
        "sentence2_none": " levels.",
        "sentence3_two": "Other crops such as {alt0} and {alt1} were evaluated, but their optimal temperature and rainfall requirements are less compatible with the current environment.",
        "sentence3_one": "Another crop such as {alt0} was evaluated, but its optimal requirements are less compatible with the current environment.",
        "sentence3_none": ""
    }
}


def _impact_label(value: float) -> str:
    abs_v = abs(value)
    sign = "positive" if value > 0 else "negative"
    if abs_v >= 0.3:
        return f"strong {sign}"
    elif abs_v >= 0.1:
        return sign
    else:
        return f"moderate {sign}"


def explain(features: dict, pred_class_idx: int, crop: str, top_crops: list, lang: str = "en") -> tuple:
    """
    Returns:
        top_factors: list of {"feature": str, "impact": str}
        explanation_text: str
        shap_values_for_class: list of {"feature": str, "value": float} (for chart)
    """
    X = np.array([[features[f] for f in FEATURE_ORDER]])

    # shap_values shape: (n_classes, n_samples, n_features) for RF
    shap_vals = EXPLAINER.shap_values(X)

    # For multi-class RF, shap_values is a list of arrays or a 3D array
    if isinstance(shap_vals, list):
        class_shap = shap_vals[pred_class_idx][0]  # shape (n_features,)
    else:
        # newer shap versions return (n_samples, n_features, n_classes)
        if len(shap_vals.shape) == 3:
            class_shap = shap_vals[0, :, pred_class_idx]
        elif len(shap_vals.shape) == 2:
            class_shap = shap_vals[0]
        else:
            class_shap = shap_vals

    # Pair features with shap values
    pairs = list(zip(FEATURE_ORDER, class_shap))
    # Sort by absolute value descending
    pairs_sorted = sorted(pairs, key=lambda x: abs(x[1]), reverse=True)
    top3 = pairs_sorted[:3]

    if lang not in ["en", "te", "hi"]:
        lang = "en"
    labels_dict = FEATURE_LABELS[lang]
    t_dict = TRANSLATIONS[lang]
    crop_dict = CROP_NAMES.get(lang, {})

    top_factors = [
        {"feature": FEATURE_LABELS["en"].get(f, f), "impact": _impact_label(v)}
        for f, v in top3
    ]

    # Build readable explanation using SHAP contributors
    positive_features = [labels_dict.get(f, f) for f, v in pairs_sorted if v > 0]
    
    crop_display = crop_dict.get(crop.lower(), crop.capitalize())
    
    if len(positive_features) >= 2:
        primary_factors = f"{positive_features[0]} {t_dict['and_word']} {positive_features[1].lower()}"
        secondary = positive_features[2:]
        if secondary:
            secondary_str = f" {t_dict['and_word']} ".join([f.lower() for f in secondary])
            secondary_factors = t_dict["sentence2_secondary"].format(secondary_list=secondary_str)
        else:
            secondary_factors = t_dict["sentence2_none"]
        
        sentence1 = t_dict["sentence1"].format(crop=crop_display)
        sentence2 = t_dict["sentence2"].format(primary_factors=primary_factors, crop=crop_display.lower(), secondary_factors=secondary_factors)
    else:
        sentence1 = t_dict["sentence1_fallback"].format(crop=crop_display)
        sentence2 = ""

    alternatives = [crop_dict.get(item["crop"].lower(), item["crop"].capitalize()) for item in top_crops if item["crop"] != crop]
    if len(alternatives) >= 2:
        sentence3 = t_dict["sentence3_two"].format(alt0=alternatives[0].lower(), alt1=alternatives[1].lower())
    elif len(alternatives) == 1:
        sentence3 = t_dict["sentence3_one"].format(alt0=alternatives[0].lower())
    else:
        sentence3 = t_dict["sentence3_none"]
        
    explanation_text = f"{sentence1}\n\n{sentence2}\n\n{sentence3}".strip()

    # Full SHAP values for bar chart (researcher view)
    shap_chart = [
        {"feature": FEATURE_LABELS["en"].get(f, f), "value": float(round(v, 4))}
        for f, v in pairs_sorted
    ]

    return top_factors, explanation_text, shap_chart
