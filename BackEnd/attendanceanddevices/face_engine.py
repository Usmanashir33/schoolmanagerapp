# face_engine.py
from deepface import DeepFace

print("Loading face model...")
model_name="Facenet"
detector_backend="opencv"
def model () :
    model =DeepFace.build_model(model_name)  # loads once and faster than VGG
    return model

print("Model loaded successfully.")