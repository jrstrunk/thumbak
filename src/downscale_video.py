import subprocess

def downscale_video(input_file: str, output_file: str, file_num: int, crf: int, target_size: int, webm: bool = False):
    '''Uses "aac" audio encoding for .mp4 and "libopus" for .webm. Idk 
        what to do about other encodings or what they are rn'''
    audio_encoding = "libopus" if webm else "aac"

    # https://stackoverflow.com/questions/3548673/how-can-i-replace-or-strip-an-extension-from-a-filename-in-python
    split_filename = os.path.splitext(output_file)
    ext = ".webm" if webm else split_filename[1]

    # Add the file number to the output file name
    output_file = f"{split_filename[0]}_{file_num}{ext}"

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
        "-c:v", "libx265",
        "-crf", str(crf),
        "-b:v", "16k",
        "-c:a", audio_encoding,
        "-b:a", "16k",
        "-y",
        output_file
    ]
    subprocess.run(command, check=True)

# dump #####################################################################
import subprocess

def downscale_video(input_file, output_file, crf, target_size):
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
        "-c:v", "libx265",
        "-crf", str(crf),
        "-b:v", "16k",
        "-c:a", "aac",
        "-b:a", "16k",
        "-y",
        output_file
    ]
    subprocess.run(command, check=True)

downscale_video("size_test_input/VID_20210812_201440.mp4", "size_test_output/VID_20210812_201440.mp4", 40, 192)

def downscale_webm(input_file, output_file, crf, target_size):
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
        "-crf", str(crf),
        "-b:v", "16k",
        "-c:a", "libopus",
        "-b:a", "16k",
        "-y",
        output_file
    ]
    subprocess.run(command, check=True)

downscale_webm("size_test_input/VID_20210812_201440.mp4", "size_test_output/VID_20210812_201440.webm", 40, 192)
