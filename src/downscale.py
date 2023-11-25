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

