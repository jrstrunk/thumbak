from PIL import Image
import io

def into_image(original_img, images_to_embed, quality):
    # Prepare the original image data
    original_buffer = io.BytesIO()
    original_img.save(original_buffer, format="WEBP", quality=quality)

    combined_data = original_buffer.getvalue()

    # Append each image to embed
    for img_to_embed in images_to_embed:
        # Convert embed image to WebP format
        embed_buffer = io.BytesIO()
        img_to_embed.save(embed_buffer, format="WEBP")
        embed_data = embed_buffer.getvalue()
        
        # Append the embed data with the separator
        combined_data += b"TBEMBEDv1" + embed_data 

    return combined_data
