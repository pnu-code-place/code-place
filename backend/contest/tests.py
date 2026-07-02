import copy
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from utils.api.tests import APITestCase

from .models import ContestAnnouncement, ContestRuleType, Contest

DEFAULT_CONTEST_DATA = {
    "title": "test title",
    "description": "test description",
    "start_time": timezone.localtime(timezone.now()),
    "end_time": timezone.localtime(timezone.now()) + timedelta(days=1),
    "rule_type": ContestRuleType.ACM,
    "password": "123",
    "allowed_ip_ranges": [],
    "visible": True,
    "real_time_rank": True,
    "allow_paste": True
}


class ContestAdminAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.create_super_admin()
        self.url = self.reverse("contest_admin_api")
        self.data = copy.deepcopy(DEFAULT_CONTEST_DATA)

    def test_create_contest(self):
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)
        return response

    def test_create_contest_with_invalid_cidr(self):
        self.data["allowed_ip_ranges"] = ["127.0.0"]
        resp = self.client.post(self.url, data=self.data)
        self.assertTrue(resp.data["data"].endswith("is not a valid cidr network"))

    def test_update_contest(self):
        id = self.test_create_contest().data["data"]["id"]
        update_data = {
            "id": id,
            "title": "update title",
            "description": "update description",
            "password": "12345",
            "visible": False,
            "real_time_rank": False
        }
        data = copy.deepcopy(self.data)
        data.update(update_data)
        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        response_data = response.data["data"]
        for k in data.keys():
            if isinstance(data[k], datetime):
                continue
            self.assertEqual(response_data[k], data[k])

    def test_get_contests(self):
        self.test_create_contest()
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def test_get_one_contest(self):
        id = self.test_create_contest().data["data"]["id"]
        response = self.client.get("{}?id={}".format(self.url, id))
        self.assertSuccess(response)

    def test_create_contest_without_ai_field_defaults_to_false(self):
        """ai_assistant_enabled 필드 없이 대회를 생성하면 기본값이 False여야 한다."""
        # DEFAULT_CONTEST_DATA에 ai_assistant_enabled 없음 → 레거시 클라이언트 재현
        resp = self.client.post(self.url, data=DEFAULT_CONTEST_DATA)
        self.assertSuccess(resp)

        contest_id = resp.data["data"]["id"]
        contest = Contest.objects.get(id=contest_id)
        self.assertFalse(contest.ai_assistant_enabled)

    def test_create_contest_with_ai_enabled_explicit(self):
        """ai_assistant_enabled=True를 명시적으로 전달하면 True로 저장된다."""
        data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        data["ai_assistant_enabled"] = True
        resp = self.client.post(self.url, data=data)
        self.assertSuccess(resp)

        contest_id = resp.data["data"]["id"]
        contest = Contest.objects.get(id=contest_id)
        self.assertTrue(contest.ai_assistant_enabled)


class ContestAIAssistantMigrationTest(APITestCase):
    """데이터 마이그레이션: 기존 대회 ai_assistant_enabled 일괄 False 전환 검증."""

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.admin = self.create_admin()

    def _bulk_disable(self):
        """0004 마이그레이션의 disable_ai_assistant 함수와 동일한 로직."""
        Contest.objects.filter(ai_assistant_enabled=True).update(ai_assistant_enabled=False)

    def test_all_enabled_contests_become_disabled(self):
        """ai_assistant_enabled=True인 대회가 모두 False로 전환된다."""
        c1 = Contest.objects.create(created_by=self.admin, **DEFAULT_CONTEST_DATA)
        c2 = Contest.objects.create(created_by=self.admin, **{**DEFAULT_CONTEST_DATA, "title": "second"})
        Contest.objects.filter(pk__in=[c1.pk, c2.pk]).update(ai_assistant_enabled=True)

        self._bulk_disable()

        c1.refresh_from_db()
        c2.refresh_from_db()
        self.assertFalse(c1.ai_assistant_enabled)
        self.assertFalse(c2.ai_assistant_enabled)

    def test_already_disabled_contests_remain_disabled(self):
        """이미 ai_assistant_enabled=False인 대회는 마이그레이션 후에도 False를 유지한다."""
        contest = Contest.objects.create(created_by=self.admin, **DEFAULT_CONTEST_DATA)
        self.assertFalse(contest.ai_assistant_enabled)

        self._bulk_disable()

        contest.refresh_from_db()
        self.assertFalse(contest.ai_assistant_enabled)

    def test_migration_does_not_affect_other_fields(self):
        """마이그레이션이 ai_assistant_enabled 외의 필드를 변경하지 않는다."""
        contest = Contest.objects.create(created_by=self.admin, **DEFAULT_CONTEST_DATA)
        Contest.objects.filter(pk=contest.pk).update(ai_assistant_enabled=True)

        self._bulk_disable()

        contest.refresh_from_db()
        self.assertFalse(contest.ai_assistant_enabled)
        self.assertEqual(contest.title, DEFAULT_CONTEST_DATA["title"])
        self.assertTrue(contest.visible)
        self.assertTrue(contest.real_time_rank)


class ContestAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        user = self.create_admin()
        self.contest = Contest.objects.create(created_by=user, **DEFAULT_CONTEST_DATA)
        self.url = self.reverse("contest_api") + "?id=" + str(self.contest.id)

    def test_get_contest_list(self):
        url = self.reverse("contest_list_api")
        response = self.client.get(url + "?limit=10")
        self.assertSuccess(response)
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_get_one_contest(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_regular_user_validate_contest_password(self):
        self.create_user(email="test@test.com", username="test", password="test1234!")
        url = self.reverse("contest_password_api")
        resp = self.client.post(url, {"contest_id": self.contest.id, "password": "error_password"})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Wrong password or password expired"})

        resp = self.client.post(url, {"contest_id": self.contest.id, "password": DEFAULT_CONTEST_DATA["password"]})
        self.assertSuccess(resp)

    def test_regular_user_access_contest(self):
        self.create_user(email="test@test.com", username="test", password="test1234!")
        url = self.reverse("contest_access_api")
        resp = self.client.get(url + "?contest_id=" + str(self.contest.id))
        self.assertFalse(resp.data["data"]["access"])

        password_url = self.reverse("contest_password_api")
        resp = self.client.post(password_url, {
            "contest_id": self.contest.id,
            "password": DEFAULT_CONTEST_DATA["password"]
        })
        self.assertSuccess(resp)
        resp = self.client.get(self.url)
        self.assertSuccess(resp)


class ContestAnnouncementAdminAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.create_super_admin()
        self.url = self.reverse("contest_announcement_admin_api")
        contest_id = self.create_contest().data["data"]["id"]
        self.data = {"title": "test title", "content": "test content", "contest_id": contest_id, "visible": True}

    def create_contest(self):
        url = self.reverse("contest_admin_api")
        data = DEFAULT_CONTEST_DATA
        return self.client.post(url, data=data)

    def test_create_contest_announcement(self):
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)
        return response

    def test_delete_contest_announcement(self):
        id = self.test_create_contest_announcement().data["data"]["id"]
        response = self.client.delete("{}?id={}".format(self.url, id))
        self.assertSuccess(response)
        self.assertFalse(ContestAnnouncement.objects.filter(id=id).exists())

    def test_get_contest_announcements(self):
        self.test_create_contest_announcement()
        response = self.client.get(self.url + "?contest_id=" + str(self.data["contest_id"]))
        self.assertSuccess(response)

    def test_get_one_contest_announcement(self):
        id = self.test_create_contest_announcement().data["data"]["id"]
        response = self.client.get("{}?id={}".format(self.url, id))
        self.assertSuccess(response)


class ContestAnnouncementListAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.create_super_admin()
        self.url = self.reverse("contest_announcement_api")

    def create_contest_announcements(self):
        contest_id = self.client.post(self.reverse("contest_admin_api"), data=DEFAULT_CONTEST_DATA).data["data"]["id"]
        url = self.reverse("contest_announcement_admin_api")
        self.client.post(url, data={"title": "test title1", "content": "test content1", "contest_id": contest_id})
        self.client.post(url, data={"title": "test title2", "content": "test content2", "contest_id": contest_id})
        return contest_id

    def test_get_contest_announcement_list(self):
        contest_id = self.create_contest_announcements()
        response = self.client.get(self.url, data={"contest_id": contest_id})
        self.assertSuccess(response)


class ContestRankAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        user = self.create_admin()
        self.acm_contest = Contest.objects.create(created_by=user, **DEFAULT_CONTEST_DATA)
        self.create_user(email="test@test.com", username="test", password="test1234!")
        self.url = self.reverse("contest_rank_api")

    def get_contest_rank(self):
        resp = self.client.get(self.url + "?contest_id=" + self.acm_contest.id)
        self.assertSuccess(resp)


class ContestParticipantsAPITest(APITestCase):

    def setUp(self):
        from problem.tests import DEFAULT_PROBLEM_DATA, ProblemCreateTestBase

        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.admin = self.create_admin()
        self.user = self.create_user(email="test@test.com", username="test", password="test1234!", login=False)
        self.contest = Contest.objects.create(created_by=self.admin, **DEFAULT_CONTEST_DATA)
        self.problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, self.admin)
        self.problem.contest_id = self.contest.id
        self.problem.save()
        self.url = self.reverse("contest_participants_api")

    def test_participants_are_grouped_by_user_id(self):
        from submission.models import JudgeStatus, Submission

        Submission.objects.create(
            user_id=self.user.id,
            username="oldname",
            language="C++",
            code="test code",
            problem_id=self.problem.id,
            ip="127.0.0.1",
            contest_id=self.contest.id,
            result=JudgeStatus.PENDING,
            statistic_info={"time_cost": "100", "memory_cost": "1024"},
            shared=False,
            first_failed_tc_idx=None,
        )
        Submission.objects.create(
            user_id=self.user.id,
            username="newname",
            language="C++",
            code="test code",
            problem_id=self.problem.id,
            ip="127.0.0.1",
            contest_id=self.contest.id,
            result=JudgeStatus.PENDING,
            statistic_info={"time_cost": "100", "memory_cost": "1024"},
            shared=False,
            first_failed_tc_idx=None,
        )

        resp = self.client.get(f"{self.url}?contest_id={self.contest.id}")
        self.assertSuccess(resp)

        participants = resp.data["data"]
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0]["user_id"], self.user.id)
        self.assertEqual(participants[0]["username"], self.user.username)
        self.assertEqual(participants[0]["submission_count"], 2)

    def test_participants_requires_contest_id(self):
        resp = self.client.get(self.url)
        self.assertFailed(resp, "Invalid parameter, contest_id is required")

    def test_participants_rejects_invalid_contest_id(self):
        resp = self.client.get(f"{self.url}?contest_id=abc")
        self.assertFailed(resp, "Invalid parameter, contest_id is required")

    def test_participants_fallback_to_submission_username_when_user_is_missing(self):
        from submission.models import JudgeStatus, Submission

        older_submission = Submission.objects.create(
            user_id=self.user.id,
            username="zzz_user",
            language="C++",
            code="test code",
            problem_id=self.problem.id,
            ip="9.9.9.9",
            contest_id=self.contest.id,
            result=JudgeStatus.PENDING,
            statistic_info={"time_cost": "100", "memory_cost": "1024"},
            shared=False,
            first_failed_tc_idx=None,
        )
        latest_submission = Submission.objects.create(
            user_id=self.user.id,
            username="aaa_user",
            language="C++",
            code="test code",
            problem_id=self.problem.id,
            ip="1.1.1.1",
            contest_id=self.contest.id,
            result=JudgeStatus.PENDING,
            statistic_info={"time_cost": "100", "memory_cost": "1024"},
            shared=False,
            first_failed_tc_idx=None,
        )
        Submission.objects.filter(id=older_submission.id).update(create_time=timezone.now() - timedelta(minutes=1))
        Submission.objects.filter(id=latest_submission.id).update(create_time=timezone.now())

        self.user.delete()

        resp = self.client.get(f"{self.url}?contest_id={self.contest.id}")
        self.assertSuccess(resp)

        participants = resp.data["data"]
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0]["username"], "aaa_user")
        self.assertEqual(participants[0]["email"], "")
        self.assertEqual(participants[0]["avatar"], f"{settings.AVATAR_URI_PREFIX}/default.png")
        self.assertEqual(participants[0]["school"], "")
        self.assertEqual(participants[0]["major"], "")
        self.assertEqual(participants[0]["last_submission_ip"], "1.1.1.1")
