from utils.api.tests import APITestCase


class GetCollegeListAPITest(APITestCase):
    """
    단과대학 리스트를 불러오는 API 테스트
    """

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test1")
        self.create_school_fixtures(college_id=2, college_name="Test", department_id=2, department_name="Test2")
        self.create_school_fixtures(college_id=3, college_name="Test", department_id=3, department_name="Test3")
        self.create_school_fixtures(college_id=4, college_name="Test", department_id=4, department_name="Test4")
        self.url = self.reverse("college_list")

    def test_get_college_list(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)


class GetDepartmentListAPITest(APITestCase):
    """
    단과대학에 속한 전공 리스트를 불러오는 API 테스트
    """

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test1")
        self.create_school_fixtures(college_id=2, college_name="Test", department_id=2, department_name="Test2")
        self.create_school_fixtures(college_id=3, college_name="Test", department_id=3, department_name="Test3")
        self.create_school_fixtures(college_id=4, college_name="Test", department_id=4, department_name="Test4")
        self.url = self.reverse("college_list")

    def test_get_college_list(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)
