import os
import joblib
import numpy as np

# Define paths to models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Define fallback mapping dictionaries for encoders trained on integers
CROP_DICT = {
    'barley': 0, 'cotton': 1, 'ground nuts': 2, 'maize': 3, 'millets': 4,
    'oil seeds': 5, 'paddy': 6, 'rice': 6, 'pulses': 7, 'sugarcane': 8,
    'tobacco': 9, 'wheat': 10
}
SOIL_DICT = {
    'black': 0, 'clayey': 1, 'loamy': 2, 'red': 3, 'sandy': 4
}

# Load models
try:
    fertilizer_model = joblib.load(os.path.join(MODELS_DIR, "fertilizer_model.pkl"))
    soil_encoder = joblib.load(os.path.join(MODELS_DIR, "soil_encoder.pkl"))
    crop_encoder = joblib.load(os.path.join(MODELS_DIR, "crop_encoder.pkl"))
    fertilizer_encoder = joblib.load(os.path.join(MODELS_DIR, "fertilizer_encoder.pkl"))
except Exception as e:
    print(f"Error loading fertilizer models: {e}")
    fertilizer_model = None
    soil_encoder = None
    crop_encoder = None
    fertilizer_encoder = None

def get_soil_type(ph: float) -> str:
    """Convert soil pH into soil type based on predefined rules."""
    if ph < 5.5:
        return "Red"
    elif 5.5 <= ph <= 6.5:
        return "Sandy"
    elif 6.5 < ph <= 7.5:
        return "Loamy"
    elif 7.5 < ph <= 8.5:
        return "Black"
    else:  # ph > 8.5
        return "Clayey"

def predict_fertilizer(temperature: float, humidity: float, N: float, P: float, K: float, ph: float, crop: str):
    """
    Predict top 3 recommended fertilizers based on crop and environmental conditions.
    """
    if fertilizer_model is None:
        raise RuntimeError("Fertilizer model could not be loaded")

    # 1. Convert pH to soil type
    soil_type = get_soil_type(ph)

    # 2. Encode categorical variables
    try:
        # Handle case variations and strip whitespace
        crop_clean = crop.lower().strip()
        soil_clean = soil_type.lower().strip()
        
        # Check explicit mapping because LabelEncoder was fitted on integers
        if crop_clean not in CROP_DICT:
            raise ValueError(f"Crop type '{crop}' is not recognized by the model.")
        if soil_clean not in SOIL_DICT:
            raise ValueError(f"Soil type '{soil_type}' is not recognized by the model.")
            
        crop_mapped = CROP_DICT[crop_clean]
        soil_mapped = SOIL_DICT[soil_clean]
        
        # Encoders are fitted on integers [0, 1, ..., N]. Passing the mapped int simply validates it.
        crop_encoded = crop_encoder.transform([crop_mapped])[0]
        soil_encoded = soil_encoder.transform([soil_mapped])[0]
        
    except ValueError as ve:
        raise ValueError(f"Encoding Error: {str(ve)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during encoding: {str(e)}")

    # 3. Create feature array: [temperature, humidity, soil_type_encoded, crop_type_encoded, N, P, K]
    # According to prompt: [temperature, humidity, soil_type_encoded, crop_type_encoded, N, P, K]
    features = np.array([[temperature, humidity, soil_encoded, crop_encoded, N, P, K]])

    # 4. Predict
    # Get probability scores for all classes
    try:
        probabilities = fertilizer_model.predict_proba(features)[0]
    except Exception as e:
         raise RuntimeError(f"Error during prediction: {str(e)}")

    # 5. Extract top 3 fertilizers
    # Get indices of the top 3 probabilities (sorted in descending order)
    top_3_indices = np.argsort(probabilities)[-3:][::-1]
    
    # 6. Decode back to fertilizer names
    try:
        top_3_fertilizers = fertilizer_encoder.inverse_transform(top_3_indices)
    except Exception as e:
        raise RuntimeError(f"Error decoding fertilizer names: {str(e)}")

    return list(top_3_fertilizers)
