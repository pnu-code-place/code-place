import json
import random
import re
import dramatiq
from functools import lru_cache

from django.db import transaction
from django.db.models import Min, F

from .models import Problem, get_default_week_info

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
    problems = Problem.objects.all()

    for problem in problems:
        problem.is_bonus = False
        problem.save(update_fields=['is_bonus'])

    low_problems = problems.filter(difficulty__in=['VeryLow', 'Low'])
    mid_problems = problems.filter(difficulty='Mid')
    high_problems = problems.filter(difficulty__in=['High', 'VeryHigh'])

    selected_problems = []

    if low_problems.exists():
        selected_problems.append(random.choice(low_problems))
    if mid_problems.exists():
        selected_problems.append(random.choice(mid_problems))
    if high_problems.exists():
        selected_problems.append(random.choice(high_problems))

    for problem in selected_problems:
        problem.is_bonus = True
        problem.save(update_fields=['is_bonus'])
