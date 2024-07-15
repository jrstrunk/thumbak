import PIL
import io

def into_image(
    original_img, 
    images_to_embed: list, 
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

    # Append each image to embed
    for img_to_embed in images_to_embed:
        # Convert embed image to WebP format
        embed_buffer = io.BytesIO()
        img_to_embed.save(embed_buffer, format="WEBP", quality=90)
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data 

    return combined_data
