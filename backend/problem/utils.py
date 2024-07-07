import json
import random
import re

import dramatiq
from functools import lru_cache

from django.db import transaction
from django.db.models import Min, F

from .models import Problem, get_default_week_info
from utils.constants import Difficulty

TEMPLATE_BASE = """//PREPEND BEGIN
{}
//PREPEND END

//TEMPLATE BEGIN
{}
//TEMPLATE END

//APPEND BEGIN
{}
//APPEND END"""


@lru_cache(maxsize=100)
def parse_problem_template(template_str):
    prepend = re.findall(r"//PREPEND BEGIN\n([\s\S]+?)//PREPEND END", template_str)
    template = re.findall(r"//TEMPLATE BEGIN\n([\s\S]+?)//TEMPLATE END", template_str)
    append = re.findall(r"//APPEND BEGIN\n([\s\S]+?)//APPEND END", template_str)
    return {"prepend": prepend[0] if prepend else "",
            "template": template[0] if template else "",
            "append": append[0] if append else ""}


@lru_cache(maxsize=100)
def build_problem_template(prepend, template, append):
    return TEMPLATE_BASE.format(prepend, template, append)


def call_update_weekly_stats():
    update_weekly_stats.send()


@dramatiq.actor()
def update_weekly_stats():
    problems = Problem.objects.filter(difficulty__in=['High', 'VeryHigh'], accepted_number__gte=1)

    if not problems:
        return

    with transaction.atomic():
        for problem in problems:
            problem.last_week_info = problem.curr_week_info
            problem.curr_week_info = get_default_week_info()
            problem.is_most_difficult = False
            problem.save(update_fields=['last_week_info', 'curr_week_info', 'is_most_difficult'])

    most_difficult_problem = problems.annotate(
        min_success_rate=F('last_week_info__success_rate')
    ).order_by('min_success_rate').first()

    if most_difficult_problem:
        most_difficult_problem.is_most_difficult = True
        most_difficult_problem.save(update_fields=['is_most_difficult'])


def call_update_bonus_problem():
    update_bonus_problem.send()


@dramatiq.actor()
def update_bonus_problem():
    """보너스문제를 업데이트합니다.

    Scheduler에 의해 매주 한번씩 실행되며 난이도 그룹별로 한 문제씩, 총 3문제를 보너스문제로 설정합니다.
    영역 중복을 최대한 겹치지 않도록 하되 총 3문제를 보너스문제로 설정할 수 없다면 영역 중복을 허용합니다.
    저번 주에 보너스 문제였던 문제는 이번 주 보너스 문제에서 제외됩니다.
    """
    difficulty_groups = [
        [Difficulty.VERYLOW, Difficulty.LOW],
        [Difficulty.MID],
        [Difficulty.HIGH, Difficulty.VERYHIGH]
    ]

    selected_problems = []
    selected_fields = set()

    with transaction.atomic():
        for difficulty in difficulty_groups:
            problems = Problem.objects \
                .filter(difficulty__in=difficulty, visible=True, contest__isnull=True) \
                .exclude(is_bonus=True, field__in=selected_fields)
            if not problems:
                # 영역 중복을 허용하여 다시 한 번 후보 문제 추출
                problems = Problem.objects \
                    .filter(difficulty__in=difficulty, visible=True, contest__isnull=True) \
                    .exclude(is_bonus=True)

            if problems:
                # 후보 문제 중 하나를 선택하여 selected_problems에 추가
                selected_problem = random.choice(problems)
                selected_problems.append(selected_problem)
                selected_fields.add(selected_problem.field)

        # 지난 주 보너스 문제 초기화
        try:
            Problem.objects.all().update(is_bonus=False)
        except Problem.DoesNotExist as e:
            raise e

        # 이번 주 보너스 문제 설정
        for problem in selected_problems:
            print(f"{problem.title} is set to bonus problem")
            problem.is_bonus = True
            problem.save(update_fields=['is_bonus'])

