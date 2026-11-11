"""AI 조교 API가 학생에게 보내는 안내 문구"""
from utils.constants import HINT_LIMIT_PER_PROBLEM

from .chat_hint import MAX_QUESTION_LENGTH


class AIHintMessage:
    LOGIN_REQUIRED = "로그인이 필요합니다."
    PROBLEM_ID_REQUIRED = "문제 번호가 필요합니다."
    PROBLEM_NOT_FOUND = "문제를 찾을 수 없습니다."
    CONTEST_NOT_FOUND = "대회를 찾을 수 없습니다."
    CONTEST_PASSWORD_INVALID = "비밀번호가 올바르지 않거나 만료되었습니다."
    CONTEST_NOT_STARTED = "아직 시작하지 않은 대회입니다."
    CONTEST_AI_DISABLED = "이 대회에서는 AI 조교를 사용할 수 없습니다."
    QUESTION_REQUIRED = "질문을 입력해 주세요."
    QUESTION_TOO_LONG = f"질문은 최대 {MAX_QUESTION_LENGTH}자까지 보낼 수 있습니다."
    BUSY = "아직 답변 중이에요! 끝나면 다시 물어봐 주세요 🙂"
    THROTTLED = "{wait}초 뒤에 다시 물어봐 주세요 🙂"
    LIMIT_EXCEEDED = (
        f"이 문제에 대한 AI 조교 사용 횟수({HINT_LIMIT_PER_PROBLEM}회)를 모두 소진했습니다. "
        "이전 답변을 복습해 보세요."
    )
    STAGE_HINT_FAILED = "힌트를 생성하지 못했습니다."
    CHAT_ANSWER_FAILED = "답변을 생성하지 못했습니다."
