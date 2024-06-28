from retinaface import RetinaFace

RetinaFace.build_model()

def extract_faces(image_path):
    RetinaFace.extract_faces(
        image_path, 
        align=False,
        expand_face_area=4,
    )