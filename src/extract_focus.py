import src.convert as convert

def from_image(image, percent, quality):
    # Calculate the xywh of the focus crops to make an "oval" shape 
    # out of two large rectangles (cropped into three so they don't overlap) 
    # in the center of the image, like this for a vertical image:
    #
    # ---------------
    # -----&@@@&-----
    # -----@@@@@-----
    # ---&$$$$$$$&---
    # ---$$$$$$$$$---
    # ---$$$$$$$$$---
    # ---$$$$$$$$$---
    # ---&$$$$$$$&---
    # -----%%%%%-----
    # -----&%%%&-----
    # ---------------
    # 
    # Or like this for a horizontal image:
    #
    # ------------------------
    # ------&$$$$$$$$$$&------
    # --&@@@$$$$$$$$$$$$%%%&--
    # --&@@@$$$$$$$$$$$$%%%&--
    # ------&$$$$$$$$$$&------
    # ------------------------
    #
    # Where "@", "$", and "%" are the three different focus crops and "&" 
    # represents a corner of one of the two large rectangles. For
    # compression I think we want to have as square crops as possible, but
    # this could be tested.

    width, height = image.size

    horizontal_crop_width = int(width * (percent / 100))
    vertical_crop_height = int(height * (percent / 100))

    vertical_crop_width = int(horizontal_crop_width * 0.67)
    horizontal_crop_hight = int(vertical_crop_height * 0.67)

    horizontal_crop = (
        (width - horizontal_crop_width) // 2,
        (height - horizontal_crop_hight) // 2,
        horizontal_crop_width,
        horizontal_crop_hight,
    )

    vertical_crop = (
        (width - vertical_crop_width) // 2,
        (height - vertical_crop_height) // 2,
        vertical_crop_width,
        vertical_crop_height,
    )

    # Depending on the image orientation, cut one of the two large rectangle
    # crops in two smaller rectangles so there is no overlap between any of
    # them. This should leave us with three focus crops.
    if width > height:
        focus_xywhs = __split_rectangle(vertical_crop, horizontal_crop) \
            + [vertical_crop]
    else:
        focus_xywhs = __split_rectangle(horizontal_crop, vertical_crop) \
            + [horizontal_crop]

    return [
        {
            "img": image.crop(convert.xywh_to_pil_rect(rect)),
            "xywh": rect,
            "quality": quality,
        }
        for rect in focus_xywhs
    ]

def __split_rectangle(rect1, rect2):
    """Splits a rectangle into pieces that do not overlap the second rectangle"""
    def overlap(a, b):
        return max(a[0], b[0]), min(a[1], b[1])

    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

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

    return result
