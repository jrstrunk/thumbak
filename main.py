import tomllib
import pathlib
import os
import src.downscale_image as image
import src.downscale_video as video

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

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
