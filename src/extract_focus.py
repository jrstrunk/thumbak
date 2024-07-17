import src.convert as convert

def from_image(image, percent, existing_crop_rects, quality):
    # Determine the smallest dimension
    width, height = image.size
    center_rect: tuple = __get_center_area(width, height, int(percent * 0.9))

    # The center rectagle that represents the area of most focus
    center_rects = [center_rect]

    for existing_crop_rect in existing_crop_rects:
        for i, center_rect in enumerate(center_rects):
            # Replace the current center rect with the new rects after the
            # the existing rects where cut from it
            center_rects[i] = __cut_overlapping_rectangle(
                existing_crop_rect,
                center_rect,
            )
        center_rects = __flatten(center_rects)

    # Expanded areas around the center rectangle to capture non-center detail
    x, y, w, h = convert.pil_rect_to_xywh(center_rect)
    expanded_rects = [
        (x + w // 4, y - h // 4, x + int(w * 0.75), y), # Top area
        (x + w, y + h // 4, x + int(w * 1.25), y + int(h * 0.75)), # Right area 
        (x + w // 4, y + h, x + int(w * 0.75), y + int(h * 1.25)), # Bottom area
        (x - w // 4, y + h // 4, x, y + int(h * 0.75)), # Left area
    ]

    # Make sure all coords are within the image bounds
    expanded_rects = [__inbound(rect, width, height) for rect in expanded_rects]

    for existing_crop_rect in existing_crop_rects:
        for i, expanded_rect in enumerate(expanded_rects):
            # Replace the current center rect with the new rects after the
            # the existing rects where cut from it
            expanded_rects[i] = __cut_overlapping_rectangle(
                existing_crop_rect,
                expanded_rect,
            )
        expanded_rects = __flatten(expanded_rects)

    return [
        {
            "img": image.crop(rect),
            "xywh": convert.pil_rect_to_xywh(rect),
            "quality": int(quality * 0.80),
        }
        for rect in center_rects
    ] + [
        {
            "img": image.crop(rect),
            "xywh": convert.pil_rect_to_xywh(rect),
            "quality": int(quality * 0.20),
        }
        for rect in expanded_rects
    ]

def __get_center_area(width, height, percent):
    smallest_dimension = min(width, height)

    # Calculate the size of the square based on the percent of the 
    # smallest dimension
    square_size = int(smallest_dimension * (percent / 100))

    # Find the center of the image
    center_x = width // 2
    center_y = height // 2

    # Calculate the coordinates for cropping
    left = center_x - square_size // 2
    top = center_y - square_size // 2
    right = left + square_size
    bottom = top + square_size

    return left, top, right, bottom

def __cut_overlapping_rectangle(rect1, rect2):
    def overlap(a, b):
        return max(a[0], b[0]), min(a[1], b[1])

    x1, y1, w1, h1 = convert.pil_rect_to_xywh(rect1)
    x2, y2, w2, h2 = convert.pil_rect_to_xywh(rect2)

    # Check if there's any overlap
    x_overlap = overlap((x1, x1 + w1), (x2, x2 + w2))
    y_overlap = overlap((y1, y1 + h1), (y2, y2 + h2))

    if x_overlap[0] >= x_overlap[1] or y_overlap[0] >= y_overlap[1]:
        # No overlap, return the original rectangle
        return [rect2]

    result = []

    # Top piece
    if y2 < y_overlap[0]:
        result.append((x2, y2, w2, y_overlap[0] - y2))

    # Bottom piece
    if y_overlap[1] < y2 + h2:
        result.append((x2, y_overlap[1], w2, (y2 + h2) - y_overlap[1]))

    # Left piece
    if x2 < x_overlap[0]:
        result.append((
            x2, 
            y_overlap[0], 
            x_overlap[0] - x2, 
            y_overlap[1] - y_overlap[0],
        ))

    # Right piece
    if x_overlap[1] < x2 + w2:
        result.append((
            x_overlap[1], 
            y_overlap[0], 
            (x2 + w2) - x_overlap[1], 
            y_overlap[1] - y_overlap[0],
        ))

    return [convert.xywh_to_pil_rect(rect) for rect in result]

def __flatten(xss):
    """Flattens a list of lists into a single list of elements"""
    return [x for xs in xss for x in xs]

def __inbound(ltrb, img_width, img_height):
    return (
        max(ltrb[0], 0),
        max(ltrb[1], 0),
        min(ltrb[2], img_width),
        min(ltrb[3], img_height),
    )