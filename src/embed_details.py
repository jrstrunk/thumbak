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

    original_img.save(
        original_buffer, 
        format="WEBP", 
        quality=quality, 
        exif=exif_data or b"", # we can't just pass None, so pass an empty byte string instaed
    )

    combined_data = original_buffer.getvalue()

    # Append each face image to embed
    for face_to_embed in faces_to_embed:
        # Convert embed image to WebP format
        embed_buffer = io.BytesIO()
        face_to_embed["img"].save(
            embed_buffer, 
            format="WEBP", 
            quality=face_to_embed["quality"],
        )
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data 

    # Append each focus point image to embed
    for focus_point_to_embed in focus_points_to_embed:
        # Convert embed image to WebP format
        embed_buffer = io.BytesIO()
        focus_point_to_embed["img"].save(
            embed_buffer,
            format="WEBP",
            quality=focus_point_to_embed["quality"],
        )
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data 

    # Append each detail image to embed
    for detail_to_embed in details_to_embed:
        # Convert embed image to WebP format
        embed_buffer = io.BytesIO()
        detail_to_embed.save(
            embed_buffer,
            format="WEBP",
            quality=80,
        )
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data 

    return combined_data
