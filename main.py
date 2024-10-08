import os
import tomllib
import pathlib
import PIL
import src.convert as convert
import src.determine_date as determine_date
import src.downscale as downscale
import src.embed_details as embed_details
import src.extract_faces as extract_faces
import src.extract_focus as extract_focus
import src.extract_details as extract_details
import src.form_metadata as form_metadata
import src.generate_description as generate_description

def main():
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    files = get_file_paths("input", "output")

    print(f"Files found in input directory:")
    for i, f in enumerate(files):
        print(f"{f['input']} -> ", end="")

        if f['input'].suffix.lower() in config['accepted_image_formats']:
            try:
                input_image: PIL.Image = PIL.Image.open(f['input'])

                img_date: str = determine_date.from_image(input_image, f['input'])

                output_img_filename: str = (img_date or str(i)) + ".tinybackup.webp"
                f["output"] = get_unique_filename(
                    f["output"].with_name(output_img_filename)
                )

                baseline_image: PIL.Image = downscale.image(
                    input_image,
                    config['image-input']['baseline_size'],
                )

                faces: list = extract_faces.from_image(
                    baseline_image,
                    config['image-output']['face_quality'],
                )

                focus_points: list = extract_focus.from_image(
                    baseline_image,
                    config['image-output']['focus_percent'],
                    config['image-output']['focus_point_quality'],
                )

                details: list = extract_details.from_image(
                    baseline_image,
                    config['image-output']['detail_quality'],
                )

                metadata: bytes = form_metadata.from_image(
                    baseline_image, 
                    config['image-input']['baseline_size'],
                    [faces["xywh"] for faces in faces],
                    [focus_point["xywh"] for focus_point in focus_points],
                    config['image-output']['user_metadata_tags'],
                )

                tiny_image: PIL.Image = downscale.image(
                    baseline_image,
                    config['image-output']['target_size'],
                )

                image_with_emdeded_data: bytes = embed_details.into_image(
                    tiny_image, 
                    faces,
                    focus_points,
                    details,
                    metadata,
                    config,
                )

                # Save the combined data as a new WebP file
                with open(f["output"], "wb") as output:
                    output.write(image_with_emdeded_data)

            except Exception as e:
                print(f"Processing error:", e)
                continue
            
            print(f["output"])

        elif f['input'].suffix.lower() in config['accepted_video_formats']:
            downscale.video(
                f['input'],
                f['output'],
                config['video-output']['target_size'],
                config['video-output']['frame_rate'],
                config['video-output']['crf'],
                config['video-output']['audio_bitrate'],
            )

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

def get_unique_filename(file_path: pathlib.Path):
    # This needs to account for the .tinybackup.webp extension
    split_name = os.fspath(file_path).split(".")
    base = split_name[0]
    extension = split_name[2]
    counter = 1

    for _ in range(10000):
        if os.path.exists(file_path):
            file_path = f"{base}_{counter}.tinybackup.{extension}"
            counter += 1
        else:
            break

    return file_path

if __name__ == "__main__":
    main()