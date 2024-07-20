from utils.api.tests import APITestCase

class GetHomeStatisticsAPITest(APITestCase):
    """
    홈 화면 컨텐츠(총 문제 수, 풀린 문제 수, 진행된 대회 수) API 테스트
    """
    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        """
        임시 테스트 코드
        """
        self.url = self.reverse("home_statistics")

    def test_get_home_ranking_with_sufficient_data(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)