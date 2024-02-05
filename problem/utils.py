import json
import re
import dramatiq
from utils.shortcuts import DRAMATIQ_WORKER_ARGS
from functools import lru_cache

from django.core.cache import cache

from .models import Problem

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
    problems = Problem.objects.all().order_by("weekly_success_rate")
    most_difficult_problem = problems[0] if problems else None

    if most_difficult_problem:
        problem_info = {
            'id': most_difficult_problem.id,
            'success_rate': float(most_difficult_problem.weekly_success_rate),
            'solvers_number': most_difficult_problem.weekly_solvers.count(),
            'difficulty': most_difficult_problem.difficulty,
            'field': most_difficult_problem.field,
            'tags': list(most_difficult_problem.tags.values_list('name', flat=True))
        }
        cache.set('most_difficult_problem', json.dumps(problem_info))

    for problem in problems:
        problem.weekly_success_rate = 0
        problem.weekly_accepted_number = 0
        problem.weekly_submission_number = 0
        problem.weekly_solvers.clear()
        problem.save(update_fields=['weekly_success_rate', 'weekly_accepted_number',
                                    'weekly_submission_number'])
