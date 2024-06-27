import subprocess
import os
import pathlib

def downscale(
    input_file, 
    output_file, 
    crf: int, 
    target_size: int, 
    video_bitrate: str,
    audio_bitrate: str,
    convert_to_webm: bool = False
): 
    '''Uses "aac" audio encoding for .mp4 and "libopus" for .webm. Idk 
        what to do about other encodings or what they are rn'''
    if convert_to_webm:
        output_file = output_file.with_suffix(".webm")

    # Command to get the video dimensions
    command = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0', 
        '-show_entries', 'stream=width,height', 
        '-of', 'csv=s=x:p=0', 
        os.fspath(input_file),
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
        "-c:v", "libvpx-vp9" if convert_to_webm else "libx265",
        "-crf", str(crf),
        "-b:v", video_bitrate,
        "-c:a", "libopus" if convert_to_webm else "aac",
        "-b:a", audio_bitrate,
        "-y",
        os.fspath(output_file)
    ]
    subprocess.run(command, check=True)
