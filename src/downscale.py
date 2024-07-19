import PIL as pillow
import pathlib
import os
import subprocess

def image(image, size: int):
    # Resize the image
    image = __resize_image(image, size)

    return image

def __resize_image(image, target_size):
    original_width, original_height = image.size

    if original_width > original_height:
        new_height = target_size
        new_width = int(target_size * (original_width / original_height))
    else:
        new_width = target_size
        new_height = int(target_size * (original_height / original_width))

    image.thumbnail((new_width, new_height), pillow.Image.Resampling.LANCZOS)

    return image

def __reduce_color_depth(image):
    # idk if this really helps
    # image_with_reduced_color_depth = image.convert("P", palette=Image.ADAPTIVE, colors=256)
    # return image_with_reduced_color_depth
    return image

def __convert_to_webp(source):
    """Just converts the image to webp"""
    destination = source.with_suffix(".webp")
    image = pillow.Image.open(source)
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
    resized_image = cropped_image.resize(
        target_size, pillow.Image.Resampling.LANCZOS
        )

    return resized_image

def video(
    input_path: pathlib.Path,
    output_path: pathlib.Path,
    target_size: int,
    frame_rate: int,
    crf: int,
    audio_bitrate: str,
):
    output_path = output_path.with_suffix(".webm")

    # Command to get the video dimensions
    command = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0', 
        '-show_entries', 'stream=width,height', 
        '-of', 'csv=s=x:p=0', 
        os.fspath(input_path),
    ]
    output = subprocess.check_output(command).decode('utf-8')
    width, height = map(int, output.strip().split('x'))

    # Determine the scale parameters
    if width < height:
        scale = f'{target_size}:-1'
    else:
        scale = f'-1:{target_size}'

    subprocess.run([
        "ffmpeg",
        "-i", os.fspath(input_path),
        "-vf", f"scale={scale}",
        "-r", str(frame_rate),
        "-c:v", "libvpx-vp9",
        "-crf", str(crf),
        "-c:a", "libopus",
        "-b:a", audio_bitrate,
        "-vbr", "on",
        "-compression_level", "10",
        "-y",
        os.fspath(output_path)
    ], 
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )