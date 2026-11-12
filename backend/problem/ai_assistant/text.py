"""문제 데이터 글자 정리 공통 함수"""
import re
from html import unescape

from django.utils.html import strip_tags


# 줄 끝 태그는 줄바꿈으로 변환
_LINE_BREAK_TAG = re.compile(r"<br\s*/?>|</(p|div|li|tr|h[1-6]|pre|blockquote)\s*>", re.IGNORECASE)
_LIST_ITEM_TAG = re.compile(r"<li[^>]*>", re.IGNORECASE)


def normalize_html_to_text(value):
    if not value:
        return ""

    html = _LINE_BREAK_TAG.sub("\n", value)
    html = _LIST_ITEM_TAG.sub("- ", html)
    text = unescape(strip_tags(html))
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def format_samples(samples):
    if not samples:
        return "없음"

    rendered_samples = []
    for index, sample in enumerate(samples, start=1):
        input_text = (sample.get("input") or "").strip() or "(비어 있음)"
        output_text = (sample.get("output") or "").strip() or "(비어 있음)"
        rendered_samples.append(f"[샘플 입력 {index}]\n{input_text}\n[샘플 출력 {index}]\n{output_text}")
    return "\n\n".join(rendered_samples)
