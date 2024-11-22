from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from utils.constants import CONTENT_WIDTH_LOWER_BOUND, CONTENT_WIDTH_UPPER_BOUND
from utils.shortcuts import rand_str
import os


class ContentUtil:

    @staticmethod
    def saveContentWithRandomFileName(content: object, save_path: str) -> str:
        suffix = os.path.splitext(content.name)[-1].lower()
        name = rand_str(10) + suffix

        content_path = os.path.join(save_path, name)
        os.makedirs(os.path.dirname(content_path), exist_ok=True)

        with open(content_path, "wb") as img:
            for chunk in content:
                img.write(chunk)
        return name

    @staticmethod
    def validateURL(link_url):
        if link_url is None:
            return "link_url is None"
        url_validator = URLValidator()
        try:
            url_validator(link_url)
        except ValidationError:
            return "Invalid URL"

        return None

    @staticmethod
    def validateImage(**kwargs):
        image = kwargs.get("image")
        width = kwargs.get("width")

        # 파일 크기 검사
        if image.size > 2 * 1024 * 1024:
            return "File is too large"

        # 파일 확장자 검사
        suffix = os.path.splitext(image.name)[-1].lower()
        if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return "Unsupported file format"

        # 이미지 넓이 유효성 검사
        if width is not None:
            if not (CONTENT_WIDTH_LOWER_BOUND <= width <= CONTENT_WIDTH_UPPER_BOUND):
                return f"Image width must be no less than {CONTENT_WIDTH_LOWER_BOUND}px and no more than {CONTENT_WIDTH_UPPER_BOUND}px."
        return None
