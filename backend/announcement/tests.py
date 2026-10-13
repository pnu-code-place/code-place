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
