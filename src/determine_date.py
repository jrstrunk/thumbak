import PIL
import dateparser
import pathlib
from datetime import datetime
import os
import re
import itertools

def from_image(image, file_path: pathlib.Path) -> str: 
    file_date, file_offset = from_photo_metadata(image)

    if not file_date:
        file_date, file_offset = from_file_name(file_path)
    
    if not file_date:
        file_date, file_offset = from_sys_file_times(file_path)

    if not file_date:
        return None

    if not file_offset:
        file_offset = ""

    return file_date.replace(" ", "").replace(":", "").replace("-", "")\
        + __shorten_offset(file_offset.replace(":", ""))

def __shorten_offset(offset: str):
    if offset[-2:] == "00":
        offset = offset[:-2]
        if offset[:2] == "-0":
            return "-" + offset[2:3]
        if offset[:2] == "+0":
            return "+" + offset[2:3]
    return offset


def from_photo_metadata(image):
    """Photo metadata often stores the time in Local Time"""
    exif_data = __get_image_exif_data(image)

    try:
        for datetimeTag in ["Creation Time", "CreationTime", "DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
            img_date = image.info.get(datetimeTag) or exif_data.get(datetimeTag)

            if img_date:
                for offsetTag in ["Offset Time", "OffsetTime", "OffsetTimeOriginal", "OffsetTimeDigitized"]:
                    img_offset = image.info.get(offsetTag) or exif_data.get(offsetTag)

                    if img_offset:
                        try:
                            file_date = dateparser.parse(
                                img_date + img_offset,
                            )
                            return file_date.strftime("%Y%m%d%H%M%S"), \
                                file_date.strftime("%z")

                        except:
                            pass

                        return img_date, img_offset

                try:
                    file_date = dateparser.parse(img_date)
                    return file_date.strftime("%Y%m%d%H%M%S"), None

                except:
                    pass

                return img_date, None
    except:
        pass

    return None, None

def __get_image_exif_data(image):
    exif_data = image._getexif()

    if not exif_data:
        return {}

    return {
        PIL.ExifTags.TAGS.get(tag, tag): val for tag, val in exif_data.items()
    }

def from_file_name(file_name: pathlib.Path):
    file_name = file_name.stem

    possible_date_formats = []

    delimiters = ["", " ", "-", "_", ".", " AT ", " at "]
    sub_delimiters = ["", "-", "_", ".", " "]
    # the empty period must be last or else it will match dates with a period
    # before the appropiate period has had a chance to
    periods = [" AM", " PM", " am", " pm", "AM", "PM", "am", "pm", ""]

    # generate regex and datetime format for each possible date format that
    # has the same sub delimiter for each block, eg. "2024-01-21 09.36.10"
    date_format_quadruple_tuples = \
        itertools.product(sub_delimiters, delimiters, sub_delimiters, periods)

    for sub_delim1, delim, sub_delim2, period in date_format_quadruple_tuples:
        if not period:
            hour_code = "%H"
            period_code = ""
        elif " " in period:
            hour_code = "%I"
            period_code = " %p"
        else:
            hour_code = "%I"
            period_code = "%p"

        # account for an all digit date
        possible_date_formats.append({
            "regex": f"\\d\\d\\d\\d{sub_delim1}\\d\\d{sub_delim1}\\d\\d{delim}\\d\\d{sub_delim2}\\d\\d{sub_delim2}\\d\\d{period}".replace(".", "\\."),
            "format": f"%Y{sub_delim1}%m{sub_delim1}%d{delim}{hour_code}{sub_delim2}%M{sub_delim2}%S{period_code}",
        })
        # account for a date with short month name
        possible_date_formats.append({
            "regex": f"\\d\\d\\d\\d{sub_delim1}[A-Za-z][A-Za-z][A-Za-z]{sub_delim1}\\d\\d{delim}\\d\\d{sub_delim2}\\d\\d{sub_delim2}\\d\\d{period}".replace(".", "\\."),
            "format": f"%Y{sub_delim1}%b{sub_delim1}%d{delim}{hour_code}{sub_delim2}%M{sub_delim2}%S{period_code}",
        })

    # generate regex and datetime format for each possible date format that
    # has the h,m,s delimiters for the time block
    date_format_triple_tuples = \
        itertools.product(sub_delimiters, delimiters, periods)

    for sub_delim1, delim, period in date_format_triple_tuples:
        if not period:
            hour_code = "%H"
            period_code = ""
        elif " " in period:
            hour_code = "%I"
            period_code = " %p"
        else:
            hour_code = "%I"
            period_code = "%p"

        # account for an all digit date
        possible_date_formats.append({
            "regex": f"\\d\\d\\d\\d{sub_delim1}\\d\\d{sub_delim1}\\d\\d{delim}\\d\\dh\\d\\dm\\d\\ds{period}".replace(".", "\\."),
            "format": f"%Y{sub_delim1}%m{sub_delim1}%d{delim}{hour_code}h%Mm%Ss{period_code}",
        })
        # account for a date with short month name
        possible_date_formats.append({
            "regex": f"\\d\\d\\d\\d{sub_delim1}[A-Za-z][A-Za-z][A-Za-z]{sub_delim1}\\d\\d{delim}\\d\\dh\\d\\dm\\d\\ds{period}".replace(".", "\\."),
            "format": f"%Y{sub_delim1}%d{sub_delim1}%d{delim}{hour_code}h%Mm%Ss{period_code}",
        })

    # Generate the regex and datetime format for each possible date format that
    # only has the date, eg. "2011.08.24". Since the all digits version (not
    # the short month name version) is so few digits to match, this can result 
    # in a lot of false positives. To reduce the chance of a false positive, 
    # this only allows for the all digit date to match at the very beginning 
    # or end of the file name and enforces that the characters  right after 
    # or before it are word boundaries
    date_format_singles = sub_delimiters

    for sub_delim1 in date_format_singles:
        # account for an all digit date at the beginning of the file name
        possible_date_formats.append({
            "regex": f"^\\d\\d\\d\\d{sub_delim1}\\d\\d{sub_delim1}\\d\\d\\b".replace(".", "\\."),
            "format": f"%Y{sub_delim1}%m{sub_delim1}%d",
        })
        possible_date_formats.append({
            "regex": f"^\\d\\d\\d\\d{sub_delim1}\\d\\d{sub_delim1}\\d\\d_".replace(".", "\\."), # underscore is not a word boundry but we want to allow it
            "format": f"%Y{sub_delim1}%m{sub_delim1}%d_",
        })
        # account for an all digit date at the end of the file name
        possible_date_formats.append({
            "regex": f"\\b\\d\\d\\d\\d{sub_delim1}\\d\\d{sub_delim1}\\d\\d$".replace(".", "\\."),
            "format": f"%Y{sub_delim1}%m{sub_delim1}%d",
        })
        possible_date_formats.append({
            "regex": f"_\\d\\d\\d\\d{sub_delim1}\\d\\d{sub_delim1}\\d\\d$".replace(".", "\\."),  # underscore is not a word boundry but we want to allow it
            "format": f"_%Y{sub_delim1}%m{sub_delim1}%d",
        })
        # account for a date with short month name
        possible_date_formats.append({
            "regex": f"\\d\\d\\d\\d{sub_delim1}[A-Za-z][A-Za-z][A-Za-z]{sub_delim1}\\d\\d".replace(".", "\\."),
            "format": f"%Y{sub_delim1}%b{sub_delim1}%d",
        })

    for date_format in possible_date_formats:
        matches = re.findall(f"(?=({date_format['regex']}))", file_name)
        for match in matches:
            try:
                file_date = datetime.strptime(match, date_format["format"])
                return file_date.strftime("%Y%m%d%H%M%S"), \
                    file_date.strftime("%z")

            # if this throws an error, then the "date" being parsed was not 
            # a valid date, so continue in the loop
            except:
                pass

    return None, None

def from_sys_file_times(file_path: pathlib.Path):
    """This is dangerous!"""
    # get the file modified date
    file_date = datetime.fromtimestamp(os.path.getmtime(os.fspath(file_path)))
    return file_date.strftime("%Y%m%d%H%M%S"), \
        file_date.strftime("%z")