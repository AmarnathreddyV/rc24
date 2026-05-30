import pytesseract
from PIL import Image
import re


def read_scores(path):
    img = Image.open(path)

    text = pytesseract.image_to_string(img)

    nums = re.findall(r"\d+", text)

    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])

    return None, None