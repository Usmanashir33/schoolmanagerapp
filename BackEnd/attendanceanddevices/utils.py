import base64
import uuid
import os
from django.conf import settings
import cv2
import numpy as np
from django.http import JsonResponse
from .face_engine import model
from deepface import DeepFace


def save_base64_image(base64_string, folder="faces_frames",folder_style = 'image', f_name = uuid.uuid4().hex):
    try:
        header, encoded = base64_string.split(",", 1)
    except ValueError:
        encoded = base64_string

    file_name = f"{f_name}.jpg"
    file_path = os.path.join(settings.MEDIA_ROOT, folder)

    os.makedirs(file_path, exist_ok=True)

    full_path = os.path.join(file_path, file_name)

    with open(full_path, "wb") as f:
        f.write(base64.b64decode(encoded))

    # Return URL path (important for frontend)
    imageFolderStyle = f"{folder}/{file_name}" # this is in image field style (without media/) auto 
    base64FolderStyle = f"/media/{folder}/{file_name}"
    return  imageFolderStyle if folder_style == 'image' else base64FolderStyle

def recognize_face(request):
    file = request.data.get('faceData')

    if not file:
        return JsonResponse({"error": "No image"}, status=400)
    # 🔥 Convert base64 → bytes
    if isinstance(file, str):
        # remove header if exists
        if "base64," in file:
            file = file.split("base64,")[1]

        file = base64.b64decode(file)

    # convert image
    img_array = np.frombuffer(file, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    try:
       
        faces = DeepFace.extract_faces(frame, detector_backend="opencv", enforce_detection=False, align=False,anti_spoofing=True)
        facial_area = faces[0]['facial_area'] if len(faces) > 0 else None
        x = facial_area['x'] if facial_area else None
        y = facial_area['y'] if facial_area else None
        w= facial_area['w'] if facial_area else None
        h = facial_area['h'] if facial_area else None
        # crop only the first detected face for visualization
        face = frame[y:y+h, x:x+w] if facial_area else None
        cv2.rectangle(face, (x, y), (x + w, y + h), (0, 255, 0), 2) if facial_area else None
        cv2.imshow('Detected Face', face)
        cv2.waitKey(0)
        print('faces: ', len(faces))

        # if len(result) > 0 and len(result[0]) > 0:
        #     identity = result[0]['identity'][0]
        #     name = identity.split("\\")[-1]

            # return JsonResponse({
            #     "status": "recognized",
            #     "name": name
            # })

        # return JsonResponse({"status": "unknown"})
        return faces # return all detected faces with their anti-spoofing results

    except Exception as e:
        print("Error recognizing face:", str(e))
        return JsonResponse({"error": str(e)}, status=500)