import os
import re
import random
from base64 import b64encode
from io import BytesIO
from typing import Any, Dict

from django.utils.crypto import get_random_string
from envelopes import Envelope

from utils.constants import Difficulty


def rand_str(length=32, type="lower_hex"):
    """
    生成指定长度的随机字符串或者数字, 可以用于密钥等安全场景
    :param length: 字符串或者数字的长度
    :param type: str 代表随机字符串，num 代表随机数字
    :return: 字符串
    """
    if type == "str":
        return get_random_string(length, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
    elif type == "lower_str":
        return get_random_string(length, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789")
    elif type == "lower_hex":
        return random.choice("123456789abcdef") + get_random_string(length - 1, allowed_chars="0123456789abcdef")
    else:
        return random.choice("123456789") + get_random_string(length - 1, allowed_chars="0123456789")


def build_query_string(kv_data, ignore_none=True):
    # {"a": 1, "b": "test"} -> "?a=1&b=test"
    query_string = ""
    for k, v in kv_data.items():
        if ignore_none is True and kv_data[k] is None:
            continue
        if query_string != "":
            query_string += "&"
        else:
            query_string = "?"
        query_string += (k + "=" + str(v))
    return query_string


def get_difficulty(difficulty_str):
    if difficulty_str is None:
        return Difficulty.MID

    difficulty_map = {
        "VeryLow": Difficulty.VERYLOW,
        "Low": Difficulty.LOW,
        "Mid": Difficulty.MID,
        "High": Difficulty.HIGH,
        "VeryHigh": Difficulty.VERYHIGH
    }

    return difficulty_map.get(difficulty_str, Difficulty.MID)


def img2base64(img):
    with BytesIO() as buf:
        img.save(buf, "gif")
        buf_str = buf.getvalue()
    img_prefix = "data:image/png;base64,"
    b64_str = img_prefix + b64encode(buf_str).decode("utf-8")
    return b64_str


def datetime2str(value, format="iso-8601"):
    if format.lower() == "iso-8601":
        value = value.isoformat()
        if value.endswith("+00:00"):
            value = value[:-6] + "Z"
        return value
    return value.strftime(format)


def natural_sort_key(s, _nsre=re.compile(r"(\d+)")):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]


def send_email(smtp_config, from_name, to_email, to_name, subject, content):
    envelope = Envelope(from_addr=(smtp_config["email"], from_name),
                        to_addr=(to_email, to_name),
                        subject=subject,
                        html_body=content)
    return envelope.send(smtp_config["server"],
                         login=smtp_config["email"],
                         password=smtp_config["password"],
                         port=smtp_config["port"],
                         tls=smtp_config["tls"])


def get_env(name, default=""):
    return os.environ.get(name, default)


def CELERY_TASK_ARGS(
    max_retries: int = 0,
    time_limit: int = 3600,
    soft_time_limit: int = 3600,
) -> Dict[str, Any]:
    """Returns a dictionary of arguments for Celery tasks.

    Args:
        max_retries: Maximum number of retries for the task.
        time_limit: Hard time limit for the task in seconds.
        soft_time_limit: Soft time limit for the task in seconds.

    Returns:
        dict: A dictionary containing the task arguments.
    """
    return {
        "max_retries": max_retries,
        "time_limit": time_limit,
        "soft_time_limit": soft_time_limit,
    }


def check_is_id(value):
    try:
        return int(value) > 0
    except Exception:
        return False


def column_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


def convert_ms_to_time(ms):
    seconds = ms // 1000
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{hours}시간 {minutes}분 {seconds}초"
