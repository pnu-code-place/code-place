import logging
from django.db import transaction
from django.db.models import F
from oj import celery

from .models import Problem, get_default_week_info
from utils.constants import Difficulty

logger = logging.getLogger(__name__)

DIFFICULTY_GROUPS = [
    [Difficulty.VERYLOW, Difficulty.LOW],
    [Difficulty.MID],
    [Difficulty.HIGH, Difficulty.VERYHIGH],
]


@celery.app.task(name='update_weekly_stats')
def update_weekly_stats():
    """Update the weekly statistics of problems.
    
    This method updates the last week's statistics to the current week,
    resets the current week's statistics, and identifies the most difficult problem
    based on the success rate from the last week.
    It marks the most difficult problem as such and resets the flag for all others.
    """
    with transaction.atomic():
        Problem.objects.update(
            last_week_info=F('curr_week_info'),
            curr_week_info=get_default_week_info(),
            is_most_difficult=False,
        )

        most_difficult_problem = Problem.objects.annotate(
            min_success_rate=F('last_week_info__success_rate')).order_by('min_success_rate').first()

        if most_difficult_problem:
            most_difficult_problem.is_most_difficult = True
            most_difficult_problem.save(update_fields=['is_most_difficult'])


@celery.app.task(name='update_bonus_problem')
def update_bonus_problem():
    """Update bonus problems by selecting one problem from each difficulty group.

    This method selects one problem from each difficulty group, ensuring that no two problems
    belong to the same field. If no problems are found in a difficulty group, it allows field overlap.
    It updates the selected problems to be marked as bonus problems and resets the bonus status
    for all other problems.
    """
    selected_problem_ids = list()
    selected_fields = set()

    with transaction.atomic():
        for difficulty in DIFFICULTY_GROUPS:
            candidate_problems = Problem.objects.filter(
                difficulty__in=difficulty,
                visible=True,
                contest__isnull=True,
            ).exclude(is_bonus=True).exclude(field__in=selected_fields)

            # If no problems found in the current difficulty group, Allow field overlap
            if not candidate_problems:
                candidate_problems = Problem.objects.filter(
                    difficulty__in=difficulty,
                    visible=True,
                    contest__isnull=True,
                ).exclude(is_bonus=True)

            # Randomly select one problem from the candidate problems
            selected_problem = candidate_problems.order_by('?').first()

            if selected_problem:
                selected_problem_ids.append(selected_problem.id)
                selected_fields.add(selected_problem.field)

        Problem.objects.filter(is_bonus=True).update(is_bonus=False)
        Problem.objects.filter(id__in=selected_problem_ids).update(is_bonus=True)
