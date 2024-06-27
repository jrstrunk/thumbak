import tomllib
import pathlib
import os
import src.downscale_image as image
import src.downscale_video as video

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

def get_file_paths(source_dir, destination_dir):
    # Convert the input directories to Path objects
    source_path = pathlib.Path(source_dir)
    destination_path = pathlib.Path(destination_dir)

    # Check if the source directory exists
    destination_path.mkdir(parents=True, exist_ok=True)

    # Create the destination directory if it doesn't exist
    destination_path.mkdir(parents=True, exist_ok=True)

    # Get input to output objects for all files in the source directory 
    return [
        {"input": f, "output": destination_path / f.name} \
            for f in source_path.iterdir() \
            if f.is_file() \
            and (f.suffix.lower() in config['accepted_image_formats']
                or f.suffix.lower() in config['accepted_video_formats'])
    ]

files = get_file_paths("input", "output")

print(f"Files found in input directory:")
for f in files:
    print(f"{f['input']} -> {f['output']}")

for f in files:
    if f['input'].suffix.lower() in config['accepted_image_formats']:
        image.downscale(
            f['input'],
            f['output'],
            config['image-output']['target_size'],
            config['image-output']['quality']
        )

    elif f['input'].suffix.lower() in config['accepted_video_formats']:
        video.downscale(
            f['input'],
            f['output'],
            config['video-output']['crf'],
            config['video-output']['target_size'],
            config['video-output']['video_bitrate'],
            config['video-output']['audio_bitrate'],
            convert_to_webm = config['video-output']['format'] == ".webm"
        )
