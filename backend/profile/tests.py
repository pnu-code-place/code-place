import copy
import datetime
from unittest import mock

from django.utils import timezone

from problem.tests import DEFAULT_PROBLEM_DATA, ProblemCreateTestBase
from submission.models import JudgeStatus, Submission
from utils.api.tests import APITestCase


class UserProfileActivityAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.user = self.create_user(email="test@test.com", username="test", password="test1234!")
        self.other_user = self.create_user(
            email="other@test.com",
            username="other",
            password="test1234!",
            login=False,
        )
        problem_data = copy.deepcopy(DEFAULT_PROBLEM_DATA)
        problem_data["_id"] = "ACTIVITY-1"
        self.problem = ProblemCreateTestBase.add_problem(problem_data, self.user)
        self.url = self.reverse("user_profile_activity_api")
        self.current_timezone = timezone.get_current_timezone()
        self.now = timezone.make_aware(
            datetime.datetime(2026, 6, 26, 12, 0),
            self.current_timezone,
        )

    def create_submission(self, user, result, created_at):
        submission = Submission.objects.create(
            user_id=user.id,
            username=user.username,
            problem=self.problem,
            code="print(1)",
            language="Python3",
            result=result,
        )
        Submission.objects.filter(id=submission.id).update(create_time=created_at)
        return submission

    def test_counts_only_accepted_submissions_for_requested_user(self):
        today = self.now.date()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_at_noon = timezone.make_aware(
            datetime.datetime.combine(yesterday, datetime.time(hour=12)),
            self.current_timezone,
        )

        self.create_submission(self.user, JudgeStatus.ACCEPTED, yesterday_at_noon)
        self.create_submission(self.user, JudgeStatus.ACCEPTED, yesterday_at_noon + datetime.timedelta(minutes=5))
        self.create_submission(self.user, JudgeStatus.WRONG_ANSWER, yesterday_at_noon + datetime.timedelta(minutes=10))
        self.create_submission(self.other_user, JudgeStatus.ACCEPTED, yesterday_at_noon)

        with mock.patch("profile.views.oj.timezone.now", return_value=self.now):
            response = self.client.get(self.url, {"username": self.user.username, "days": 7})

        self.assertSuccess(response)
        data = response.data["data"]
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["max_count"], 2)
        self.assertEqual(data["end_date"], today.isoformat())
        self.assertEqual(data["current_streak"], 0)
        self.assertEqual(data["longest_streak"], 1)
        self.assertEqual(data["day_boundary"], "6:00 UTC+9")
        self.assertEqual(data["days"], [{"date": yesterday.isoformat(), "count": 2}])

    def test_excludes_accepted_submissions_outside_requested_window(self):
        old_date = self.now.date() - datetime.timedelta(days=7)
        old_datetime = timezone.make_aware(
            datetime.datetime.combine(old_date, datetime.time(hour=12)),
            self.current_timezone,
        )
        self.create_submission(self.user, JudgeStatus.ACCEPTED, old_datetime)

        with mock.patch("profile.views.oj.timezone.now", return_value=self.now):
            response = self.client.get(self.url, {"username": self.user.username, "days": 7})

        self.assertSuccess(response)
        data = response.data["data"]
        self.assertEqual(data["total"], 0)
        self.assertEqual(data["max_count"], 0)
        self.assertEqual(data["days"], [])

    def test_rejects_invalid_days(self):
        response = self.client.get(self.url, {"username": self.user.username, "days": 0})

        self.assertFailed(response, "days must be between 1 and 366")

    def test_activity_day_changes_at_six_am_kst_and_streaks_are_server_calculated(self):
        today = self.now.date()
        three_days_ago = today - datetime.timedelta(days=3)
        two_days_ago = today - datetime.timedelta(days=2)
        yesterday = today - datetime.timedelta(days=1)

        # 05:59 belongs to the previous activity day; 06:00 starts the new one.
        self.create_submission(
            self.user,
            JudgeStatus.ACCEPTED,
            timezone.make_aware(datetime.datetime.combine(yesterday, datetime.time(hour=5, minute=59)),
                                self.current_timezone),
        )
        self.create_submission(
            self.user,
            JudgeStatus.ACCEPTED,
            timezone.make_aware(datetime.datetime.combine(yesterday, datetime.time(hour=6)), self.current_timezone),
        )
        self.create_submission(
            self.user,
            JudgeStatus.ACCEPTED,
            timezone.make_aware(datetime.datetime.combine(today, datetime.time(hour=6)), self.current_timezone),
        )
        self.create_submission(
            self.user,
            JudgeStatus.ACCEPTED,
            timezone.make_aware(datetime.datetime.combine(three_days_ago, datetime.time(hour=7)),
                                self.current_timezone),
        )

        with mock.patch("profile.views.oj.timezone.now", return_value=self.now):
            response = self.client.get(self.url, {"username": self.user.username, "days": 7})

        self.assertSuccess(response)
        data = response.data["data"]
        self.assertEqual(data["current_streak"], 4)
        self.assertEqual(data["longest_streak"], 4)
        self.assertEqual(data["days"], [
            {"date": three_days_ago.isoformat(), "count": 1},
            {"date": two_days_ago.isoformat(), "count": 1},
            {"date": yesterday.isoformat(), "count": 1},
            {"date": today.isoformat(), "count": 1},
        ])


class ProfileProblemAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.user = self.create_user(email="problem@test.com", username="problem", password="test1234!")
        problem_data = copy.deepcopy(DEFAULT_PROBLEM_DATA)
        problem_data["_id"] = "PROFILE-PROBLEM-1"
        self.problem = ProblemCreateTestBase.add_problem(problem_data, self.user)
        self.url = self.reverse("profile_problem_api")

    def create_submission(self, result, created_at):
        submission = Submission.objects.create(
            user_id=self.user.id,
            username=self.user.username,
            problem=self.problem,
            code="print(1)",
            language="Python3",
            result=result,
        )
        Submission.objects.filter(id=submission.id).update(create_time=created_at)
        return submission

    def test_returns_all_problem_submissions_in_latest_order(self):
        current_timezone = timezone.get_current_timezone()
        base_time = timezone.make_aware(datetime.datetime(2026, 6, 25, 12, 0), current_timezone)
        older_submission = self.create_submission(JudgeStatus.WRONG_ANSWER, base_time)
        latest_submission = self.create_submission(JudgeStatus.ACCEPTED, base_time + datetime.timedelta(minutes=5))

        response = self.client.get(self.url, {"username": self.user.username})

        self.assertSuccess(response)
        data = response.data["data"]
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["submissionId"], latest_submission.id)
        self.assertEqual(data[0]["id"], self.problem._id)
        self.assertEqual(data[0]["status"], JudgeStatus.ACCEPTED)
        self.assertEqual(data[1]["submissionId"], older_submission.id)
        self.assertEqual(data[1]["id"], self.problem._id)
        self.assertEqual(data[1]["status"], JudgeStatus.WRONG_ANSWER)

    def test_filters_problem_field_by_numeric_or_string_value(self):
        current_timezone = timezone.get_current_timezone()
        created_at = timezone.make_aware(datetime.datetime(2026, 6, 25, 12, 0), current_timezone)
        self.create_submission(JudgeStatus.ACCEPTED, created_at)

        numeric_response = self.client.get(self.url, {"username": self.user.username, "field": "0"})
        string_response = self.client.get(self.url, {"username": self.user.username, "field": "implementation"})

        self.assertSuccess(numeric_response)
        self.assertSuccess(string_response)
        self.assertEqual(numeric_response.data["data"], string_response.data["data"])
        self.assertEqual(len(string_response.data["data"]), 1)

    def test_invalid_problem_field_filter_returns_api_error(self):
        response = self.client.get(self.url, {"username": self.user.username, "field": "unknown"})

        self.assertFailed(response, "Invalid field")

    def test_missing_username_returns_api_error(self):
        response = self.client.get(self.url)

        self.assertFailed(response, "username is required")

    def test_unknown_username_returns_api_error(self):
        response = self.client.get(self.url, {"username": "missing"})

        self.assertFailed(response, "User does not exist")

    def test_invalid_problem_status_filter_returns_api_error(self):
        response = self.client.get(self.url, {"username": self.user.username, "status": "unknown"})

        self.assertFailed(response, "Invalid status")
