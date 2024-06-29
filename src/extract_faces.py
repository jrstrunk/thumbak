from retinaface import RetinaFace
import os
import PIL as pillow
import pathlib
import numpy as np
from typing import Union
import cv2

# Build the model and store it in memory once when this module is 
# first imported
RetinaFace.build_model()

def from_image(image_path: pathlib.Path) -> list:
    faces = __retinaface_extract_faces(
        os.fspath(image_path), 
        expand_face_area=4,
    )

    # retinaface was made to work with CV2 images, so we need to convert
    # them to pillow images
    return [
        {"img": pillow.Image.fromarray(face["img"]), "xywh": face["xywh"]} 
        for face in faces
    ]

# A modification of the retinaface package's extract_faces function so that
# it will return the cropped faces and also the cooordinates of the face
def __retinaface_extract_faces(
    img_path: Union[str, np.ndarray],
    threshold: float = 0.9,
    allow_upscaling: bool = True,
    expand_face_area: int = 0,
) -> list:
    """
    Extract detected and aligned faces
    Args:
        img_path (str or numpy): given image
        threshold (float): detection threshold
        model (Model): pre-trained model can be passed to the function
        align (bool): enable or disable alignment
        allow_upscaling (bool): allowing up-scaling
        expand_face_area (int): expand detected facial area with a percentage
    """
    resp = []

    img = cv2.imread(img_path)

    # Validate image shape
    if len(img.shape) != 3 or np.prod(img.shape) == 0:
        raise ValueError("Input image needs to have 3 channels at must not be empty.")

    obj = RetinaFace.detect_faces(
        img_path=img, threshold=threshold, model=None, allow_upscaling=allow_upscaling
    )

    if not isinstance(obj, dict):
        return resp

    for _, identity in obj.items():
        facial_area = identity["facial_area"]

        x = facial_area[0]
        y = facial_area[1]
        w = facial_area[2] - x
        h = facial_area[3] - y

        if expand_face_area > 0:
            expanded_w = w + int(w * expand_face_area / 100)
            expanded_h = h + int(h * expand_face_area / 100)

            # overwrite facial area
            x = max(0, x - int((expanded_w - w) / 2))
            y = max(0, y - int((expanded_h - h) / 2))
            w = min(img.shape[1] - x, expanded_w)
            h = min(img.shape[0] - y, expanded_h)

        facial_img = img[y : y + h, x : x + w]

        resp.append(
            {"img": facial_img[:, :, ::-1], "xywh": (x, y, w, h)}
        )

    return resp
