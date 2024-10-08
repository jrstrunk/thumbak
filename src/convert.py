def xywh_to_pil_rect(xywh: tuple[int, int, int, int]):
    return (xywh[0], xywh[1], xywh[0] + xywh[2], xywh[1] + xywh[3])

def xywh_to_ltrb(xywh: tuple[int, int, int, int]):
    return (xywh[0], xywh[1], xywh[0] + xywh[2], xywh[1] + xywh[3])

def pil_rect_to_xywh(rect: tuple[int, int, int, int]):
    return (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])

def ltrb_to_xywh(rect: tuple[int, int, int, int]):
    return (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])

def xywh_to_scale(xywh: tuple[int, int, int, int], scale: float):
    if scale == 1:
        return xywh
    return (
        int(xywh[0] * scale), 
        int(xywh[1] * scale), 
        int(xywh[2] * scale), 
        int(xywh[3] * scale),
    )

def shrink_xywh(xywh: tuple[int, int, int, int], by: int):
    return (xywh[0] + by, xywh[1] + by, xywh[2] - by * 2, xywh[3] - by * 2)

def expand_xywh(xywh: tuple[int, int, int, int], by: int):
    return (xywh[0] - by, xywh[1] - by, xywh[2] + by * 2, xywh[3] + by * 2)