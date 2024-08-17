import PIL
from PIL import Image
import os
import io
import pathlib
import re
import shutil

# This file has some duplicate functions with the main project src so it can
# be used as a standalone script to restore tinybackup images

def get_file_paths(source_dir, destination_dir):
    source_path = pathlib.Path(source_dir)
    destination_path = pathlib.Path(destination_dir)

    # Get all file paths recursively
    all_files = list(source_path.rglob('*'))

    outputs = []

    for file_path in all_files:
        if file_path.is_file():
            # Calculate the relative path
            relative_path = file_path.relative_to(source_path)

            # Create the new destination path
            new_path = destination_path / relative_path

            # Create the directory structure if it doesn't exist
            new_path.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            outputs.append({"input": file_path, "output": new_path})

    return outputs

def upscale_image(input_path, output_path):
    with open(input_path, "rb") as f:
        raw_data = f.read()
    
    # Find all image separators in the raw file data
    separator = b"TBEMBEDv1"
    separator_indices = [
        i for i in range(len(raw_data)) if raw_data.startswith(separator, i)
    ]

    # Extract the original and embedded image data
    original_data = raw_data[:separator_indices[0]]
    embedded_data_list = [
        raw_data[start + len(separator):end] 
        for start, end in zip(separator_indices, separator_indices[1:] + [None])
    ]
    
    # Open the original image
    tiny_img = Image.open(io.BytesIO(original_data))
    
    # Get the original dimensions and details coords
    width, height = tiny_img.size

    desc = get_image_exif_data(tiny_img).get("ImageDescription").split("tbdv1")[1]

    baseline_size = int(
        re.findall(r"b\d+", desc)[0].replace("b", "")
    )

    # Determine the scaling factor
    if width < height:
        scale_factor = baseline_size / width
    else:
        scale_factor = baseline_size / height

    # Calculate the new dimensions
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Resize the image
    resized_img = tiny_img.resize((new_width, new_height), PIL.Image.LANCZOS)

    # Overlay the details on the tiny image
    embedded_imgs = [
        PIL.Image.open(io.BytesIO(img_data)) for img_data in embedded_data_list
    ]

    details_coords = [
        parse_coords(coords.replace("p", ""))
        for coords in re.findall(r"p\d+,\d+,\d+,\d+", desc)
    ] + calculate_details_coords(new_width, new_height) + [
        parse_coords(coords.replace("f", ""))
        for coords in re.findall(r"f\d+,\d+,\d+,\d+", desc)
    ]

    for i, embedded_img in enumerate(embedded_imgs):
        resized_img.paste(embedded_img, (details_coords[i][0], details_coords[i][1]))

    # Save the resized image
    resized_img.save(os.fspath(output_path).replace("tinybackup", "tinyrestore"))

def get_image_exif_data(image):
    exif_data = image._getexif()

    if not exif_data:
        return {}

    return {
        PIL.ExifTags.TAGS.get(tag, tag): val for tag, val in exif_data.items()
    }

def parse_coords(coords):
    return tuple(int(coord) for coord in coords.split(","))

def calculate_details_coords(width, height):
    detail_crop_size = 64
    half_crop = detail_crop_size // 2

    smallest_dimension = min(width, height)

    # Define the centers of each quadrant
    centers = [
        (smallest_dimension // 4, smallest_dimension // 4),          # Top-left quadrant center
        (width - (smallest_dimension // 4), smallest_dimension // 4),      # Top-right quadrant center
        (smallest_dimension // 4, height - (smallest_dimension // 4)),      # Bottom-left quadrant center
        (width - (smallest_dimension // 4), height - (smallest_dimension // 4))   # Bottom-right quadrant center
    ]

    coords = []
    for center in centers:
        left = center[0] - half_crop
        upper = center[1] - half_crop
        right = center[0] + half_crop
        lower = center[1] + half_crop
        coords.append((left, upper, right, lower))
    
    return coords

def convert_pil_rect_to_xywh(rect: tuple[int, int, int, int]):
    return (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])

# Example usage
input_path = 'output'
output_path = 'restored'

all_files = get_file_paths(input_path, output_path)

for file in [f for f in all_files if f['input'].suffix.lower() == ".webp"]:
    upscale_image(file["input"], file["output"])

for file in [f for f in all_files if f['input'].suffix.lower() == ".webm"]:
    shutil.copy2(file["input"], file["output"])