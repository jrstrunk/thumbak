import PIL
from PIL.ExifTags import TAGS
import piexif

# Keeping all the original exif data of an average camera photo leads to 
# 3x larger files, so we only want to preserve the description data or data
# the user explicitly specified to keep. The datetime data is important too 
# but is extracted in a different way.
# See https://exiv2.org/tags.html for information on all exif tags.
def from_image(image: PIL.Image, added_desc: str, user_tags_to_keep: list[int]):
    exif_data = __get_image_exif_data(image)

    comment = exif_data.get('UserComment', None)

    img_desc = bytes(exif_data.get('ImageDescription', ""), "utf-8") \
        + b"tbdv1" \
        + bytes(added_desc, "utf-8")

    exif_dict = {
        "0th": {},
        "Exif": {},
    }

    exif_dict['0th'][piexif.ImageIFD.ImageDescription] = img_desc

    if comment:
        exif_dict['Exif'][piexif.ExifIFD.UserComment] = comment

    exif_bytes = piexif.dump(exif_dict)

    return exif_bytes

def __get_image_exif_data(image):
    exif_data = image._getexif()
    if not exif_data:
        return {}
    exif = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
    return exif