from retinaface import RetinaFace
import PIL as pillow
import PIL
import numpy as np
import cv2

# Build the model and store it in memory once when this module is 
# first imported
RetinaFace.build_model()

def from_image(pil_img: PIL.Image) -> list:
    # retinaface was made to work with CV2 images, so we need to convert
    # pillow images to the CV2 format
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    faces = __retinaface_extract_faces(img, expand_face_area=10)

    # retinaface was made to work with CV2 images, so we need to convert
    # them to pillow images
    return [
        {"img": pillow.Image.fromarray(face["img"]), "xywh": face["xywh"]} 
        for face in faces
    ]

# A modification of the retinaface package's extract_faces function so that
# it will return the cropped faces and also the cooordinates of the face
def __retinaface_extract_faces(
    img: np.ndarray,
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
    
        # If the smallest dimension of the face is less than 8% of the
        # smallest dimension of the image, then expand the face area to 
        # try and include the entire body since this is a far away shot
        face_w = min(w, h)
        face_h = max(w, h)
        if face_w / min(img.shape[0], img.shape[1]) < 0.08:
            # Move the left edge of the area by 1.5x the face width
            x = int(max(0, x - (face_w * 1.5)))
            # Move the right edge of the area by 1.5x the face width
            w = int(min(img.shape[1], face_w + (face_w * 3)))
            # Move the top edge of the area by 0.75x the face width
            y = int(max(0, y - (face_w * 0.75)))
            # Move the bottom edge of the area by 9x the face width to
            # include the entire body
            h = int(min(img.shape[0], face_h + (face_w * 11)))

        facial_img = img[y : y + h, x : x + w]

        resp.append(
            {"img": facial_img[:, :, ::-1], "xywh": (x, y, w, h)}
        )

    return resp
