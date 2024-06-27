from PIL import Image
from pathlib import Path

def downscale(source, dest, size, quality):
    # Open the image
    image = Image.open(source)

    # Resize the image
    image = __resize_image(image, size)

    # Reduce the color depth of the image
    image = __reduce_color_depth(image)

    # Save the image in WebP format with reduced quality
    destination = dest.with_suffix(".webp")
    image.save(destination, format="webp", quality=quality)

def __resize_image(image, target_size):
    original_width, original_height = image.size

    if original_width > original_height:
        new_height = target_size
        new_width = int(target_size * (original_width / original_height))
    else:
        new_width = target_size
        new_height = int(target_size * (original_height / original_width))

    image.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

    return image

def __reduce_color_depth(image):
    # idk if this really helps
    # image_with_reduced_color_depth = image.convert("P", palette=Image.ADAPTIVE, colors=256)
    # return image_with_reduced_color_depth
    return image

def __convert_to_webp(source):
    """Just converts the image to webp"""
    destination = source.with_suffix(".webp")
    image = Image.open(source)
    image.save(destination, format="webp")
    return destination

def __resize_crop_image(image, target_size):
    """Don't think we want to ever crop an image, but this is here"""
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