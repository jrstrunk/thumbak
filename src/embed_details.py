import PIL
from PIL import Image, ImageDraw 
import io
import src.convert as convert

def into_image(
    original_img,
    faces_to_embed: list,
    focus_points_to_embed: list,
    details_to_embed: list,
    exif_data: bytes,
    config,
):
    # Add a green outline to the images in debug mode
    if config['debug']['enabled']:
        faces_to_embed, focus_points_to_embed, details_to_embed = apply_green_outline(
            faces_to_embed, focus_points_to_embed, details_to_embed
        )

    # Save the image to an in-memory buffer
    original_buffer = io.BytesIO()

    if config['image-output']['white_crops']:
        apply_white_crops_to_baseline(
            original_img,
            faces_to_embed + focus_points_to_embed + details_to_embed,
            config['image-output']['target_size'],
            config['image-input']['baseline_size'],
        )

        for focus_point in focus_points_to_embed:
            apply_white_crops_to_crops(
                focus_point,
                faces_to_embed,
            )

    # This will strip all metadata from the image
    baseline_image = PIL.Image.new(original_img.mode, original_img.size)
    baseline_image.putdata(list(original_img.getdata()))

    baseline_image.save(
        original_buffer, 
        format="AVIF", 
        quality=config['image-output']['quality'], 
    )

    combined_data = original_buffer.getvalue()

    # Append the metadata after the original image
    # combined_data += b'TBEMBEDv1' + exif_data


    # Append each focus point image to embed
    for focus_point_to_embed in focus_points_to_embed:
        # Convert embed image to WebP format
        embed_buffer = io.BytesIO()

        # This will strip all metadata from the image
        focus_point = PIL.Image.new(focus_point_to_embed["img"].mode, focus_point_to_embed["img"].size)
        focus_point.putdata(list(focus_point_to_embed["img"].getdata()))

        focus_point.save(
            embed_buffer,
            format="AVIF",
            quality=focus_point_to_embed["quality"],
        )
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data 

    # Append each detail image to embed
    for detail_to_embed in details_to_embed:
        # Convert embed image to WebP format
        embed_buffer = io.BytesIO()

        # This will strip all metadata from the image
        new_image = PIL.Image.new(detail_to_embed.mode, detail_to_embed["img"].size)
        new_image.putdata(list(detail_to_embed["img"].getdata()))

        new_image.save(
            embed_buffer,
            format="AVIF",
            quality=detail_to_embed["quality"],
        )
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data 

    # Append each face image to embed
    for face_to_embed in faces_to_embed:
        # Convert embed image to WebP format
        embed_buffer = io.BytesIO()

        new_image = PIL.Image.new(detail_to_embed.mode, detail_to_embed["img"].size)
        new_image.putdata(list(detail_to_embed["img"].getdata()))

        face_to_embed["img"].save(
            embed_buffer, 
            format="WEBP", 
            quality=face_to_embed["quality"],
        )
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data

    return combined_data

def apply_white_crops_to_baseline(image, list_of_crops, image_size, crop_baseline_size):
    """Replaces parts of an image with all white where a crop of that part of the
    image is saved in higher resolution. This saves space but makes the image
    more dependent on restoration processing to be recognizable."""
    for crop in list_of_crops:
        white_out_crop_space(
            image, 
            convert.shrink_xywh(
                convert.xywh_to_scale(crop["xywh"], image_size / crop_baseline_size), 
                by=5,
            ),
        )
    
def apply_white_crops_to_crops(lesser_crop, greater_crops):
    for greater_crop in greater_crops:
        overlap = get_overlap_coordinates(
            lesser_crop["xywh"], 
            convert.shrink_xywh(greater_crop["xywh"], by=5),
        )

        if not overlap:
            continue

        white_out_crop_space(lesser_crop["img"], overlap)

def get_overlap_coordinates(xywh1, xywh2):
    # Unpack the coordinates
    x1, y1, w1, h1 = xywh1
    x2, y2, w2, h2 = xywh2

    # Calculate the coordinates of the rectangles' edges
    left1, right1, top1, bottom1 = x1, x1 + w1, y1, y1 + h1
    left2, right2, top2, bottom2 = x2, x2 + w2, y2, y2 + h2

    # Check if rect1 is completely inside rect2
    if left2 <= left1 and right1 <= right2 and top2 <= top1 and bottom1 <= bottom2:
        return -1

    # Calculate the overlap
    overlap_left = max(left1, left2)
    overlap_top = max(top1, top2)
    overlap_right = min(right1, right2)
    overlap_bottom = min(bottom1, bottom2)

    # Check if there's no overlap
    if overlap_left >= overlap_right or overlap_top >= overlap_bottom:
        return None

    # Calculate the overlap width and height
    overlap_width = overlap_right - overlap_left
    overlap_height = overlap_bottom - overlap_top

    # Return the overlap coordinates relative to rect1
    return (overlap_left - x1, overlap_top - y1, overlap_width, overlap_height)


def white_out_crop_space(image, xywh: tuple[int, int, int, int]):
    """Replaces the crop space with white pixels"""
    draw = ImageDraw.Draw(image)
    draw.rectangle(convert.xywh_to_ltrb(xywh), fill='white')

def apply_green_outline(faces_to_embed, focus_points_to_embed, details_to_embed):
    fill = (0, 255, 0)
    faces_to_embed = [
        {
            "img": PIL.ImageOps.expand(f["img"], fill=fill, border=1),
            "quality": f["quality"],
            "xywh": f["xywh"],
        } for f in faces_to_embed
    ]

    focus_points_to_embed = [
        {
            "img": PIL.ImageOps.expand(p["img"], fill=fill, border=1),
            "quality": p["quality"],
            "xywh": p["xywh"],
        } for p in focus_points_to_embed
    ]

    details_to_embed = [
        PIL.ImageOps.expand(d, fill=fill, border=1)
        for d in details_to_embed
    ]

    return faces_to_embed, focus_points_to_embed, details_to_embed