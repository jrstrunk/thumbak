import PIL
import io

def into_image(
    original_img,
    faces_to_embed: list,
    focus_points_to_embed: list,
    details_to_embed: list,
    quality: int,
    exif_data: bytes,
):   
    # Save the image to an in-memory buffer
    original_buffer = io.BytesIO()

    # This will strip all metadata from the image
    baseline_image = PIL.Image.new(original_img.mode, original_img.size)
    baseline_image.putdata(list(original_img.getdata()))

    baseline_image.save(
        original_buffer, 
        format="AVIF", 
        quality=quality, 
    )

    combined_data = original_buffer.getvalue()

    # Append the metadata after the original image
    # combined_data += b'TBEMBEDv1' + exif_data

    # Append each face image to embed
    for face_to_embed in faces_to_embed:
        # Convert embed image to WebP format
        embed_buffer = io.BytesIO()

        # This will strip all metadata from the image
        face = PIL.Image.new(face_to_embed["img"].mode, face_to_embed["img"].size)
        face.putdata(list(face_to_embed["img"].getdata()))

        face.save(
            embed_buffer, 
            format="AVIF", 
            quality=face_to_embed["quality"],
        )
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data 

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
        new_image = PIL.Image.new(detail_to_embed.mode, detail_to_embed.size)
        new_image.putdata(list(detail_to_embed.getdata()))

        new_image.save(
            embed_buffer,
            format="AVIF",
            quality=60,
        )
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data 

    return combined_data
