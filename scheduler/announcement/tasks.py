import os

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from django.db import transaction
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import logging

from announcement.models import LinkAnnouncement
from utils.constants import LINK_NOTICE_LIMIT, LINK_NOTICE_SCRAPING_URL
from utils.shortcuts import get_env

logger = logging.getLogger(__name__)


def get_browser_by_env():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    production_env = get_env("OJ_ENV", "dev") == "production"
    if production_env:
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium-browser")
        service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
        return webdriver.Chrome(service=service, options=options)
    return webdriver.Chrome(options=options)

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
    print("update_link_announcement", diff_cnt)
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

def scrap_link_announcement():
    """
    일정 주기(2시간) 마다 소프트웨어융합교육원 공지사항을 최대 LINK_NOTICE_LIMIT개 만큼 크롤링 후 데이터베이스 업데이트

    크롤링 정보
    - 공지사항 번호, 제목, 날짜, 새 글 태그

    기존 링크 공지사항 테이블에 존재하는 pk(링크 공지사항 번호)와 대비하여 새로운 공지사항 번호가 사이트에 생겼다면, 차이나는 개수(diff_cnt)만큼 테이블에 신규 데이터를 삽입합니다.
    이후 새글 태그 업데이트를 위해서 크롤링한 전체 데이터의 길이 - diff_cnt 만큼 새글 태그 플래그(new_flag)를 업데이트합니다.
    """

    # 공지사항 접속
    browser = get_browser_by_env()
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

    time.sleep(3)

    # 첫번째 tr이 headline인지 아닌지에 따른 분기처리
    if "headline" in rows[0].get_attribute("class"):
        rows = rows[1:LINK_NOTICE_LIMIT + 1]
    else:
        rows = rows[:LINK_NOTICE_LIMIT]

    target_list = []

    logger.debug("for loop starts!")

    time.sleep(3)

    cnt = 0
    for row in rows:
        # 번호
        # id = row.find_element(By.CLASS_NAME, "_artclTdNum").text
        id = WebDriverWait(row, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "_artclTdNum"))).text
        # 작성일
        # create_time = row.find_element(By.CLASS_NAME, "_artclTdRdate").text
        create_time = WebDriverWait(row, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "_artclTdRdate"))).text
        # 새 글
        new_flag = is_element_exist(row, By.CLASS_NAME, "newArtcl")
        logger.info("{} {} {}".format(id, create_time, new_flag))
        print("{} {} {}".format(id, create_time, new_flag))
        title = curr_url = None

        if cnt < diff_cnt:
            # 내부 컨텐츠 진입
            a_title_element = WebDriverWait(row, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "artclLinkView")))
            a_title_element.click()
            time.sleep(3)

            # 전체 제목
            title = browser.find_element(By.CLASS_NAME, "artclViewTitle").text
            # 링크
            curr_url = browser.current_url

            browser.back()
            time.sleep(1)

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
    print("Scrap and update done")

    browser.close()
