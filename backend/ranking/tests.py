from utils.api.tests import APITestCase


class HomeRankingAPITest(APITestCase):
    """
    홈 화면에 최대 3위까지 랭킹을 보여주는 API 테스트
    """

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.create_user(email="test1@test.com", username="test1", password="test1234!", login=False)
        self.create_user(email="test2@test.com", username="test2", password="test1234!", login=False)
        self.create_user(email="test3@test.com", username="test3", password="test1234!", login=False)
        self.url = self.reverse("home_ranking_api")

    def test_get_home_ranking_with_sufficient_data(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)


class UserRankAPITest(APITestCase):
    """
    랭킹 탭 - 사용자 랭킹 API 테스트
    """

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.create_user(email="test1@test.com", username="test1", password="test1234!", login=False)
        self.create_user(email="test2@test.com", username="test2", password="test1234!", login=False)
        self.create_user(email="test3@test.com", username="test3", password="test1234!", login=False)
        self.url = self.reverse("user_rank_api")

    def test_get_user_rank_with_sufficient_data(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)


class SurgeUserRankAPITest(APITestCase):
    """
    랭킹 탭 - 오늘의 급상승 사용자 API 테스트
    """

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.create_user(email="test1@test.com", username="test1", password="test1234!", login=False)
        self.create_user(email="test2@test.com", username="test2", password="test1234!", login=False)
        self.create_user(email="test3@test.com", username="test3", password="test1234!", login=False)
        self.url = self.reverse("surge_user_rank_api")

    def test_get_surge_user_rank_with_sufficient_data(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)


class MajorRankAPITest(APITestCase):
    """
    랭킹 탭 - 학과별 랭킹 API 테스트
    """

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.create_user(email="test1@test.com", username="test1", password="test1234!", login=False)
        self.create_user(email="test2@test.com", username="test2", password="test1234!", login=False)
        self.create_user(email="test3@test.com", username="test3", password="test1234!", login=False)
        self.url = self.reverse("major_rank_api")

    def test_get_major_rank_with_sufficient_data(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)
