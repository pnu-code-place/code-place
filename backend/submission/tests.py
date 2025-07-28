import copy
from datetime import timedelta
from unittest import mock

from django.utils import timezone

from utils.api.tests import APITestCase
from contest.models import Contest
from contest.tests import DEFAULT_CONTEST_DATA
from problem.tests import DEFAULT_PROBLEM_DATA, ProblemCreateTestBase
from utils.captcha import Captcha
from utils.throttling import TokenBucket

from .models import Submission, JudgeStatus

DEFAULT_SUBMISSION_DATA = {"problem_id": 1, "language": "C++", "code": "#include <iostream>\nint main() { return 0; }"}


class SubmissionCreateTestBase(APITestCase):

    @staticmethod
    def create_submission(user, problem, **kwargs):
        data = {
            "user_id": user.id,
            "username": user.username,
            "language": kwargs.get("language", "C++"),
            "code": kwargs.get("code", "test code"),
            "problem_id": problem.id,
            "ip": kwargs.get("ip", "127.0.0.1"),
            "contest_id": kwargs.get("contest_id", None),
            "result": kwargs.get("result", JudgeStatus.PENDING),
            "statistic_info": kwargs.get("statistic_info", {
                "time_cost": "100",
                "memory_cost": "1024"
            }),
            "shared": kwargs.get("shared", False),
            "first_failed_tc_idx": kwargs.get("first_failed_tc_idx", None)
        }
        return Submission.objects.create(**data)


class SubmissionAPITest(SubmissionCreateTestBase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.url = self.reverse("submission_api")
        self.admin = self.create_super_admin()
        self.user = self.create_user(email="test@test.com", username="test", password="test1234!")
        self.problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, self.admin)

    def test_create_submission_success(self):
        data = copy.deepcopy(DEFAULT_SUBMISSION_DATA)
        data["problem_id"] = self.problem.id

        with mock.patch('judge.tasks.judge_task.apply_async'):
            resp = self.client.post(self.url, data=data)
            self.assertSuccess(resp)
            self.assertIn("submission_id", resp.data["data"])

    def test_create_submission_nonexistent_problem(self):
        data = copy.deepcopy(DEFAULT_SUBMISSION_DATA)
        data["problem_id"] = 99999

        resp = self.client.post(self.url, data=data)
        self.assertFailed(resp, "Problem not exist")

    def test_create_submission_invalid_language(self):
        data = copy.deepcopy(DEFAULT_SUBMISSION_DATA)
        data["problem_id"] = self.problem.id
        data["language"] = "Python"

        resp = self.client.post(self.url, data=data)
        self.assertFailed(resp, "language: Python is not a valid language")

    def test_create_submission_invalid_captcha(self):
        data = copy.deepcopy(DEFAULT_SUBMISSION_DATA)
        data["problem_id"] = self.problem.id
        data["captcha"] = "invalid"

        with mock.patch.object(Captcha, 'check', return_value=False):
            resp = self.client.post(self.url, data=data)
            self.assertFailed(resp, "Invalid captcha")

    def test_create_submission_throttling(self):
        data = copy.deepcopy(DEFAULT_SUBMISSION_DATA)
        data["problem_id"] = self.problem.id

        with mock.patch.object(TokenBucket, 'consume', return_value=(False, 30)):
            resp = self.client.post(self.url, data=data)
            self.assertFailed(resp, "Please wait 30 seconds")

    def test_get_submission_success(self):
        submission = self.create_submission(self.user, self.problem)

        resp = self.client.get(f"{self.url}?id={submission.id}")
        self.assertSuccess(resp)
        self.assertEqual(resp.data["data"]["id"], submission.id)

    def test_get_submission_nonexistent(self):
        resp = self.client.get(f"{self.url}?id=99999")
        self.assertFailed(resp, "Submission doesn't exist")

    def test_get_submission_no_permission(self):
        other_user = self.create_user(email="other@test.com", username="other", password="test1234!", login=False)
        submission = self.create_submission(other_user, self.problem)

        resp = self.client.get(f"{self.url}?id={submission.id}")
        self.assertFailed(resp, "No permission for this submission")

    def test_get_submission_with_testcase_info(self):
        submission = self.create_submission(self.user, self.problem, first_failed_tc_idx=1)

        with mock.patch('utils.testcase_cache.TestCaseCacheManager.get_testcase', return_value={"input": "1 2"}):
            resp = self.client.get(f"{self.url}?id={submission.id}")
            self.assertSuccess(resp)
            self.assertIn("first_failed_tc_io", resp.data["data"])

    def test_share_submission_success(self):
        submission = self.create_submission(self.user, self.problem)

        data = {"id": submission.id, "shared": True}
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)

    def test_share_submission_no_permission(self):
        other_user = self.create_user(email="other@test.com", username="other", password="test1234!", login=False)
        submission = self.create_submission(other_user, self.problem)

        data = {"id": submission.id, "shared": True}
        resp = self.client.put(self.url, data=data)
        self.assertFailed(resp, "No permission to share the submission")


