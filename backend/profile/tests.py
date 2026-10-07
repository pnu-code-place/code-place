import copy
import datetime
from unittest import mock

from django.utils import timezone

from problem.tests import DEFAULT_PROBLEM_DATA, ProblemCreateTestBase
from submission.models import JudgeStatus, Submission
from contest.models import Contest
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

    def create_problem(self, problem_id):
        problem_data = copy.deepcopy(DEFAULT_PROBLEM_DATA)
        problem_data["_id"] = problem_id
        return ProblemCreateTestBase.add_problem(problem_data, self.user)

    def create_submission(self, user, result, created_at, contest=None, problem=None):
        submission = Submission.objects.create(
            user_id=user.id,
            username=user.username,
            problem=problem or self.problem,
            code="print(1)",
            language="Python3",
            result=result,
            contest=contest,
        )
        Submission.objects.filter(id=submission.id).update(create_time=created_at)
        return submission

    def create_contest(self):
        contest = Contest.objects.create(
            title="Test Contest",
            description="Test Contest Description",
            real_time_rank=True,
            rule_type="ACM",
            start_time=self.now - datetime.timedelta(days=1),
            end_time=self.now + datetime.timedelta(days=1),
            created_by=self.user,
        )
        return contest

    def test_counts_only_accepted_submissions_for_requested_user(self):
        today = self.now.date()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_at_noon = timezone.make_aware(
            datetime.datetime.combine(yesterday, datetime.time(hour=12)),
            self.current_timezone,
        )

        problem_a = self.create_problem("ACTIVITY-2")
        problem_b = self.create_problem("ACTIVITY-3")
        problem_c = self.create_problem("ACTIVITY-4")

        self.create_submission(self.user, JudgeStatus.ACCEPTED, yesterday_at_noon, problem=problem_a)
        self.create_submission(self.user, JudgeStatus.ACCEPTED, yesterday_at_noon + datetime.timedelta(minutes=5), problem=problem_b)
        self.create_submission(self.user, JudgeStatus.WRONG_ANSWER, yesterday_at_noon + datetime.timedelta(minutes=10), problem=problem_c)
        self.create_submission(self.other_user, JudgeStatus.ACCEPTED, yesterday_at_noon, problem=problem_a)

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

        boundary_problems = [self.create_problem(f"ACTIVITY-{index}") for index in range(2, 6)]

        # 05:59 belongs to the previous activity day; 06:00 starts the new one.
        self.create_submission(
            self.user,
            JudgeStatus.ACCEPTED,
            timezone.make_aware(datetime.datetime.combine(yesterday, datetime.time(hour=5, minute=59)),
                                self.current_timezone),
            problem=boundary_problems[0],
        )
        self.create_submission(
            self.user,
            JudgeStatus.ACCEPTED,
            timezone.make_aware(datetime.datetime.combine(yesterday, datetime.time(hour=6)), self.current_timezone),
            problem=boundary_problems[1],
        )
        self.create_submission(
            self.user,
            JudgeStatus.ACCEPTED,
            timezone.make_aware(datetime.datetime.combine(today, datetime.time(hour=6)), self.current_timezone),
            problem=boundary_problems[2],
        )
        self.create_submission(
            self.user,
            JudgeStatus.ACCEPTED,
            timezone.make_aware(datetime.datetime.combine(three_days_ago, datetime.time(hour=7)),
                                self.current_timezone),
            problem=boundary_problems[3],
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

    def test_excludes_contest_submissions_from_activity_count(self):
        contest = self.create_contest()
        today = self.now.date()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_at_noon = timezone.make_aware(
            datetime.datetime.combine(yesterday, datetime.time(hour=12)),
            self.current_timezone,
        )

        self.create_submission(self.user, JudgeStatus.ACCEPTED, yesterday_at_noon, contest=contest)
        self.create_submission(self.user, JudgeStatus.ACCEPTED, yesterday_at_noon + datetime.timedelta(minutes=5))

        with mock.patch("profile.views.oj.timezone.now", return_value=self.now):
            response = self.client.get(self.url, {"username": self.user.username, "days": 7})

        self.assertSuccess(response)
        data = response.data["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["days"], [{"date": yesterday.isoformat(), "count": 1}])

    def test_contest_only_submission_does_not_count_toward_activity(self):
        contest = self.create_contest()
        yesterday = self.now.date() - datetime.timedelta(days=1)
        yesterday_at_noon = timezone.make_aware(
            datetime.datetime.combine(yesterday, datetime.time(hour=12)),
            self.current_timezone,
        )
        self.create_submission(self.user, JudgeStatus.ACCEPTED, yesterday_at_noon, contest=contest)

        with mock.patch("profile.views.oj.timezone.now", return_value=self.now):
            response = self.client.get(self.url, {"username": self.user.username, "days": 7})

        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 0)
        self.assertEqual(response.data["data"]["days"], [])

    def test_counts_repeated_accepted_problem_only_on_first_solved_day(self):
        today = self.now.date()
        two_days_ago = today - datetime.timedelta(days=2)
        two_days_ago_at_noon = timezone.make_aware(
            datetime.datetime.combine(two_days_ago, datetime.time(hour=12)),
            self.current_timezone,
        )
        self.create_submission(self.user, JudgeStatus.ACCEPTED, two_days_ago_at_noon)
        self.create_submission(self.user, JudgeStatus.ACCEPTED, two_days_ago_at_noon + datetime.timedelta(minutes=5))
        self.create_submission(self.user, JudgeStatus.ACCEPTED, two_days_ago_at_noon + datetime.timedelta(days=1))

        with mock.patch("profile.views.oj.timezone.now", return_value=self.now):
            response = self.client.get(self.url, {"username": self.user.username, "days": 7})

        self.assertSuccess(response)
        data = response.data["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["days"], [{"date": two_days_ago.isoformat(), "count": 1}])

    def test_excludes_problems_already_solved_before_requested_window(self):
        today = self.now.date()
        yesterday_at_noon = timezone.make_aware(
            datetime.datetime.combine(today - datetime.timedelta(days=1), datetime.time(hour=12)),
            self.current_timezone,
        )
        before_window = timezone.make_aware(
            datetime.datetime.combine(today - datetime.timedelta(days=30), datetime.time(hour=12)),
            self.current_timezone,
        )
        self.create_submission(self.user, JudgeStatus.ACCEPTED, before_window)
        self.create_submission(self.user, JudgeStatus.ACCEPTED, yesterday_at_noon)

        with mock.patch("profile.views.oj.timezone.now", return_value=self.now):
            response = self.client.get(self.url, {"username": self.user.username, "days": 7})

        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 0)
        self.assertEqual(response.data["data"]["days"], [])

    def test_contest_solve_before_window_does_not_hide_first_practice_solve(self):
        contest = self.create_contest()
        today = self.now.date()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_at_noon = timezone.make_aware(
            datetime.datetime.combine(yesterday, datetime.time(hour=12)),
            self.current_timezone,
        )
        before_window = timezone.make_aware(
            datetime.datetime.combine(today - datetime.timedelta(days=30), datetime.time(hour=12)),
            self.current_timezone,
        )
        self.create_submission(self.user, JudgeStatus.ACCEPTED, before_window, contest=contest)
        self.create_submission(self.user, JudgeStatus.ACCEPTED, yesterday_at_noon)

        with mock.patch("profile.views.oj.timezone.now", return_value=self.now):
            response = self.client.get(self.url, {"username": self.user.username, "days": 7})

        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 1)
        self.assertEqual(response.data["data"]["days"], [{"date": yesterday.isoformat(), "count": 1}])


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
        self.assertEqual(data[0]["serviceDate"], base_time.date().isoformat())
        self.assertEqual(data[0]["serviceMonth"], "2026-06")
        self.assertEqual(data[0]["status"], JudgeStatus.ACCEPTED)
        self.assertEqual(data[1]["submissionId"], older_submission.id)
        self.assertEqual(data[1]["id"], self.problem._id)
        self.assertEqual(data[1]["status"], JudgeStatus.WRONG_ANSWER)

    def test_returns_service_date_by_six_am_kst_boundary(self):
        before_boundary = datetime.datetime(2026, 6, 26, 20, 59, tzinfo=datetime.timezone.utc)
        after_boundary = datetime.datetime(2026, 6, 26, 21, 0, tzinfo=datetime.timezone.utc)
        self.create_submission(JudgeStatus.ACCEPTED, before_boundary)
        self.create_submission(JudgeStatus.ACCEPTED, after_boundary)

        response = self.client.get(self.url, {"username": self.user.username})

        self.assertSuccess(response)
        data = response.data["data"]
        self.assertEqual(data[0]["serviceDate"], "2026-06-27")
        self.assertEqual(data[0]["serviceMonth"], "2026-06")
        self.assertEqual(data[1]["serviceDate"], "2026-06-26")
        self.assertEqual(data[1]["serviceMonth"], "2026-06")

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

    def test_failed_status_filter_excludes_pending_submissions(self):
        current_timezone = timezone.get_current_timezone()
        base_time = timezone.make_aware(datetime.datetime(2026, 6, 25, 12, 0), current_timezone)
        self.create_submission(JudgeStatus.WRONG_ANSWER, base_time)
        self.create_submission(JudgeStatus.PENDING, base_time + datetime.timedelta(minutes=1))
        self.create_submission(JudgeStatus.JUDGING, base_time + datetime.timedelta(minutes=2))

        response = self.client.get(self.url, {"username": self.user.username, "status": "Failed"})

        self.assertSuccess(response)
        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], JudgeStatus.WRONG_ANSWER)
