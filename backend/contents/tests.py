import copy
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

from contest.models import Contest
from contest.tests import DEFAULT_CONTEST_DATA
from utils.api.tests import APITestCase


class GetHomeStatisticsAPITest(APITestCase):
    """
    홈 화면 컨텐츠(총 문제 수, 풀린 문제 수, 개최된 대회 수) API 테스트
    """

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.admin = self.create_admin()
        self.url = self.reverse("home_statistics")

    def _create_contest(self, title, start_delta, end_delta, visible=True):
        now = timezone.now()
        data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        data.update({
            "title": title,
            "start_time": now + start_delta,
            "end_time": now + end_delta,
            "visible": visible,
        })
        return Contest.objects.create(created_by=self.admin, **data)

    def test_get_home_statistics_success(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_ended_contest_length_counts_started_contests_only(self):
        # 종료된 대회 (시작·종료 모두 과거) → 포함
        self._create_contest("ended", timedelta(days=-2), timedelta(days=-1))
        # 진행중인 대회 (시작했고 아직 안 끝남) → 개최된 것으로 포함
        self._create_contest("ongoing", timedelta(hours=-1), timedelta(hours=1))
        # 예정 대회 (아직 시작 전) → 제외
        self._create_contest("not_started", timedelta(days=1), timedelta(days=2))
        # 시작했지만 비공개 (visible=False) → 제외
        self._create_contest("hidden", timedelta(days=-2), timedelta(days=-1), visible=False)

        # 뷰가 결과를 10분 캐싱하므로, 캐시를 비워 새로 계산되도록 함
        cache.clear()

        resp = self.client.get(self.url)
        self.assertSuccess(resp)
        # 종료(ended) + 진행중(ongoing) = 2, 예정/비공개는 제외
        self.assertEqual(resp.data["data"]["ended_contest_length"], 2)


class GetHomeAnnouncementsAPITest(APITestCase):

    def setUp(self):
        self.url = self.reverse("home_announcements")

    def test_get_home_announcements(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)
        self.assertTrue(len(resp.data) <= 2)


class GetHomeRSSNoticeAPITest(APITestCase):
    """
    RSS 공지사항을 JSON으로 파싱하여 반환하는 API 테스트
    """

    def setUp(self):
        self.url = self.reverse("home_rss_notice")

    def test_get_home_rss_notice(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)
        self.assertTrue(len(resp.data) <= 5)
