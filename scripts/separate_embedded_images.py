from PIL import Image
import io

def read_embedded_images(input_path):
    with open(input_path, "rb") as f:
        data = f.read()
    
    # Find all separators
    separator = b"TBEMBEDv1"
    separator_indices = [i for i in range(len(data)) if data.startswith(separator, i)]
    
    if not separator_indices:
        raise ValueError("No embedded images found")
    
    # Extract the original and embedded image data
    original_data = data[:separator_indices[0]]
    embedded_data_list = [data[start + len(separator):end] for start, end in zip(separator_indices, separator_indices[1:] + [None])]
    
    # Open the original image
    original_img = Image.open(io.BytesIO(original_data))
    
    # Open all embedded images
    embedded_imgs = [Image.open(io.BytesIO(img_data)) for img_data in embedded_data_list]
    
    return original_img, embedded_imgs

# Usage
original, embedded_list = read_embedded_images("output/20240529092231-4.tinybackup.webp")
original.save("concat_mulitple_original.webp")
for i, img in enumerate(embedded_list):
    img.save(f"concat_mulitple_embedded_{i+1}.webp")