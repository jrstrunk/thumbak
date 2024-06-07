from PIL import Image
from pathlib import Path
from downscale_image import downscale_image
from downscale_video import downscale_video, downscale_webm

def image(source, dest, size, quality):
    downscale_image(source, dest, 192, 25) # play around with these params

def video(input_file, output_file):
    downscale_video(input_file, output_file, 40, 192) # play around with these params
    downscale_webm(input_file, output_file, 40, 192) # play around with these params