class ContestSubmissionAPITest(SubmissionCreateTestBase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.user = self.create_user(email="test@test.com", username="test", password="test1234!")
        self.create_super_admin()

        contest_data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        contest_data["start_time"] = timezone.now() - timedelta(hours=1)
        contest_data["end_time"] = timezone.now() + timedelta(hours=1)
        contest_resp = self.client.post(self.reverse("contest_admin_api"), data=contest_data)
        self.assertSuccess(contest_resp)
        self.contest = contest_resp.data["data"]

        self.contest_problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, self.user)
        self.contest_problem.contest_id = self.contest["id"]
        self.contest_problem.save()

        self.url = self.reverse("submission_api")

    def test_create_contest_submission_ended(self):
        contest = Contest.objects.get(id=self.contest["id"])
        contest.end_time = timezone.now() - timedelta(hours=1)
        contest.save()

        data = copy.deepcopy(DEFAULT_SUBMISSION_DATA)
        data["problem_id"] = self.contest_problem.id
        data["contest_id"] = self.contest["id"]

        resp = self.client.post(self.reverse("submission_api"), data=data)
        self.assertFailed(resp, "The contest have ended")

    def test_get_contest_submission_list(self):
        submission = self.create_submission(self.user, self.contest_problem, contest_id=self.contest["id"])

        resp = self.client.get(f"{self.reverse('submission_list_api')}?limit=10")
        self.assertSuccess(resp)


class SubmissionListAPITest(SubmissionCreateTestBase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.admin = self.create_admin(login=False)
        self.user = self.create_user(email="test@test.com", username="test", password="test1234!")
        self.problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, self.admin)
        self.url = self.reverse("submission_list_api")

    def test_get_submission_list_success(self):
        submission = self.create_submission(self.user, self.problem)

        resp = self.client.get(f"{self.url}?limit=10")
        self.assertSuccess(resp)

    def test_get_submission_list_no_limit(self):
        resp = self.client.get(self.url)
        self.assertFailed(resp, "Limit is needed")

    def test_get_submission_list_contest_id_error(self):
        resp = self.client.get(f"{self.url}?limit=10&contest_id=1")
        self.assertFailed(resp, "Parameter error")


class SubmissionExistsAPITest(SubmissionCreateTestBase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.admin = self.create_admin(login=False)
        self.user = self.create_user(email="test@test.com", username="test", password="test1234!")
        self.problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, self.admin)
        self.url = self.reverse("submission_exists")

    def test_submission_exists_true(self):
        submission = self.create_submission(self.user, self.problem)

        resp = self.client.get(f"{self.url}?problem_id={self.problem.id}")
        self.assertSuccess(resp)
        self.assertTrue(resp.data["data"])

    def test_submission_exists_no_problem_id(self):
        resp = self.client.get(self.url)
        self.assertFailed(resp, "Parameter error, problem_id is required")


