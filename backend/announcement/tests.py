from datetime import timedelta

from django.utils import timezone

from utils.api.tests import APITestCase

from .models import Announcement


class AnnouncementAdminTest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.user = self.create_super_admin()
        self.url = self.reverse("announcement_admin_api")

    def test_announcement_list(self):
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def create_announcement(self):
        return self.client.post(
            self.url, data={
                "title": "test",
                "content": "test",
                "visible": True,
                "is_pinned": False
            })

    def test_create_announcement(self):
        resp = self.create_announcement()
        self.assertSuccess(resp)
        return resp

    def test_edit_announcement(self):
        """
        공지사항 제목, 내용, 공개, 고정 수정 test
        """
        data = {
            "id": self.create_announcement().data["data"]["id"],
            "title": "ahaha",
            "content": "test content",
            "visible": False,
            "is_pinned": True
        }
        resp = self.client.put(self.url, data=data)
        self.assertSuccess(resp)
        resp_data = resp.data["data"]
        self.assertEqual(resp_data["title"], "ahaha")
        self.assertEqual(resp_data["content"], "test content")
        self.assertEqual(resp_data["visible"], False)
        self.assertEqual(resp_data["is_pinned"], True)

    def test_edit_announcement_preserves_release_note_when_omitted(self):
        announcement = Announcement.objects.create(
            title="Release 3.1.10",
            content="release content",
            visible=True,
            is_pinned=False,
            is_release_note=True,
            created_by=self.user,
        )

        resp = self.client.put(
            self.url,
            data={
                "id": announcement.id,
                "title": "Release 3.1.10 updated",
                "content": announcement.content,
                "visible": announcement.visible,
                "is_pinned": announcement.is_pinned,
            },
        )

        self.assertSuccess(resp)
        announcement.refresh_from_db()
        self.assertTrue(announcement.is_release_note)

    def test_admin_toggle_release_note_and_pin(self):
        """
        관리자 공지사항 릴리즈 여부 및 고정 여부 변경 test
        """
        create_resp = self.create_announcement()
        self.assertSuccess(create_resp)
        announcement_id = create_resp.data["data"]["id"]

        # 릴리즈 및 고정으로 변경
        resp = self.client.put(
            self.url,
            data={
                "id": announcement_id,
                "title": "Release v1.0",
                "content": "Release notes",
                "visible": True,
                "is_pinned": True,
                "is_release_note": True,
            },
        )
        self.assertSuccess(resp)
        announcement = Announcement.objects.get(id=announcement_id)
        self.assertTrue(announcement.is_release_note)
        self.assertTrue(announcement.is_pinned)

        # 고정 해제 (릴리즈 여부는 유지)
        resp = self.client.put(
            self.url,
            data={
                "id": announcement_id,
                "title": "Release v1.0",
                "content": "Release notes",
                "visible": True,
                "is_pinned": False,
                "is_release_note": True,
            },
        )
        self.assertSuccess(resp)
        announcement.refresh_from_db()
        self.assertTrue(announcement.is_release_note)
        self.assertFalse(announcement.is_pinned)

    def test_edit_announcement_not_exist(self):
        """
        존재하지 않는 공지사항 수정 test
        """
        data = {"id": -9999, "title": "error trial", "content": "test content", "visible": False, "is_pinned": False}
        resp = self.client.put(self.url, data=data)
        self.assertFailed(resp)
        self.assertEqual(resp.data["data"], "Announcement does not exist")

    def test_delete_announcement(self):
        id = self.test_create_announcement().data["data"]["id"]
        resp = self.client.delete(self.url + "?id=" + str(id))
        self.assertSuccess(resp)
        self.assertFalse(Announcement.objects.filter(id=id).exists())

    def test_get_one_specific_announcement(self):
        """
        존재하는 id 로 공지사항 하나 조회 test
        """
        id = self.test_create_announcement().data["data"]["id"]
        resp = self.client.get(self.url + "?id=" + str(id))
        self.assertSuccess(resp)
        resp_data = resp.data["data"]
        self.assertEqual(resp_data["id"], id)
        self.assertEqual(resp_data["title"], "test")

    def test_get_one_specific_announcement_not_exist(self):
        """
        존재하지 않는 id 로 공지사항 하나 조회 test
        """
        resp = self.client.get(self.url + "?id=-99999")
        self.assertFailed(resp)
        self.assertEqual(resp.data["data"], "Announcement does not exist")

    def test_get_visible_announcement_list(self):
        """
        visible 설정된 공지사항 리스트 가져오기 test
        """
        self.client.post(self.url, data={"title": "보임1", "content": "test", "visible": True, "is_pinned": False})
        self.client.post(self.url, data={"title": "안보임1", "content": "test", "visible": False, "is_pinned": False})
        self.client.post(self.url, data={"title": "보임2", "content": "test", "visible": True, "is_pinned": False})
        resp = self.client.get(self.url + "?visible=true")
        self.assertEqual(len(resp.data["data"]["results"]), 2)
        titles = [announcement["title"] for announcement in resp.data["data"]["results"]]
        self.assertIn("보임1", titles)
        self.assertIn("보임2", titles)

    def test_create_pinned_announcement(self):
        """
        고정된 공지사항 생성 test
        """
        resp = self.client.post(
            self.url, data={
                "title": "고정 공지사항",
                "content": "test",
                "visible": True,
                "is_pinned": True
            })
        self.assertSuccess(resp)
        self.assertEqual(resp.data["data"]["is_pinned"], True)

    def test_get_notice_list_in_order(self):
        """
        공지사항 리스트 조회 시, 고정 공지사항 우선 로드 여부 test
        """
        self.client.post(self.url, data={"title": "고정1", "content": "test", "visible": True, "is_pinned": True})
        self.client.post(self.url, data={"title": "고정아님1", "content": "test", "visible": True, "is_pinned": False})
        self.client.post(self.url, data={"title": "고정2", "content": "test", "visible": True, "is_pinned": True})
        self.client.post(self.url, data={"title": "고정아님2", "content": "test", "visible": True, "is_pinned": False})

        resp = self.client.get(self.url)
        self.assertSuccess(resp)
        results = resp.data["data"]["results"]
        self.assertEqual(len(results), 4)

        self.assertTrue(results[0]["is_pinned"])
        self.assertTrue(results[1]["is_pinned"])
        self.assertFalse(results[2]["is_pinned"])
        self.assertFalse(results[3]["is_pinned"])

        pinned_titles = {results[0]["title"], results[1]["title"]}
        self.assertIn("고정1", pinned_titles)
        self.assertIn("고정2", pinned_titles)


class AnnouncementAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.user = self.create_super_admin()
        self.announcement = Announcement.objects.create(
            title="title", content="content", is_pinned=False, visible=True, created_by=self.user)
        self.url = self.reverse("announcement_api")

    def test_get_announcement_list(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_filter_announcement_list_by_category(self):
        Announcement.objects.create(
            title="Release 3.1.10",
            content="release content",
            is_release_note=True,
            visible=True,
            created_by=self.user,
        )

        general_resp = self.client.get(self.url + "?category=general")
        release_resp = self.client.get(self.url + "?category=release")

        self.assertSuccess(general_resp)
        self.assertSuccess(release_resp)
        self.assertEqual(general_resp.data["data"]["total"], 1)
        self.assertEqual(release_resp.data["data"]["total"], 1)
        self.assertEqual(
            release_resp.data["data"]["results"][0]["title"],
            "Release 3.1.10",
        )

    def test_announcement_detail(self):
        response = self.client.get(self.url + f"?id={self.announcement.id}")
        self.assertSuccess(response)

    def test_release_pinned_ordering(self):
        """
        릴리즈 노트 목록 조회 시 고정된 릴리즈가 상단에 우선 배치되고,
        고정 항목 및 일반 항목 각각 내에서 최신순으로 정렬되는지 test
        """
        now = timezone.now()
        # r1: 과거 작성, 고정
        r1 = Announcement.objects.create(
            title="Release 1.0 (pinned, old)",
            content="content",
            is_release_note=True,
            is_pinned=True,
            visible=True,
            created_by=self.user,
        )
        Announcement.objects.filter(id=r1.id).update(create_time=now - timedelta(days=10))

        # r2: 최근 작성, 미고정
        r2 = Announcement.objects.create(
            title="Release 2.0 (unpinned, recent)",
            content="content",
            is_release_note=True,
            is_pinned=False,
            visible=True,
            created_by=self.user,
        )
        Announcement.objects.filter(id=r2.id).update(create_time=now - timedelta(days=2))

        # r3: 최신 작성, 고정
        r3 = Announcement.objects.create(
            title="Release 3.0 (pinned, newest)",
            content="content",
            is_release_note=True,
            is_pinned=True,
            visible=True,
            created_by=self.user,
        )
        Announcement.objects.filter(id=r3.id).update(create_time=now - timedelta(days=1))

        # r4: 가장 오래된 작성, 미고정
        r4 = Announcement.objects.create(
            title="Release 0.1 (unpinned, oldest)",
            content="content",
            is_release_note=True,
            is_pinned=False,
            visible=True,
            created_by=self.user,
        )
        Announcement.objects.filter(id=r4.id).update(create_time=now - timedelta(days=20))

        resp = self.client.get(self.url + "?category=release")
        self.assertSuccess(resp)
        results = resp.data["data"]["results"]
        self.assertEqual(len(results), 4)

        # 고정된 릴리즈가 먼저 오고 최신순 정렬 (r3 -> r1)
        self.assertEqual(results[0]["id"], r3.id)
        self.assertTrue(results[0]["is_pinned"])
        self.assertEqual(results[1]["id"], r1.id)
        self.assertTrue(results[1]["is_pinned"])

        # 미고정 릴리즈는 그 아래에 최신순 정렬 (r2 -> r4)
        self.assertEqual(results[2]["id"], r2.id)
        self.assertFalse(results[2]["is_pinned"])
        self.assertEqual(results[3]["id"], r4.id)
        self.assertFalse(results[3]["is_pinned"])

    def test_release_unpinning_moves_to_recent(self):
        """
        릴리즈 노트의 고정을 해제하면 상단 고정 영역에서 일반 최신순 목록으로 이동하는지 test
        """
        now = timezone.now()
        # r_old: 과거 작성, 처음에는 고정 상태
        r_old = Announcement.objects.create(
            title="Release 1.0 (initially pinned)",
            content="content",
            is_release_note=True,
            is_pinned=True,
            visible=True,
            created_by=self.user,
        )
        Announcement.objects.filter(id=r_old.id).update(create_time=now - timedelta(days=5))

        # r_new: 최신 작성, 미고정 상태
        r_new = Announcement.objects.create(
            title="Release 2.0 (unpinned)",
            content="content",
            is_release_note=True,
            is_pinned=False,
            visible=True,
            created_by=self.user,
        )
        Announcement.objects.filter(id=r_new.id).update(create_time=now - timedelta(days=1))

        # 고정 상태일 때는 r_old가 r_new보다 우선
        resp1 = self.client.get(self.url + "?category=release")
        self.assertEqual(resp1.data["data"]["results"][0]["id"], r_old.id)

        # r_old의 고정 해제
        Announcement.objects.filter(id=r_old.id).update(is_pinned=False)

        # 고정이 풀리면 최신 작성된 r_new가 r_old보다 우선
        resp2 = self.client.get(self.url + "?category=release")
        results = resp2.data["data"]["results"]
        self.assertEqual(results[0]["id"], r_new.id)
        self.assertEqual(results[1]["id"], r_old.id)

    def test_pinned_items_isolated_by_category(self):
        """
        일반 공지와 릴리즈 노트를 각각 고정했을 때 카테고리별로 정확히 분리되어 조회되는지 test
        """
        Announcement.objects.create(
            title="General Pinned",
            content="content",
            is_release_note=False,
            is_pinned=True,
            visible=True,
            created_by=self.user,
        )
        Announcement.objects.create(
            title="Release Pinned",
            content="content",
            is_release_note=True,
            is_pinned=True,
            visible=True,
            created_by=self.user,
        )

        gen_resp = self.client.get(self.url + "?category=general")
        rel_resp = self.client.get(self.url + "?category=release")

        self.assertSuccess(gen_resp)
        self.assertSuccess(rel_resp)

        # category=general 조회 결과에는 일반 공지만 포함
        gen_titles = [item["title"] for item in gen_resp.data["data"]["results"]]
        self.assertIn("General Pinned", gen_titles)
        self.assertNotIn("Release Pinned", gen_titles)

        # category=release 조회 결과에는 릴리즈 노트만 포함
        rel_titles = [item["title"] for item in rel_resp.data["data"]["results"]]
        self.assertIn("Release Pinned", rel_titles)
        self.assertNotIn("General Pinned", rel_titles)
