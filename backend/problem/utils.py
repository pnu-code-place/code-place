import json
import random
import re
import time

import dramatiq
from functools import lru_cache

from django.db import transaction
from django.db.models import Min, F
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from announcement.models import LinkAnnouncement
from .models import Problem, get_default_week_info
from utils.constants import Difficulty, LINK_NOTICE_LIMIT, LINK_NOTICE_SCRAPING_URL
from selenium import webdriver
import logging

logger = logging.getLogger(__name__)

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


def is_element_exist(item, by, locator):
    try:
        item.find_element(by, locator)
        return True
    except NoSuchElementException:
        return False


def diff_link_announcement(first_id):
    base_objs = LinkAnnouncement.objects.all()[:LINK_NOTICE_LIMIT].first().la_id
    return int(first_id) - base_objs


def update_link_announcement(rows, diff_cnt):
    with transaction.atomic():
        for k, v in enumerate(rows):
            link_announcement = LinkAnnouncement(
                la_id=v['id'],
                title=v['title'],
                url=v['url'],
                create_time=v['create_time'],
                new_flag=v['new_flag']
            )
            if k <= diff_cnt - 1:
                link_announcement.save()
            else:
                link_announcement.save(update_fields=['new_flag'])

def scrap_and_update():
    scrap_link_announcement.send()
@dramatiq.actor()
def scrap_link_announcement():
    # 브라우저를 열지 않고 실행
    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    # 공지사항 접속
    browser = webdriver.Chrome(options=options)
    browser.get(LINK_NOTICE_SCRAPING_URL)
    time.sleep(7)

    # tbody(테이블 바디)가 있는지 확인
    if not is_element_exist(browser, By.CSS_SELECTOR, "tbody"):
        browser.close()
        return

    # 첫번째 tr이 headline인지 아닌지에 따른 분기처리
    first_element = browser.find_element(By.CSS_SELECTOR, "tbody > tr:nth-child(1)")
    if "headline" in first_element.get_attribute("class"):
        first_id = browser.find_element(By.CSS_SELECTOR, "tbody > tr:nth-child(2)").find_element(By.CLASS_NAME,
                                                                                                 "_artclTdNum").text
    else:
        first_id = first_element.find_element(By.CLASS_NAME, "_artclTdNum").text

    diff_cnt = LINK_NOTICE_LIMIT if LinkAnnouncement.objects.count() == 0 else diff_link_announcement(first_id)
    if diff_cnt == 0:
        logger.info("There is no additional notice")

    time.sleep(1)
    rows = browser.find_elements(By.CSS_SELECTOR, "tbody > tr")

    # 첫번째 tr이 headline인지 아닌지에 따른 분기처리
    if "headline" in rows[0].get_attribute("class"):
        rows = rows[1:LINK_NOTICE_LIMIT + 1]
    else:
        rows = rows[:LINK_NOTICE_LIMIT]

    target_list = []

    cnt = 0
    for row in rows:
        # 번호
        id = row.find_element(By.CLASS_NAME, "_artclTdNum").text
        # 작성일
        create_time = row.find_element(By.CLASS_NAME, "_artclTdRdate").text
        # 새 글
        new_flag = is_element_exist(row, By.CLASS_NAME, "newArtcl")
        logger.info("{} {} {}".format(id, create_time, new_flag))
        title = curr_url = None

        if cnt < diff_cnt:
            # 내부 컨텐츠 진입
            a_title_element = row.find_element(By.CLASS_NAME, "artclLinkView")
            a_title_element.click()
            time.sleep(3)

            # 전체 제목
            title = browser.find_element(By.CLASS_NAME, "artclViewTitle").text
            # 링크
            curr_url = browser.current_url

            browser.back()
            browser.implicitly_wait(1)

        cnt += 1
        target_list.append({
            "id": int(id),
            "title": title,
            "url": curr_url,
            "create_time": create_time,
            "new_flag": new_flag
        })

    logger.info(target_list)

    if len(target_list) > 0:
        update_link_announcement(target_list, diff_cnt)

    logger.info("Scrap and update done")

    browser.close()
