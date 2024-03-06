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
    Problem.objects.all().update(is_bonus=False)

    difficulty_groups = [['VeryLow', 'Low'], ['Mid'], ['High', 'VeryHigh']]

    selected_problems = []
    selected_fields = set()

    with transaction.atomic():
        for difficulty in difficulty_groups:
            problems = Problem.objects.filter(difficulty__in=difficulty).exclude(field__in=selected_fields)
            if problems:
                selected_problem = random.choice(problems)
            if selected_problem:
                selected_problems.append(selected_problem)
                selected_fields.add(selected_problem.field)

        for problem in selected_problems:
            print(problem.title, "is set to bonus problem", sep='')
            problem.is_bonus = True
            problem.save(update_fields=['is_bonus'])