class SubmissionRankAPITest(SubmissionCreateTestBase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")

        # 관리자 생성 및 테스트 컨테스트 생성
        self.admin = self.create_admin()
        contest_data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        contest_data["start_time"] = timezone.now() - timedelta(hours=1)
        contest_data["end_time"] = timezone.now() + timedelta(hours=1)
        contest_resp = self.client.post(self.reverse("contest_admin_api"), data=contest_data)
        self.assertSuccess(contest_resp)
        self.contest = contest_resp.data["data"]

        self.contest_problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, self.admin)
        self.contest_problem.contest_id = self.contest["id"]
        self.contest_problem.save()

        self.user = self.create_user(email="test@test.com", username="test", password="test1234!")
        self.problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, self.admin)
        self.url = self.reverse("submission_rank_api")

    def test_get_submission_rank_success(self):
        submission = self.create_submission(self.user,
                                            self.problem,
                                            result=JudgeStatus.ACCEPTED,
                                            statistic_info={
                                                "time_cost": 100,
                                                "memory_cost": 1024
                                            })

        resp = self.client.get(f"{self.url}?submission_id={submission.id}")
        self.assertSuccess(resp)
        self.assertIn("solved_rank", resp.data["data"])

    def test_statistic_info_invalid(self):
        submission = self.create_submission(self.user,
                                            self.problem,
                                            result=JudgeStatus.ACCEPTED,
                                            statistic_info={
                                                "time_cost": "invalid",
                                                "memory_cost": "invalid"
                                            })

        resp = self.client.get(f"{self.url}?submission_id={submission.id}")
        self.assertFailed(resp, "Invalid submission statistic_info")

        # statistic_info가 비어있는 경우
        submission.statistic_info = {}
        submission.save()

        resp = self.client.get(f"{self.url}?submission_id={submission.id}")
        self.assertFailed(resp, "Invalid submission statistic_info")

    def test_reject_contest_problem(self):
        submission = self.create_submission(self.user,
                                            self.contest_problem,
                                            contest_id=self.contest["id"],
                                            result=JudgeStatus.ACCEPTED,
                                            statistic_info={
                                                "time_cost": 100,
                                                "memory_cost": 1024
                                            })

        resp = self.client.get(f"{self.url}?submission_id={submission.id}")
        self.assertFailed(resp, "This API is not available for contest submissions")

    def test_reject_unauthorized_user(self):
        submission = self.create_submission(user=self.user,
                                            problem=self.problem,
                                            result=JudgeStatus.ACCEPTED,
                                            statistic_info={
                                                "time_cost": 100,
                                                "memory_cost": 1024
                                            })

        # 다른 유저로 요청
        other_user = self.create_user(
            email="other",
            username="other",
            password="test1234!",
        )

        resp = self.client.get(f"{self.url}?submission_id={submission.id}", user=other_user)
        self.assertFailed(resp, "No permission for this submission")

    def test_get_submission_rank_multiple_users(self):
        # 여러 유저 생성
        user1 = self.create_user(email="user1@test.com", username="user1", password="test1234!")
        user2 = self.create_user(email="user2@test.com", username="user2", password="test1234!")
        user3 = self.create_user(email="user3@test.com", username="user3", password="test1234!")

        problem = self.problem

        # user1: Accepted, time_cost 100, memory_cost 1024, 제출 시각 가장 빠름
        sub1 = self.create_submission(user1,
                                      problem,
                                      result=JudgeStatus.ACCEPTED,
                                      statistic_info={
                                          "time_cost": 100,
                                          "memory_cost": 1024
                                      })
        # 인위적으로 생성 시간 조절 (예: sub1가 가장 먼저 제출)
        Submission.objects.filter(id=sub1.id).update(create_time=timezone.now() - timedelta(minutes=10))

        # user2: Accepted, time_cost 200, memory_cost 2048
        sub2 = self.create_submission(user2,
                                      problem,
                                      result=JudgeStatus.ACCEPTED,
                                      statistic_info={
                                          "time_cost": 200,
                                          "memory_cost": 2048
                                      })
        Submission.objects.filter(id=sub2.id).update(create_time=timezone.now() - timedelta(minutes=5))

        # user3: Accepted, time_cost 150, memory_cost 1024
        sub3 = self.create_submission(user3,
                                      problem,
                                      result=JudgeStatus.ACCEPTED,
                                      statistic_info={
                                          "time_cost": 150,
                                          "memory_cost": 1024
                                      })
        Submission.objects.filter(id=sub3.id).update(create_time=timezone.now() - timedelta(minutes=1))

        # user3의 제출물로 랭크 조회
        resp = self.client.get(f"{self.url}?submission_id={sub3.id}")
        self.assertSuccess(resp)

        data = resp.data["data"]

        # solved_rank: sub1가 10분 전에 제출한 Accepted, sub2는 5분 전, sub3는 1분 전 -> solved_rank = 2 (2명 앞섬)
        self.assertEqual(data["solved_rank"], 3)

        # time_cost ranking:
        # sub1(100), sub3(150), sub2(200) 순
        # sub3의 time_cost는 150, 'time_cost < 150'인것은 sub1(100) 1개 -> rank = 2
        # total_count = 3
        self.assertEqual(data["time_cost_percent"], round(1 / 3 * 100, 2))

        # memory_cost ranking:
        # sub1(1024), sub3(1024), sub2(2048)
        # 'memory_cost < 1024'는 없음 -> rank = 1
        self.assertEqual(data["memory_cost_percent"], round(0 / 3 * 100, 2))

    def test_get_submission_rank_no_submission_id(self):
        resp = self.client.get(self.url)
        self.assertFailed(resp, "Parameter submission_id is required")

    def test_get_submission_rank_nonexistent(self):
        resp = self.client.get(f"{self.url}?submission_id=99999")
        self.assertFailed(resp, "Submission does not exist")

    def test_get_submission_rank_total_zero(self):
        # Accepted된 submission이 없는 상태: 새로 제출 생성 (Accepted 외 상태로)
        submission = self.create_submission(self.user,
                                            self.problem,
                                            result=JudgeStatus.PENDING,
                                            statistic_info={
                                                "time_cost": 100,
                                                "memory_cost": 1024
                                            })

        resp = self.client.get(f"{self.url}?submission_id={submission.id}")
        self.assertSuccess(resp)
        self.assertEqual(resp.data["data"]["time_cost_percent"], 0.0)
        self.assertEqual(resp.data["data"]["memory_cost_percent"], 0.0)
