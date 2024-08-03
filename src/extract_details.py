import PIL

def from_image(image: PIL.Image):
    width, height = image.size

    calculate_details_coords(width, height)

    return [
        image.crop(coord)
        for coord in calculate_details_coords(width, height)
    ]

def calculate_details_coords(width, height):
    detail_crop_size = 64
    half_crop = detail_crop_size // 2

    smallest_dimension = min(width, height)

    # Define the centers of each quadrant
    centers = [
        (smallest_dimension // 4, smallest_dimension // 4),          # Top-left quadrant center
        (width - (smallest_dimension // 4), smallest_dimension // 4),      # Top-right quadrant center
        (smallest_dimension // 4, height - (smallest_dimension // 4)),      # Bottom-left quadrant center
        (width - (smallest_dimension // 4), height - (smallest_dimension // 4))   # Bottom-right quadrant center
    ]

    coords = []
    for center in centers:
        left = center[0] - half_crop
        upper = center[1] - half_crop
        right = center[0] + half_crop
        lower = center[1] + half_crop
        coords.append((left, upper, right, lower))
    
    return coords