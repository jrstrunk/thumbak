from PIL import Image
from pathlib import Path

def convert_to_webp(source):
    destination = source.with_suffix(".webp")
    image = Image.open(source)
    image.save(destination, format="webp")
    return destination

def resize_crop_image(image, target_size):
    original_width, original_height = image.size
    target_width, target_height = target_size

    original_aspect_ratio = original_width / original_height
    target_aspect_ratio = target_width / target_height

    if original_aspect_ratio > target_aspect_ratio:
        new_width = int(original_height * target_aspect_ratio)
        offset = (original_width - new_width) / 2
        resize_box = (offset, 0, original_width - offset, original_height)
    else:
        new_height = int(original_width / target_aspect_ratio)
        offset = (original_height - new_height) / 2
        resize_box = (0, offset, original_width, original_height - offset)

    cropped_image = image.crop(resize_box)
    resized_image = cropped_image.resize(target_size, Image.Resampling.LANCZOS)

    return resized_image

def resize_image(image, target_size):
    original_width, original_height = image.size

    if original_width > original_height:
        new_height = target_size
        new_width = int(target_size * (original_width / original_height))
    else:
        new_width = target_size
        new_height = int(target_size * (original_height / original_width))

    image.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

    return image

def reduce_color_depth(image):
    # idk if this really helps
    # image_with_reduced_color_depth = image.convert("P", palette=Image.ADAPTIVE, colors=256)
    # return image_with_reduced_color_depth
    return image

def save_image_with_reduced_quality(image, destination, quality):
    image.save(destination, format="webp", quality=quality)
    return destination

def convert_image(source, dest, size, quality):
    # Open the image
    image = Image.open(source)

    # Resize the image
    image = resize_image(image, size)

    # Reduce the color depth of the image
    image = reduce_color_depth(image)

    # Save the image in WebP format with reduced quality
    destination = dest.with_suffix(".webp")
    save_image_with_reduced_quality(image, destination, quality)

    return destination

# # Example usage:
# convert_image(Path("example2.jpg"), (256, 212), 50)

import os
import shutil

input_dir = 'size_test_input'
output_dir = 'size_test_output'

for dirpath, dirnames, filenames in os.walk(input_dir):
    structure = os.path.join(output_dir, os.path.relpath(dirpath, input_dir))
    if not os.path.isdir(structure):
        os.mkdir(structure)
    for file in filenames:
        src_file = os.path.join(dirpath, file)
        dst_file = os.path.join(structure, file)
        convert_image(Path(src_file), Path(dst_file), 192, 25)