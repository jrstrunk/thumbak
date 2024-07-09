def for_image(image):
    return __to_camel_case(
        "A young child dressed in a vibrant red sweater sits on a red plaid blanket, gazing upwards at a towering Christmas tree with a white sign attached to its top. The tree is surrounded by other trees, creating a natural and festive setting.",
    )

def __to_camel_case(text: str):
    '''Removes spaces and capitalizes the first letter of each work to 
        save bytes. 
        Ex. "This image is cool" -> "ThisImageIsCool"'''
    return text