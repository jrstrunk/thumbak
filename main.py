import tomllib
import pathlib
import src.downscale_image as image
import src.downscale_video as video
import src.extract_faces as extract_faces
import src.embed_details as embed_details
import src.generate_description as generate_description
import src.form_metadata as form_metadata
import src.determine_date as determine_date
import PIL as pillow

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
for i, f in enumerate(files):
    print(f"{f['input']} -> ", end="")

    if f['input'].suffix.lower() in config['accepted_image_formats']:
        input_image = pillow.Image.open(f['input'])

        img_date = determine_date.from_image(input_image, f['input'])

        img_filename = (img_date or str(i)) + ".webp"
        print(img_filename)

        img_description = generate_description.for_image(input_image)

        downscaled_image = image.downscale(
            input_image,
            config['image-output']['target_size'],
        )

        faces = extract_faces.from_image(f['input'])

        metadata: bytes = form_metadata.from_image(
            input_image, 
            img_description, 
            [faces["xywh"] for faces in faces],
            config['image-output']['user_metadata_tags'],
        )

        image_with_emdeded_data: bytes = embed_details.into_image(
            downscaled_image, 
            [faces["img"] for faces in faces],
            config['image-output']['quality'],
            metadata,
        )

        # Save the combined data as a new WebP file
        with open(f["output"].with_name(img_filename), "wb") as f:
            f.write(image_with_emdeded_data)

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
