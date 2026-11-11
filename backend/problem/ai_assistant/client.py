"""vLLM 호출 공통 모듈"""
import json
import os
import time

import requests

from utils.observability_metrics import AI_HINT_DURATION_SECONDS, AI_HINT_REQUESTS_TOTAL

LOCAL_VLLM_CHAT_COMPLETIONS_URL = "http://127.0.0.1:8010/v1/chat/completions"
CLUSTER_VLLM_CHAT_COMPLETIONS_URL = "http://vllm.code-place-prod:8000/v1/chat/completions"
VLLM_MODEL = "nvidia/Qwen3.6-35B-A3B-NVFP4"
VLLM_CONNECT_TIMEOUT_SEC = 10
VLLM_STREAM_READ_TIMEOUT_SEC = 3600


class LLMHintError(Exception):
    pass


def get_vllm_chat_completions_url():
    # 클러스터 내부 주소
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return CLUSTER_VLLM_CHAT_COMPLETIONS_URL
    # 로컬 개발 시 환경 변수 주소
    return os.getenv("VLLM_CHAT_COMPLETIONS_URL", LOCAL_VLLM_CHAT_COMPLETIONS_URL)


def get_vllm_model():
    return os.getenv("VLLM_MODEL", VLLM_MODEL)


def _extract_stream_delta(response_json):
    choices = response_json.get("choices") or []
    if not choices:
        return ""

    delta = choices[0].get("delta") or {}
    content = delta.get("content")
    if content is None:
        return ""

    if isinstance(content, list):
        return "".join(item.get("text", "") if isinstance(item, dict) else str(item) for item in content)
    return str(content)


def stream_vllm(payload):
    response = None
    started_at = time.monotonic()
    status = "success"
    try:
        response = requests.post(
            get_vllm_chat_completions_url(),
            json=payload,
            timeout=(VLLM_CONNECT_TIMEOUT_SEC, VLLM_STREAM_READ_TIMEOUT_SEC),
            stream=True,
        )
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if not line.startswith("data: "):
                continue

            payload = line[6:]
            if payload == "[DONE]":
                return

            try:
                chunk = json.loads(payload)
            except ValueError as exc:
                status = "stream_parse_error"
                raise LLMHintError("Failed to parse vLLM stream") from exc

            text = _extract_stream_delta(chunk)
            if text:
                yield text
    except requests.RequestException as exc:
        status = "request_error"
        raise LLMHintError("Failed to call vLLM") from exc
    except GeneratorExit:
        status = "client_closed"
        raise
    except Exception:
        if status == "success":
            status = "error"
        raise
    finally:
        AI_HINT_REQUESTS_TOTAL.labels(status=status).inc()
        AI_HINT_DURATION_SECONDS.labels(status=status).observe(max(time.monotonic() - started_at, 0))
        if response is not None:
            response.close()
