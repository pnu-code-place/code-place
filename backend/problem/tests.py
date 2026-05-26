import copy
import hashlib
import json
import os
import shutil
from datetime import timedelta
from zipfile import ZipFile

import requests
from django.conf import settings
from django.db import DatabaseError
from django.utils import timezone

from utils.constants import Difficulty
from utils.api.tests import APITestCase
from unittest import mock

from .models import ProblemTag, ProblemIOMode, get_default_week_info
from .models import Problem, ProblemRuleType, ProblemAIHintLog
from .tasks import update_weekly_stats, update_bonus_problem
from contest.models import Contest, ContestRuleType
from contest.tests import DEFAULT_CONTEST_DATA
from utils.constants import CONTEST_PASSWORD_SESSION_KEY
from .llm_hint import (CLUSTER_VLLM_CHAT_COMPLETIONS_URL, LOCAL_VLLM_CHAT_COMPLETIONS_URL,
                       VLLM_CONNECT_TIMEOUT_SEC, VLLM_MODEL, VLLM_STREAM_READ_TIMEOUT_SEC,
                       get_vllm_chat_completions_url)

from .views.admin import TestCaseAPI
from .utils import parse_problem_template

DEFAULT_PROBLEM_DATA = {
    "_id": "A-110",
    "title": "test",
    "description": "<p>test</p>",
    "input_description": "test",
    "output_description": "test",
    "time_limit": 1000,
    "memory_limit": 256,
    "field": 0,
    "difficulty": "Low",
    "visible": True,
    "tags": ["test"],
    "languages": ["C", "C++", "Java"],
    "template": {},
    "samples": [{
        "input": "test",
        "output": "test"
    }],
    "spj": False,
    "spj_language": "C",
    "spj_code": "",
    "spj_compile_ok": True,
    "test_case_id": "499b26290cc7994e0b497212e842ea85",
    "test_case_score": [{
        "output_name": "1.out",
        "input_name": "1.in",
        "output_size": 0,
        "stripped_output_md5": "d41d8cd98f00b204e9800998ecf8427e",
        "input_size": 0,
        "score": 0
    }],
    "io_mode": {
        "io_mode": ProblemIOMode.standard,
        "input": "input.txt",
        "output": "output.txt"
    },
    "share_submission": False,
    "rule_type": "ACM",
    "hint": "<p>test</p>",
    "source": "test"
}


class ProblemCreateTestBase(APITestCase):

    @staticmethod
    def add_problem(problem_data, created_by):
        data = copy.deepcopy(problem_data)
        if data["spj"]:
            if not data["spj_language"] or not data["spj_code"]:
                raise ValueError("Invalid spj")
            data["spj_version"] = hashlib.md5(
                (data["spj_language"] + ":" + data["spj_code"]).encode("utf-8")).hexdigest()
        else:
            data["spj_language"] = None
            data["spj_code"] = None
        if data["rule_type"] == ProblemRuleType.OI:
            total_score = 0
            for item in data["test_case_score"]:
                if item["score"] <= 0:
                    raise ValueError("invalid score")
                else:
                    total_score += item["score"]
            data["total_score"] = total_score
        data["created_by"] = created_by
        tags = data.pop("tags")

        data["languages"] = list(data["languages"])

        problem = Problem.objects.create(**data)

        for item in tags:
            try:
                tag = ProblemTag.objects.get(name=item)
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=item)
            problem.tags.add(tag)
        return problem

    @staticmethod
    def create_problem_with_custom_field(created_by, **kwargs):
        data = copy.deepcopy(DEFAULT_PROBLEM_DATA)
        data.update(kwargs)
        return ProblemCreateTestBase.add_problem(data, created_by)


class ProblemTagListAPITest(APITestCase):

    def test_get_tag_list(self):
        ProblemTag.objects.create(name="name1")
        ProblemTag.objects.create(name="name2")
        resp = self.client.get(self.reverse("problem_tag_list_api"))
        self.assertSuccess(resp)


class TestCaseUploadAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.api = TestCaseAPI()
        self.url = self.reverse("test_case_api")
        self.create_super_admin()

    def test_filter_file_name(self):
        self.assertEqual(
            self.api.filter_name_list(["1.in", "1.out", "2.in", ".DS_Store"], spj=False), ["1.in", "1.out"])
        self.assertEqual(self.api.filter_name_list(["2.in", "2.out"], spj=False), [])

        self.assertEqual(self.api.filter_name_list(["1.in", "1.out", "2.in"], spj=True), ["1.in", "2.in"])
        self.assertEqual(self.api.filter_name_list(["2.in", "3.in"], spj=True), [])

    def make_test_case_zip(self):
        base_dir = os.path.join("/tmp", "test_case")
        shutil.rmtree(base_dir, ignore_errors=True)
        os.mkdir(base_dir)
        file_names = ["1.in", "1.out", "2.in", ".DS_Store"]
        for item in file_names:
            with open(os.path.join(base_dir, item), "w", encoding="utf-8") as f:
                f.write(item + "\n" + item + "\r\n" + "end")
        zip_file = os.path.join(base_dir, "test_case.zip")
        with ZipFile(os.path.join(base_dir, "test_case.zip"), "w") as f:
            for item in file_names:
                f.write(os.path.join(base_dir, item), item)
        return zip_file

    def test_upload_spj_test_case_zip(self):
        with open(self.make_test_case_zip(), "rb") as f:
            resp = self.client.post(self.url, data={"spj": "true", "file": f}, format="multipart")
            self.assertSuccess(resp)
            data = resp.data["data"]
            self.assertEqual(data["spj"], True)
            test_case_dir = os.path.join(settings.TEST_CASE_DIR, data["id"])
            self.assertTrue(os.path.exists(test_case_dir))
            for item in data["info"]:
                name = item["input_name"]
                with open(os.path.join(test_case_dir, name), "r", encoding="utf-8") as f:
                    self.assertEqual(f.read(), name + "\n" + name + "\n" + "end")

    def test_upload_test_case_zip(self):
        with open(self.make_test_case_zip(), "rb") as f:
            resp = self.client.post(self.url, data={"spj": "false", "file": f}, format="multipart")
            self.assertSuccess(resp)
            data = resp.data["data"]
            self.assertEqual(data["spj"], False)
            test_case_dir = os.path.join(settings.TEST_CASE_DIR, data["id"])
            self.assertTrue(os.path.exists(test_case_dir))
            for item in data["info"]:
                name = item["input_name"]
                with open(os.path.join(test_case_dir, name), "r", encoding="utf-8") as f:
                    self.assertEqual(f.read(), name + "\n" + name + "\n" + "end")


class ProblemAdminAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.url = self.reverse("problem_admin_api")
        self.create_super_admin()
        self.data = copy.deepcopy(DEFAULT_PROBLEM_DATA)

    def test_create_problem(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        return resp

    def test_duplicate_display_id(self):
        self.test_create_problem()

        resp = self.client.post(self.url, data=self.data)
        self.assertFailed(resp, "Problem ID already exists")

    def test_spj(self):
        data = copy.deepcopy(self.data)
        data["spj"] = True

        resp = self.client.post(self.url, data)
        self.assertFailed(resp, "Invalid spj")

        data["spj_code"] = "test"
        resp = self.client.post(self.url, data=data)
        self.assertSuccess(resp)

    def test_get_problem(self):
        self.test_create_problem()
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_get_one_problem(self):
        problem_id = self.test_create_problem().data["data"]["id"]
        resp = self.client.get(self.url + "?id=" + str(problem_id))
        self.assertSuccess(resp)

    def test_edit_problem(self):
        problem_id = self.test_create_problem().data["data"]["id"]
        data = copy.deepcopy(self.data)
        data["id"] = problem_id
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)


