from announcement.models import Announcement
from contents.serializers import HomeStatistics, RSSItemSerializer, HomeAnnouncementsSerializer
from contest.models import Contest
from problem.models import Problem
from utils.api import APIView
from django.core.cache import cache
from django.utils.timezone import now
import requests
import xml.etree.ElementTree as ET

from utils.constants import RSS_FEED_URL

HOME_STATS_CACHE_KEY = "home_statistics_v2"
HOME_STATS_CACHE_TTL = 60 * 10  # 10분

RSS_CACHE_KEY = "home_rss_feed"
RSS_CACHE_TTL = 60 * 30  # 30분


class GetHomeStatisticsAPI(APIView):

    def get(self, request):
        cached = cache.get(HOME_STATS_CACHE_KEY)
        if cached:
            return self.success(cached)

        problems = Problem.objects.filter(visible=True)
        total_problem_length = problems.count()
        accepted_problem_length = problems.filter(accepted_number__gt=0).count()

        # 개최된 대회 수: 이미 시작된 대회(진행중 + 종료)를 집계, 아직 시작 전인 예정 대회는 제외
        ended_contest_length = Contest.objects.filter(visible=True, start_time__lte=now()).count()

        home_statistics = {
            "total_problem_length": total_problem_length,
            "accepted_problem_length": accepted_problem_length,
            "ended_contest_length": ended_contest_length,
        }

        data = HomeStatistics(home_statistics).data
        cache.set(HOME_STATS_CACHE_KEY, data, HOME_STATS_CACHE_TTL)
        return self.success(data)


class GetHomeAnnouncementAPI(APIView):
    """
    홈에서 보여지는 CSEP 공지사항의 id, title, create_time 정보를 반환하는 API
    """

    def get(self, request):
        home_announcements = Announcement.objects.filter(visible=True)[:2]
        return self.success(HomeAnnouncementsSerializer(home_announcements, many=True).data)


class GetHomeRSSNoticeAPI(APIView):

    def get(self, request):
        """
        RSS 공지사항을 JSON으로 파싱하여 반환하는 API
        """
        cached = cache.get(RSS_CACHE_KEY)
        if cached:
            return self.success(cached)

        try:
            response = requests.get(RSS_FEED_URL, timeout=5)
        except requests.RequestException:
            return self.error("Failed to fetch RSS feed")

        if response.status_code != 200:
            return self.error("Failed to fetch RSS feed")

        root = ET.fromstring(response.content)
        BASE_URL = "https://swedu.pusan.ac.kr"
        items = []
        for item in root.findall('.//item')[:5]:
            link = item.find('link').text or ''
            if link and not link.startswith('http'):
                link = BASE_URL + link
            item_dict = {
                'title': item.find('title').text.rstrip("}"),
                'link': link,
                'pubDate': item.find('pubDate').text
            }
            items.append(item_dict)

        data = RSSItemSerializer(items, many=True).data
        cache.set(RSS_CACHE_KEY, data, RSS_CACHE_TTL)
        return self.success(data)
