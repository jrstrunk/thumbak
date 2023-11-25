from PIL import Image
from pathlib import Path

def __convert_to_webp(source):
    destination = source.with_suffix(".webp")
    image = Image.open(source)
    image.save(destination, format="webp")
    return destination

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
    # image_with_reduced_color_depth = image.convert("P", palette=Image.ADAPTIVE, colors=256)
    # return image_with_reduced_color_depth
    return image

def __save_image_with_reduced_quality(image, destination, quality):
    image.save(destination, format="webp", quality=quality)
    return destination

def image(source, dest, size, quality):
    # Open the image
    image = Image.open(source)

    # Resize the image
    image = __resize_image(image, size)

    # Reduce the color depth of the image
    image = __reduce_color_depth(image)

    # Save the image in WebP format with reduced quality
    destination = dest.with_suffix(".webp")
    __save_image_with_reduced_quality(image, destination, quality)

def video(input_file, output_file, target_size):
    # Command to get the video dimensions
    command = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0', 
        '-show_entries', 'stream=width,height', 
        '-of', 'csv=s=x:p=0', 
        input_file,
    ]
    output = subprocess.check_output(command).decode('utf-8')
    width, height = map(int, output.strip().split('x'))

    # Determine the scale parameters
    if width < height:
        scale = f'{target_size}:-2'
    else:
        scale = f'-2:{target_size}'

    command = [
        "ffmpeg",
        "-i", input_file,
        "-vf", f"scale={scale}",
        "-r", "3",
        "-c:v", "libvpx-vp9",
        "-crf", "40",
        "-b:v", "16k",
        "-c:a", "libopus",
        "-b:a", "16k",
        "-y",
        output_file
    ]
    subprocess.run(command, check=True)