class ProblemAPITest(ProblemCreateTestBase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.url = self.reverse("problem_api")
        admin = self.create_admin(login=False)
        self.problem = self.add_problem(DEFAULT_PROBLEM_DATA, admin)
        self.create_user(email="test@test.com", username="test", password="test1234!")

    def test_get_problem_list(self):
        resp = self.client.get(f"{self.url}?limit=10")
        self.assertSuccess(resp)

    def test_get_one_problem(self):
        resp = self.client.get(self.url + "?problem_id=" + self.problem._id)
        self.assertSuccess(resp)


class ProblemLLMHintAPITest(ProblemCreateTestBase):

    def setUp(self):
        os.environ["IS_LOCAL_TEST"] = "False"

        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.url = self.reverse("problem_llm_hint_api")
        self.admin = self.create_admin(login=False)
        self.problem = self.add_problem(DEFAULT_PROBLEM_DATA, self.admin)
        self.hidden_problem = self.create_problem_with_custom_field(self.admin, _id="A-211", visible=False)
        # self.create_user(email="test@test.com", username="test", password="test1234!")
        self.user = self.create_user(email="test@test.com", username="test", password="test1234!")
        self.client.force_login(self.user)

    @staticmethod
    def _streaming_body(response):
        return "".join(
            chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk for chunk in response.streaming_content)

    @staticmethod
    def _mock_streaming_response(lines):
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.iter_lines.return_value = lines
        response.close.return_value = None
        return response

    @mock.patch("problem.llm_hint.requests.post")
    def test_stream_llm_hint(self, mocked_post):
        mocked_post.return_value = self._mock_streaming_response([
            'data: {"choices":[{"delta":{"content":"힌트 "}}]}',
            'data: {"choices":[{"delta":{"content":"스트림"}}]}',
            "data: [DONE]",
        ])

        resp = self.client.get(f"{self.url}?problem_id={self.problem._id}")
        body = self._streaming_body(resp)

        self.assertEqual(resp["Content-Type"], "text/event-stream")
        self.assertIn('event: chunk', body)
        self.assertIn(json.dumps({"text": "힌트 "}, ensure_ascii=False), body)
        self.assertIn(json.dumps({"text": "스트림"}, ensure_ascii=False), body)
        self.assertIn('event: done', body)
        self.assertEqual(ProblemAIHintLog.objects.filter(user=self.user, problem=self.problem).count(), 1)
        saved_log = ProblemAIHintLog.objects.filter(user=self.user, problem=self.problem).first()
        self.assertEqual(saved_log.hint_content, "힌트 스트림")

        msgs = mocked_post.call_args.kwargs["json"]["messages"]
        mocked_post.assert_called_once()
        self.assertEqual(mocked_post.call_args.args[0], get_vllm_chat_completions_url())
        self.assertEqual(mocked_post.call_args.kwargs["json"]["model"], VLLM_MODEL)

        # messages[0]: 시스템 프롬프트
        self.assertIn("Do not repeat the same hint.", msgs[0]["content"])
        self.assertIn("Start from a specific condition, constraint, structure, or example from the problem.",
                      msgs[0]["content"])
        self.assertIn("Hint levels:", msgs[0]["content"])
        self.assertIn("현재 N단계 힌트를 제공해야 합니다", msgs[0]["content"])

        # messages[1]: 문제 데이터 (HTML 태그 미포함, problem._id 포함)
        self.assertIn(self.problem._id, msgs[1]["content"])
        self.assertNotIn("<p>", msgs[1]["content"])

        # messages[2]: 트리거 — 첫 요청이므로 1단계를 명시해야 함
        self.assertEqual(msgs[2]["role"], "user")
        self.assertIn("You must provide the Level 1 hint now.", msgs[2]["content"])

        self.assertEqual(mocked_post.call_args.kwargs["json"]["temperature"], 0.3)
        self.assertEqual(mocked_post.call_args.kwargs["stream"], True)
        self.assertEqual(
            mocked_post.call_args.kwargs["timeout"],
            (VLLM_CONNECT_TIMEOUT_SEC, VLLM_STREAM_READ_TIMEOUT_SEC),
        )

    @mock.patch("problem.llm_hint.requests.post")
    def test_stream_llm_hint_problem_limit(self, mocked_post):
        """한 문제당 5회 제한에 걸리는지 테스트"""
        # 해당 문제에 대해 이미 5개의 힌트 로그가 존재하도록 세팅
        for i in range(5):
            ProblemAIHintLog.objects.create(user=self.user, problem=self.problem, hint_content=f"더미 {i}")

        resp = self.client.get(f"{self.url}?problem_id={self.problem._id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("limit-exceeded", body)
        self.assertIn("소진", body)
        mocked_post.assert_not_called()    # 제한에 걸리면 LLM 호출이 아예 안 일어나야 함

    @mock.patch("problem.llm_hint.requests.post")
    def test_stream_llm_hint_admin_bypass(self, mocked_post):
        """관리자는 횟수 제한 없이 무제한으로 사용 가능한지 테스트"""
        mocked_post.return_value = self._mock_streaming_response([
            'data: {"choices":[{"delta":{"content":"어드민 패스"}}]}',
            "data: [DONE]",
        ])

        # Admin 계정으로 5회 꽉 채움
        for i in range(5):
            ProblemAIHintLog.objects.create(user=self.admin, problem=self.problem, hint_content=f"더미 {i}")

        # 일반 유저를 로그아웃시키고 Admin으로 로그인
        self.client.force_login(self.admin)
        resp = self.client.get(f"{self.url}?problem_id={self.problem._id}")
        body = self._streaming_body(resp)

        # 제한에 걸리지 않고 정상 응답이 와야 함
        self.assertNotIn("limit-exceeded", body)
        self.assertIn("어드민 패스", body)
        mocked_post.assert_called_once()

    @mock.patch("problem.llm_hint.requests.post")
    def test_stream_llm_hint_empty_response(self, mocked_post):
        """정상적으로 스트리밍이 종료되었으나 텍스트가 비어있는 경우, 선제 생성된 로그가 삭제되는지 테스트"""
        # 공백만 리턴하는 모델 응답 Mocking
        mocked_post.return_value = self._mock_streaming_response([
            'data: {"choices":[{"delta":{"content":"   "}}]}',
            "data: [DONE]",
        ])

        resp = self.client.get(f"{self.url}?problem_id={self.problem._id}")
        body = self._streaming_body(resp)

        # 1. 정상적으로 done 이벤트가 와야 함
        self.assertIn('event: done', body)

        # 2. 가장 중요: 빈 텍스트였기 때문에 DB에 로그가 남아있으면 안 됨 (횟수 차감 방어 성공)
        self.assertEqual(ProblemAIHintLog.objects.filter(user=self.user, problem=self.problem).count(), 0)

    def test_stream_llm_hint_requires_login(self):
        self.client.logout()

        resp = self.client.get(f"{self.url}?problem_id={self.problem._id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("로그인이 필요합니다.", body)

    def test_stream_llm_hint_with_missing_problem(self):
        resp = self.client.get(f"{self.url}?problem_id=NOT-EXIST")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("문제를 찾을 수 없습니다.", body)

    def test_stream_llm_hint_with_missing_problem_id(self):
        resp = self.client.get(self.url)
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("문제 번호가 필요합니다.", body)

    def test_stream_llm_hint_with_hidden_problem(self):
        resp = self.client.get(f"{self.url}?problem_id={self.hidden_problem._id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("문제를 찾을 수 없습니다.", body)

    def test_stream_llm_hint_with_contest_problem(self):
        contest = Contest.objects.create(created_by=self.admin, **DEFAULT_CONTEST_DATA)
        contest_problem = self.create_problem_with_custom_field(self.admin, _id="A-212")
        contest_problem.contest = contest
        contest_problem.save(update_fields=["contest"])

        resp = self.client.get(f"{self.url}?problem_id={contest_problem._id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("문제를 찾을 수 없습니다.", body)

    # ------------------------------------------------------------------
    # contest_id path tests
    # ------------------------------------------------------------------

    def _make_contest(self, problem_id, **contest_kwargs):
        """Return (contest, problem) — underway, public, ai_enabled by default."""
        defaults = {
            "title": "contest test",
            "description": "desc",
            "start_time": timezone.localtime(timezone.now()) - timedelta(hours=1),
            "end_time": timezone.localtime(timezone.now()) + timedelta(days=1),
            "rule_type": ContestRuleType.ACM,
            "password": "",
            "allowed_ip_ranges": [],
            "visible": True,
            "real_time_rank": True,
            "allow_paste": True,
            "ai_assistant_enabled": True,
        }
        defaults.update(contest_kwargs)
        contest = Contest.objects.create(created_by=self.admin, **defaults)
        problem = self.create_problem_with_custom_field(self.admin, _id=problem_id)
        problem.contest = contest
        problem.save(update_fields=["contest"])
        return contest, problem

    @mock.patch("problem.llm_hint.requests.post")
    def test_contest_stream_llm_hint(self, mocked_post):
        """SSE stream works for an accessible contest problem."""
        mocked_post.return_value = self._mock_streaming_response([
            'data: {"choices":[{"delta":{"content":"힌트"}}]}',
            "data: [DONE]",
        ])
        contest, problem = self._make_contest("C-301")

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertEqual(resp["Content-Type"], "text/event-stream")
        self.assertIn('event: chunk', body)
        self.assertIn('event: done', body)
        self.assertNotIn('event: app-error', body)
        mocked_post.assert_called_once()

    def test_contest_stream_llm_hint_ai_disabled(self):
        """app-error when ai_assistant_enabled=False."""
        contest, problem = self._make_contest("C-302", ai_assistant_enabled=False)

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("AI 조교를 사용할 수 없습니다", body)

    def test_contest_stream_llm_hint_invisible_contest(self):
        """app-error (permission-denied) when contest has visible=False."""
        contest, problem = self._make_contest("C-303", visible=False)

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("permission-denied", body)

    def test_contest_stream_llm_hint_password_no_session(self):
        """app-error when contest is password-protected and no password is in session."""
        contest, problem = self._make_contest("C-304", password="secret")

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("permission-denied", body)

    def test_contest_stream_llm_hint_password_wrong(self):
        """app-error when session contains a wrong password."""
        contest, problem = self._make_contest("C-305", password="secret")

        session = self.client.session
        session[CONTEST_PASSWORD_SESSION_KEY] = {contest.id: "wrong"}
        session.save()

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("permission-denied", body)

    @mock.patch("problem.llm_hint.requests.post")
    def test_contest_stream_llm_hint_password_correct(self, mocked_post):
        """SSE stream works when the correct password is stored in session."""
        mocked_post.return_value = self._mock_streaming_response([
            'data: {"choices":[{"delta":{"content":"힌트"}}]}',
            "data: [DONE]",
        ])
        contest, problem = self._make_contest("C-306", password="secret")

        session = self.client.session
        session[CONTEST_PASSWORD_SESSION_KEY] = {contest.id: "secret"}
        session.save()

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn('event: chunk', body)
        self.assertIn('event: done', body)
        self.assertNotIn('event: app-error', body)

    def test_contest_stream_llm_hint_not_started(self):
        """app-error (permission-denied) when the contest has not started yet."""
        contest, problem = self._make_contest(
            "C-307",
            start_time=timezone.localtime(timezone.now()) + timedelta(hours=1),
        )

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("permission-denied", body)

    @mock.patch("problem.llm_hint.requests.post")
    def test_contest_stream_llm_hint_admin_bypasses_restrictions(self, mocked_post):
        """Contest creator gets SSE stream even for not-started password-protected contests."""
        mocked_post.return_value = self._mock_streaming_response([
            'data: {"choices":[{"delta":{"content":"힌트"}}]}',
            "data: [DONE]",
        ])
        contest, problem = self._make_contest(
            "C-308",
            password="secret",
            start_time=timezone.localtime(timezone.now()) + timedelta(hours=1),
        )

        self.client.login(username="admin@admin.com", password="admin1234!")

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn('event: chunk', body)
        self.assertIn('event: done', body)
        self.assertNotIn('event: app-error', body)

    def test_contest_stream_llm_hint_hidden_problem(self):
        """app-error when the problem itself has visible=False within an accessible contest."""
        contest, problem = self._make_contest("C-309")
        problem.visible = False
        problem.save(update_fields=["visible"])

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn('event: app-error', body)
        self.assertIn("문제를 찾을 수 없습니다.", body)

    @mock.patch("problem.llm_hint.requests.post", side_effect=requests.Timeout)
    def test_stream_llm_hint_handles_timeout(self, mocked_post):
        resp = self.client.get(f"{self.url}?problem_id={self.problem._id}")
        body = self._streaming_body(resp)

        mocked_post.assert_called_once()
        self.assertIn('event: app-error', body)
        self.assertIn("힌트를 생성하지 못했습니다.", body)

    @mock.patch("problem.views.oj.stream_problem_hint", side_effect=TypeError("boom"))
    def test_stream_llm_hint_handles_unexpected_error(self, mocked_stream):
        resp = self.client.get(f"{self.url}?problem_id={self.problem._id}")
        body = self._streaming_body(resp)

        mocked_stream.assert_called_once()
        self.assertIn('event: app-error', body)
        self.assertIn("힌트를 생성하지 못했습니다.", body)
        self.assertIn('event: done', body)

    def test_get_vllm_chat_completions_url_for_local(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_vllm_chat_completions_url(), LOCAL_VLLM_CHAT_COMPLETIONS_URL)

    def test_get_vllm_chat_completions_url_for_kubernetes(self):
        with mock.patch.dict(os.environ, {"KUBERNETES_SERVICE_HOST": "10.0.0.1"}, clear=False):
            self.assertEqual(get_vllm_chat_completions_url(), CLUSTER_VLLM_CHAT_COMPLETIONS_URL)

    # ------------------------------------------------------------------
    # 레거시 대회 (ai_assistant_enabled 필드 도입 이전 생성) 테스트
    # ------------------------------------------------------------------

    def _make_public_contest_no_ai(self, problem_id):
        """비밀번호 없는 공개 대회(ai_assistant_enabled=False)와 문제를 반환한다."""
        contest = Contest.objects.create(
            created_by=self.admin,
            title="legacy contest",
            description="desc",
            start_time=timezone.localtime(timezone.now()) - timedelta(hours=1),
            end_time=timezone.localtime(timezone.now()) + timedelta(days=1),
            rule_type=ContestRuleType.ACM,
            password="",
            allowed_ip_ranges=[],
            visible=True,
            real_time_rank=True,
            allow_paste=True,
            # ai_assistant_enabled 생략 → 모델 기본값(False) 적용
        )
        problem = self.create_problem_with_custom_field(self.admin, _id=problem_id)
        problem.contest = contest
        problem.save(update_fields=["contest"])
        return contest, problem

    def test_legacy_contest_no_ai_field_blocks_hint(self):
        """ai_assistant_enabled 없이 생성된 레거시 대회는 모델 기본값(False)이 적용되어 AI 힌트가 차단된다."""
        contest, problem = self._make_public_contest_no_ai("L-001")

        self.assertFalse(contest.ai_assistant_enabled)

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn("event: app-error", body)
        self.assertIn("AI 조교를 사용할 수 없습니다", body)

    def test_legacy_contest_after_bulk_disable_blocks_hint(self):
        """데이터 마이그레이션으로 ai_assistant_enabled=True → False로 일괄 전환된 대회도 AI 힌트가 차단된다."""
        contest, problem = self._make_public_contest_no_ai("L-002")

        # 마이그레이션 전 상태 재현: 구 기본값(True)으로 강제 설정
        Contest.objects.filter(pk=contest.pk).update(ai_assistant_enabled=True)
        contest.refresh_from_db()
        self.assertTrue(contest.ai_assistant_enabled)

        # 데이터 마이그레이션 로직 실행 (ai_assistant_enabled=True인 대회를 전부 False로)
        Contest.objects.filter(ai_assistant_enabled=True).update(ai_assistant_enabled=False)
        contest.refresh_from_db()
        self.assertFalse(contest.ai_assistant_enabled)

        resp = self.client.get(f"{self.url}?problem_id={problem._id}&contest_id={contest.id}")
        body = self._streaming_body(resp)

        self.assertIn("event: app-error", body)
        self.assertIn("AI 조교를 사용할 수 없습니다", body)


class AIHintHistoryAPITest(ProblemCreateTestBase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.url = self.reverse("problem_ai_hint_history_api")    # urls/oj.py 에 등록했던 name과 일치해야 함
        self.admin = self.create_admin(login=False)
        self.problem = self.add_problem(DEFAULT_PROBLEM_DATA, self.admin)
        self.user = self.create_user(email="history@test.com", username="history_test", password="test1234!")
        self.hidden_problem = self.create_problem_with_custom_field(self.admin, _id="A-211", visible=False)

    def test_get_history_require_login(self):
        """로그인하지 않은 유저가 조회 요청 시 에러"""
        self.client.logout()
        resp = self.client.get(f"{self.url}?problem_id={self.problem._id}")
        # 일반 APIView 응답 구조에 맞춰 검증 (에러 메시지 포함 여부)
        self.assertIsNotNone(resp.data.get("error"))

    def test_get_history_success_and_structure(self):
        """정상적으로 로그와 횟수 데이터가 넘어오는지 구조 검증"""
        self.client.force_login(self.user)

        # 더미 데이터 생성
        ProblemAIHintLog.objects.create(user=self.user, problem=self.problem, hint_content="과거의 힌트 1")
        ProblemAIHintLog.objects.create(user=self.user, problem=self.problem, hint_content="과거의 힌트 2")

        resp = self.client.get(f"{self.url}?problem_id={self.problem._id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.data.get("error"))

        payload = resp.data.get("data")

        # 응답 구조 검증
        self.assertIn("logs", payload)

        # 값 검증
        self.assertEqual(len(payload["logs"]), 2)
        self.assertEqual(payload["logs"][0]["hint_content"], "과거의 힌트 1")

    def test_get_history_with_hidden_problem(self):
        """비공개 문제의 힌트 히스토리는 조회할 수 없어야 함"""
        self.client.force_login(self.user)

        # setUp에서 미리 만들어둔 hidden_problem 사용
        resp = self.client.get(f"{self.url}?problem_id={self.hidden_problem._id}")

        self.assertIsNotNone(resp.data.get("error"))
        self.assertIn("문제를 찾을 수 없습니다.", resp.data.get("data", ""))

    def test_get_history_with_contest_problem(self):
        """대회용 문제의 힌트 히스토리는 일반 API로 조회할 수 없어야 함"""
        self.client.force_login(self.user)

        # 대회 및 대회용 문제 임시 생성
        from contest.models import Contest
        from contest.tests import DEFAULT_CONTEST_DATA
        contest = Contest.objects.create(created_by=self.admin, **DEFAULT_CONTEST_DATA)
        contest_problem = self.create_problem_with_custom_field(self.admin, _id="C-999")
        contest_problem.contest = contest
        contest_problem.save(update_fields=["contest"])

        resp = self.client.get(f"{self.url}?problem_id={contest_problem._id}")

        self.assertIsNotNone(resp.data.get("error"))
        self.assertIn("문제를 찾을 수 없습니다.", resp.data.get("data", ""))

    def test_get_history_with_invalid_problem_id(self):
        """존재하지 않는 문제 ID를 넣었을 때 처리"""
        self.client.force_login(self.user)
        resp = self.client.get(f"{self.url}?problem_id=INVALID_ID")

        self.assertIsNotNone(resp.data.get("error"))
        self.assertIn("문제를 찾을 수 없습니다.", resp.data.get("data", ""))


class ContestProblemAdminTest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.url = self.reverse("contest_problem_admin_api")
        self.create_admin()
        contest_data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        contest_data["allow_paste"] = True
        contest_data["start_time"] = timezone.localtime(timezone.now())
        contest_data["end_time"] = timezone.localtime(timezone.now()) + timedelta(days=1)
        resp = self.client.post(self.reverse("contest_admin_api"), data=contest_data)
        self.assertSuccess(resp)
        self.contest = resp.data["data"]

    def test_create_contest_problem(self):
        data = copy.deepcopy(DEFAULT_PROBLEM_DATA)
        data["contest_id"] = self.contest["id"]
        resp = self.client.post(self.url, data=data)
        self.assertSuccess(resp)
        return resp.data["data"]

    def test_get_contest_problem(self):
        self.test_create_contest_problem()
        contest_id = self.contest["id"]
        resp = self.client.get(self.url + "?contest_id=" + str(contest_id))
        self.assertSuccess(resp)
        self.assertEqual(len(resp.data["data"]["results"]), 1)

    def test_get_one_contest_problem(self):
        contest_problem = self.test_create_contest_problem()
        contest_id = self.contest["id"]
        problem_id = contest_problem["id"]
        resp = self.client.get(f"{self.url}?contest_id={contest_id}&id={problem_id}")
        self.assertSuccess(resp)


class ContestProblemTest(ProblemCreateTestBase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        admin = self.create_admin()
        url = self.reverse("contest_admin_api")
        contest_data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        contest_data["allow_paste"] = True
        contest_data["password"] = ""
        contest_data["start_time"] = timezone.localtime(timezone.now()) + timedelta(hours=1)
        contest_data["end_time"] = timezone.localtime(timezone.now()) + timedelta(days=2)
        resp = self.client.post(url, data=contest_data)
        self.assertSuccess(resp)
        self.contest = resp.data["data"]
        self.problem = self.add_problem(DEFAULT_PROBLEM_DATA, admin)
        self.problem.contest_id = self.contest["id"]
        self.problem.save()
        self.url = self.reverse("contest_problem_api")

    def test_admin_get_contest_problem_list(self):
        contest_id = self.contest["id"]
        resp = self.client.get(self.url + "?contest_id=" + str(contest_id))
        self.assertSuccess(resp)
        self.assertEqual(len(resp.data["data"]), 1)

    def test_admin_get_one_contest_problem(self):
        contest_id = self.contest["id"]
        problem_id = self.problem._id
        resp = self.client.get("{}?contest_id={}&problem_id={}".format(self.url, contest_id, problem_id))
        self.assertSuccess(resp)

    def test_regular_user_get_not_started_contest_problem(self):
        self.create_user(email="test@test.com", username="test", password="test1234!")
        resp = self.client.get(self.url + "?contest_id=" + str(self.contest["id"]))
        self.assertDictEqual(resp.data, {"error": "error", "data": "Contest has not started yet."})

    def test_reguar_user_get_started_contest_problem(self):
        self.create_user(email="test@test.com", username="test", password="test1234!")
        contest = Contest.objects.first()
        contest.start_time = contest.start_time - timedelta(hours=1)
        contest.save()
        resp = self.client.get(self.url + "?contest_id=" + str(self.contest["id"]))
        self.assertSuccess(resp)


class AddProblemFromPublicProblemAPITest(ProblemCreateTestBase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        admin = self.create_admin()
        url = self.reverse("contest_admin_api")
        contest_data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        contest_data["allow_paste"] = True
        contest_data["password"] = ""
        contest_data["start_time"] = timezone.localtime(timezone.now()) + timedelta(hours=1)
        contest_data["end_time"] = timezone.localtime(timezone.now()) + timedelta(days=2)
        resp = self.client.post(url, data=contest_data)
        self.assertSuccess(resp)
        self.contest = resp.data["data"]
        self.problem = self.add_problem(DEFAULT_PROBLEM_DATA, admin)
        self.url = self.reverse("add_contest_problem_from_public_api")
        self.data = {"display_id": "1000", "contest_id": self.contest["id"], "problem_id": self.problem.id}

    def test_add_contest_problem(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        self.assertTrue(Problem.objects.all().exists())
        self.assertTrue(Problem.objects.filter(contest_id=self.contest["id"]).exists())


class ParseProblemTemplateTest(APITestCase):

    def test_parse(self):
        template_str = """
//PREPEND BEGIN
aaa
//PREPEND END

//TEMPLATE BEGIN
bbb
//TEMPLATE END

//APPEND BEGIN
ccc
//APPEND END
"""

        ret = parse_problem_template(template_str)
        self.assertEqual(ret["prepend"], "aaa\n")
        self.assertEqual(ret["template"], "bbb\n")
        self.assertEqual(ret["append"], "ccc\n")

    def test_parse1(self):
        template_str = """
//PREPEND BEGIN
aaa
//PREPEND END

//APPEND BEGIN
ccc
//APPEND END
//APPEND BEGIN
ddd
//APPEND END
"""

        ret = parse_problem_template(template_str)
        self.assertEqual(ret["prepend"], "aaa\n")
        self.assertEqual(ret["template"], "")
        self.assertEqual(ret["append"], "ccc\n")


class UpdateWeeklyStatsTest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.admin = self.create_super_admin()
        self.data = copy.deepcopy(DEFAULT_PROBLEM_DATA)
        self.url = self.reverse("update_weekly_stats_api")

        self.problem_1 = ProblemCreateTestBase.create_problem_with_custom_field(self.admin, _id="A-1")
        self.problem_2 = ProblemCreateTestBase.create_problem_with_custom_field(self.admin, _id="A-2")
        self.problem_3 = ProblemCreateTestBase.create_problem_with_custom_field(self.admin, _id="A-3")

    def test_update_weekly_stats(self):
        week_info_1 = {
            'submission': 10,
            'accepted': 5,
            'success_rate': 0.5,
            'solver': ['user1', 'user2', 'user3', 'user4', 'user5'],
        }
        week_info_2 = {
            'submission': 10,
            'accepted': 3,
            'success_rate': 0.3,
            'solver': ['user1', 'user2', 'user3'],
        }
        week_info_3 = { # This problem will be marked as most difficult
            'submission': 10,
            'accepted': 1,
            'success_rate': 0.1,
            'solver': ['user1'],
        }

        self.problem_1.curr_week_info = week_info_1
        self.problem_1.save(update_fields=['curr_week_info'])
        self.problem_2.curr_week_info = week_info_2
        self.problem_2.save(update_fields=['curr_week_info'])
        self.problem_3.curr_week_info = week_info_3
        self.problem_3.save(update_fields=['curr_week_info'])

        # Check is_most_difficult = false before update
        self.assertFalse(self.problem_1.is_most_difficult)
        self.assertFalse(self.problem_2.is_most_difficult)
        self.assertFalse(self.problem_3.is_most_difficult)

        update_weekly_stats()

        updated_problem_1 = Problem.objects.get(id=self.problem_1.id)
        updated_problem_2 = Problem.objects.get(id=self.problem_2.id)
        updated_problem_3 = Problem.objects.get(id=self.problem_3.id)

        # Check last_week_info and curr_week_info are updated
        self.assertEqual(updated_problem_1.last_week_info, week_info_1)
        self.assertEqual(updated_problem_1.curr_week_info, get_default_week_info())
        self.assertEqual(updated_problem_2.last_week_info, week_info_2)
        self.assertEqual(updated_problem_2.curr_week_info, get_default_week_info())
        self.assertEqual(updated_problem_3.last_week_info, week_info_3)
        self.assertEqual(updated_problem_3.curr_week_info, get_default_week_info())

        # Check is_most_difficult is updated correctly
        self.assertFalse(updated_problem_1.is_most_difficult)
        self.assertFalse(updated_problem_2.is_most_difficult)
        self.assertTrue(updated_problem_3.is_most_difficult)

    def test_update_weekly_stats_database_error(self):

        with mock.patch('problem.models.Problem.objects.update', side_effect=Exception("Database error")):
            with self.assertRaises(Exception):
                update_weekly_stats()


class UpdateBonusProblemTest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.admin = self.create_super_admin()
        self.url = self.reverse("update_bonus_problem_api")

        self.low_problem_1 = ProblemCreateTestBase.create_problem_with_custom_field(
            self.admin,
            _id="A-1",
            difficulty=Difficulty.LOW,
        )
        self.mid_problem_1 = ProblemCreateTestBase.create_problem_with_custom_field(
            self.admin,
            _id="A-2",
            difficulty=Difficulty.MID,
        )
        self.high_problem_1 = ProblemCreateTestBase.create_problem_with_custom_field(
            self.admin,
            _id="A-3",
            difficulty=Difficulty.HIGH,
        )

    def test_update_bonus_problem(self):
        # Check initial state
        self.assertFalse(self.low_problem_1.is_bonus)
        self.assertFalse(self.mid_problem_1.is_bonus)
        self.assertFalse(self.high_problem_1.is_bonus)

        update_bonus_problem()

        updated_low_problem_1 = Problem.objects.get(id=self.low_problem_1.id)
        updated_mid_problem_1 = Problem.objects.get(id=self.mid_problem_1.id)
        updated_high_problem_1 = Problem.objects.get(id=self.high_problem_1.id)

        # Check is_bonus is updated correctly
        self.assertTrue(updated_low_problem_1.is_bonus)
        self.assertTrue(updated_mid_problem_1.is_bonus)
        self.assertTrue(updated_high_problem_1.is_bonus)

    def test_update_bonus_problem_with_existing_bonus(self):
        # Set low_problem_1 as current bonus problem
        self.low_problem_1.is_bonus = True
        self.low_problem_1.save(update_fields=['is_bonus'])

        low_problem_2 = ProblemCreateTestBase.create_problem_with_custom_field(
            self.admin,
            _id="A-4",
            difficulty=Difficulty.LOW,
        )

        # Check initial state
        self.assertTrue(self.low_problem_1.is_bonus)
        self.assertFalse(low_problem_2.is_bonus)
        self.assertFalse(self.mid_problem_1.is_bonus)
        self.assertFalse(self.high_problem_1.is_bonus)

        update_bonus_problem()

        updated_low_problem_1 = Problem.objects.get(id=self.low_problem_1.id)
        updated_low_problem_2 = Problem.objects.get(id=low_problem_2.id)
        updated_mid_problem_1 = Problem.objects.get(id=self.mid_problem_1.id)
        updated_high_problem_1 = Problem.objects.get(id=self.high_problem_1.id)

        # Check is_bonus is updated correctly
        # Since low_problem_1 was bonus, it should not be selected again
        self.assertFalse(updated_low_problem_1.is_bonus)
        self.assertTrue(updated_low_problem_2.is_bonus)
        self.assertTrue(updated_mid_problem_1.is_bonus)
        self.assertTrue(updated_high_problem_1.is_bonus)

    def test_update_bonus_problem_with_contest_problems(self):
        # Ensure other problems are marked as bonus to avoid selection
        self.low_problem_1.is_bonus = True
        self.low_problem_1.save(update_fields=['is_bonus'])
        self.mid_problem_1.is_bonus = True
        self.mid_problem_1.save(update_fields=['is_bonus'])
        self.high_problem_1.is_bonus = True
        self.high_problem_1.save(update_fields=['is_bonus'])

        # Create contest problems (should be excluded from bonus selection)
        contest_data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        contest_data["allow_paste"] = True
        contest_data["start_time"] = timezone.localtime(timezone.now())
        contest_data["end_time"] = timezone.localtime(timezone.now()) + timedelta(days=1)
        resp = self.client.post(self.reverse("contest_admin_api"), data=contest_data)
        self.assertSuccess(resp)
        contest = resp.data["data"]

        contest_problem = ProblemCreateTestBase.create_problem_with_custom_field(
            self.admin,
            _id="C-1",
            difficulty=Difficulty.LOW,
            contest_id=contest["id"],
        )

        update_bonus_problem()

        # Contest problem should not be selected as bonus
        updated_contest_problem = Problem.objects.get(id=contest_problem.id)
        self.assertFalse(updated_contest_problem.is_bonus)

    def test_update_bonus_problem_with_invisible_problems(self):
        #Ensure other problems are marked as bonus to avoid selection
        self.low_problem_1.is_bonus = True
        self.low_problem_1.save(update_fields=['is_bonus'])
        self.mid_problem_1.is_bonus = True
        self.mid_problem_1.save(update_fields=['is_bonus'])
        self.high_problem_1.is_bonus = True
        self.high_problem_1.save(update_fields=['is_bonus'])

        # Create an invisible problem
        invisible_problem = ProblemCreateTestBase.create_problem_with_custom_field(
            self.admin,
            _id="A-6",
            difficulty=Difficulty.LOW,
            visible=False,
        )

        update_bonus_problem()

        # Invisible problem should not be selected as bonus
        updated_invisible_problem = Problem.objects.get(id=invisible_problem.id)
        self.assertFalse(updated_invisible_problem.is_bonus)

    def test_update_bonus_problem_with_database_error(self):
        with mock.patch('problem.models.Problem.objects.filter', side_effect=DatabaseError("Database error")):
            with self.assertRaises(DatabaseError):
                update_bonus_problem()
