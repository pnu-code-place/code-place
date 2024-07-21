from contents.serializers import HomeStatistics, RSSItemSerializer
from contest.models import Contest
from problem.models import Problem
from utils.api import APIView
from django.utils.timezone import now
import requests
import xml.etree.ElementTree as ET

from utils.constants import RSS_FEED_URL


class GetHomeStatisticsAPI(APIView):
    def get(self, request):
        """
        총 문제 수, 채점이 완료된 문제 수, 마감된 대회 수를 반환하는 API
        """
        problems = Problem.objects.all().filter(visible=True)

        # 총 문제 수
        total_problem_length = problems.count()

        # 한번이라도 accept가 된 문제 수
        accepted_problem_length = problems.filter(accepted_number__lt=0).count()

        # 마감된 대회 수
        contests = Contest.objects.select_related("created_by").filter(visible=True)
        cur = now()
        contests = contests.filter(end_time__lt=cur)
        ended_contest_length = contests.count()

        home_statistics = {
            "total_problem_length": total_problem_length,
            "accepted_problem_length": accepted_problem_length,
            "ended_contest_length": ended_contest_length,
        }

        return self.success(HomeStatistics(home_statistics).data)


class GetHomeRSSNoticeAPI(APIView):
    def get(self, request):
        """
        RSS 공지사항을 JSON으로 파싱하여 반환하는 API
        """

        # RSS 피드 가져오기
        response = requests.get(RSS_FEED_URL)

        if response.status_code == 200:
            # XML 파싱
            root = ET.fromstring(response.content)

            # 필요한 정보 추출
            items = []
            for item in root.findall('.//item')[:5]:
                item_dict = {
                    'title': item.find('title').text,
                    'link': item.find('link').text,
                    'pubDate': item.find('pubDate').text
                }
                items.append(item_dict)

            # Serializer를 사용하여 데이터 직렬화
            serializer = RSSItemSerializer(items, many=True)

            # JsonResponse로 반환
            return self.success(serializer.data)
        else:
            self.error("Failed to fetch RSS feed")