import copy
from datetime import timedelta

from account.models import User
from contest.models import Contest
from contest.tests import DEFAULT_CONTEST_DATA
from django.utils import timezone
from problem.models import Problem
from problem.tests import DEFAULT_PROBLEM_DATA, ProblemCreateTestBase
from utils.api.tests import APITestCase

from .models import Comment, Post


class CommunityAPITest(APITestCase):

    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")

        # 사용자 생성
        self.user = self.create_user(email="test@test.com", username="testuser", password="password")
        self.other_user = self.create_user(
            email="other@test.com",
            username="otheruser",
            password="password",
        )
        self.admin = self.create_super_admin(email="admin@test.com", username="admin", password="password")

        # 테스트 데이터 생성
        self.problem = ProblemCreateTestBase.create_problem_with_custom_field(
            self.admin,
            _id="PROB001",
            title="Test Problem",
            description="Description",
        )

        contest_data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        contest_data["start_time"] = timezone.now() - timedelta(hours=1)
        contest_data["end_time"] = timezone.now() + timedelta(hours=1)
        contest_data["password"] = ""
        self.client.force_login(self.admin)
        contest_resp = self.client.post(self.reverse("contest_admin_api"), data=contest_data)
        self.assertSuccess(contest_resp)
        self.contest = contest_resp.data["data"]
        self.client.logout()

        # 비공개 대회 생성
        contest_data["password"] = "private"
        self.client.force_login(self.admin)
        contest_resp = self.client.post(self.reverse("contest_admin_api"), data=contest_data)
        self.private_contest = contest_resp.data["data"]
        self.client.logout()

        self.general_post = Post.objects.create(title="General Post", content="Content", author=self.user)

        # URL
        self.post_list_url = self.reverse("community_posts")
        self.post_detail_url = self.reverse("community_post_detail", kwargs={"post_id": self.general_post.id})

    # Post API Tests
    def test_create_general_post_unauthenticated(self):
        """비로그인 사용자는 게시글을 생성할 수 없다."""
        response = self.client.post(self.post_list_url, {"title": "New", "content": "Content"})
        self.assertFailed(response)

    def test_create_general_post_authenticated(self):
        """로그인 사용자는 일반 게시글을 생성할 수 있다."""
        self.client.force_login(self.user)
        response = self.client.post(
            self.post_list_url,
            {
                "title": "New Post",
                "content": "Content",
                "post_type": "ARTICLE"
            },
        )
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["title"], "New Post")
        self.assertEqual(response.data["data"]["community_type"], "GENERAL")

    def test_create_announcement_post_by_non_super_admin(self):
        """일반 사용자는 공지사항 게시글을 생성할 수 없다."""
        self.client.force_login(self.user)
        response = self.client.post(
            self.post_list_url,
            {
                "title": "Announcement Post",
                "content": "Content",
                "post_type": "ANNOUNCEMENT"
            },
        )
        self.assertFailed(response, "Only Super Admin can create announcement posts")

    def test_create_announcement_post_by_super_admin(self):
        """Super Admin은 공지사항 게시글을 생성할 수 있다."""
        self.client.force_login(self.admin)
        response = self.client.post(
            self.post_list_url,
            {
                "title": "Announcement Post",
                "content": "Content",
                "post_type": "ANNOUNCEMENT"
            },
        )
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["post_type"], "ANNOUNCEMENT")

    def test_create_problem_post(self):
        """문제에 대한 게시글을 생성할 수 있다."""
        self.client.force_login(self.user)
        response = self.client.post(
            self.post_list_url,
            {
                "title": "Problem Post",
                "content": "Content",
                "post_type": "QUESTION",
                "problem_id": self.problem.id,
            },
        )
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["community_type"], "PROBLEM")
        self.assertEqual(response.data["data"]["question_status"], "OPEN")

    def test_create_post_with_both_contest_and_problem(self):
        """대회와 문제를 동시에 지정하여 게시글을 생성할 수 없다."""
        self.client.force_login(self.user)
        response = self.client.post(
            self.post_list_url,
            {
                "title": "Invalid Post",
                "content": "Content",
                "post_type": "ARTICLE",
                "contest_id": self.contest["id"],
                "problem_id": self.problem.id,
            },
        )
        self.assertFailed(response, "Cannot specify both contest and problem")

    def test_contest_permission_denied(self):
        """대회에 대한 접근 권한이 없는 사용자는 대회 게시글을 생성할 수 없다."""
        self.client.force_login(self.other_user)
        response = self.client.post(
            self.post_list_url,
            {
                "title": "Contest Post",
                "content": "Content",
                "post_type": "ARTICLE",
                "contest_id": self.private_contest["id"],
            },
        )

        self.assertFailed(response, "No permission to access this contest's community")

    def test_contest_not_exist(self):
        """존재하지 않는 대회에 대한 게시글을 생성할 수 없다."""
        self.client.force_login(self.user)
        response = self.client.post(
            self.post_list_url,
            {
                "title": "Contest Post",
                "content": "Content",
                "post_type": "ARTICLE",
                "contest_id": 9999,
            },
        )
        self.assertFailed(response, "Contest does not exist")

    def test_problem_not_exist(self):
        """존재하지 않는 문제에 대한 게시글을 생성할 수 없다."""
        self.client.force_login(self.user)
        response = self.client.post(
            self.post_list_url,
            {
                "title": "Problem Post",
                "content": "Content",
                "post_type": "ARTICLE",
                "problem_id": 9999,
            },
        )
        self.assertFailed(response, "Problem does not exist")

    def test_create_contest_post(self):
        """대회에 대한 게시글을 생성할 수 있다."""
        self.client.force_login(self.user)
        response = self.client.post(
            self.post_list_url,
            {
                "title": "Contest Post",
                "content": "Content",
                "post_type": "ARTICLE",
                "contest_id": self.contest["id"],
            },
        )
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["community_type"], "CONTEST")

    def test_get_post_list(self):
        """게시글 목록을 조회할 수 있다."""
        response = self.client.get(self.post_list_url)
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 1)

    def test_get_contest_post_list(self):
        """대회 게시글 목록을 조회할 수 있다."""
        # 대회 게시글 생성
        self.client.force_login(self.user)
        self.client.post(
            self.post_list_url,
            {
                "title": "Contest Post",
                "content": "Content",
                "post_type": "ARTICLE",
                "contest_id": self.contest["id"],
            },
        )

        response = self.client.get(self.post_list_url, {"contest_id": self.contest["id"]})
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 1)

    def test_get_contest_post_list_no_permission(self):
        """대회에 대한 접근 권한이 없는 사용자는 대회 게시글 목록을 조회할 수 없다."""
        # 비공개 대회 게시글 생성
        self.client.force_login(self.admin)
        self.client.post(
            self.post_list_url,
            {
                "title": "Private Contest Post",
                "content": "Content",
                "post_type": "ARTICLE",
                "contest_id": self.private_contest["id"],
            },
        )
        self.client.logout()

        response = self.client.get(self.post_list_url, {"contest_id": self.private_contest["id"]})
        self.assertFailed(response, "No permission to access this contest's community")

    def test_get_contest_list_contest_not_exist(self):
        """존재하지 않는 대회에 대한 게시글 목록을 조회할 수 없다."""
        response = self.client.get(self.post_list_url, {"contest_id": 9999})
        self.assertFailed(response, "Contest does not exist")

    def test_get_problem_post_list(self):
        """문제 게시글 목록을 조회할 수 있다."""
        # 문제 게시글 생성
        self.client.force_login(self.user)
        self.client.post(
            self.post_list_url,
            {
                "title": "Problem Post",
                "content": "Content",
                "post_type": "ARTICLE",
                "problem_id": self.problem.id,
            },
        )

        response = self.client.get(self.post_list_url, {"problem_id": self.problem.id})
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 1)

    def test_get_post_list_with_post_type(self):
        """특정 유형의 게시글 목록을 조회할 수 있다."""
        # 질문 게시글 생성
        self.client.force_login(self.user)
        self.client.post(
            self.post_list_url,
            {
                "title": "Question Post",
                "content": "Content",
                "post_type": "QUESTION",
            },
        )
        self.client.post(
            self.post_list_url,
            {
                "title": "Closed Question Post",
                "content": "Content",
                "post_type": "QUESTION",
            },
        )

        # 질문 게시글 상태를 'CLOSED'로 변경
        closed_post = Post.objects.get(title="Closed Question Post")
        closed_post.question_status = Post.QuestionStatus.CLOSED
        closed_post.save()

        self.client.post(
            self.post_list_url,
            {
                "title": "Article Post",
                "content": "Content",
                "post_type": "ARTICLE",
            },
        )

        response = self.client.get(self.post_list_url, {"post_type": "QUESTION"})
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 2)

        # self.general_post + 방금 생성한 ARTICLE 게시글
        response = self.client.get(self.post_list_url, {"post_type": "ARTICLE"})
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 2)

        response = self.client.get(self.post_list_url, {"question_status": "CLOSED"})
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 1)

    def test_get_post_list_with_keyword(self):
        """키워드로 게시글을 필터링할 수 있다."""
        # 테스트 데이터 준비
        self.client.force_login(self.user)
        self.client.post(self.post_list_url, {"title":"HI Annyeong", "content" : "What Im saying is HIIIIIIII","post_type" : "ARTICLE" })
        self.client.post(self.post_list_url, {"title":"HI Annyeong", "content" : "What Im saying is HIIIIIIII","post_type" : "QUESTION" })
        self.client.post(self.post_list_url, {"title":"Bye Jalga", "content" : "What Im saying is B22222","post_type" : "ARTICLE" })

        # API 호출
        response = self.client.get(self.post_list_url, {"keyword" : "HI"})
        # 상태값 검증
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 2)

        # API 호출
        response = self.client.get(self.post_list_url, {"keyword" : "Bye"})
        # 상태값 검증
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 1)

        # API 호출
        response = self.client.get(self.post_list_url, {"keyword" : "is"})
        # 상태값 검증
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"],3)
    
    def test_get_post_list_order_by_newest(self):
        """게시글을 최신 순으로 정렬할 수 있다."""
        #테스트 데이터 준비
        self.client.force_login(self.user)
        self.client.post(self.post_list_url, {"title" : "Post1", "content": "content1", "post_type": "ARTICLE"})
        self.client.post(self.post_list_url, {"title" : "Post2", "content": "content2", "post_type": "QUESTION"})
        self.client.post(self.post_list_url, {"title" : "Post3", "content": "content3", "post_type": "ARTICLE"})

        # API 호출
        response = self.client.get(self.post_list_url, {"sort_type" : "NEWEST"})
        # 상태값 검증
        self.assertSuccess(response)
        results = response.data["data"]["results"]
        self.assertEqual(results[0]["title"], "Post3")
        self.assertEqual(results[1]["title"], "Post2")
        self.assertEqual(results[2]["title"], "Post1")

    def test_get_post_list_order_by_oldest(self):
        """게시글을 오래된 순으로 정렬할 수 있다."""
        #테스트 데이터 준비
        self.client.force_login(self.user)
        self.client.post(self.post_list_url, {"title" : "Post1", "content": "content1", "post_type": "ARTICLE"})
        self.client.post(self.post_list_url, {"title" : "Post2", "content": "content2", "post_type": "QUESTION"})
        self.client.post(self.post_list_url, {"title" : "Post3", "content": "content3", "post_type": "ARTICLE"})

        #API 호출
        response = self.client.get(self.post_list_url, {"sort_type" : "OLDEST"})
        #상태값 검증
        self.assertSuccess(response)
        results = response.data["data"]["results"]
        self.assertEqual(results[0]["title"], "Post1")
        self.assertEqual(results[1]["title"], "Post2")
        self.assertEqual(results[2]["title"], "Post3")

    def test_get_post_list_order_by_comments(self):
        """게시글을 댓글 많은 순으로 정렬할 수 있다."""
        #테스트 데이터 준비
        self.client.force_login(self.user)
        ## Post1, 댓글 3개
        self.client.post(self.post_list_url, {"title" : "Post1", "content": "content1", "post_type": "ARTICLE"})
        post1 = Post.objects.get(title="Post1")
        Comment.objects.create(post=post1, author=self.user, content="comment1")
        Comment.objects.create(post=post1, author=self.user, content="comment2")
        Comment.objects.create(post=post1, author=self.user, content="comment3")
        ## Post2, 댓글 5개
        self.client.post(self.post_list_url, {"title" : "Post2", "content": "content2", "post_type": "QUESTION"})
        post2 = Post.objects.get(title="Post2")
        Comment.objects.create(post=post2, author=self.user, content="comment1")
        Comment.objects.create(post=post2, author=self.user, content="comment2")
        Comment.objects.create(post=post2, author=self.user, content="comment3")
        Comment.objects.create(post=post2, author=self.user, content="comment4")
        Comment.objects.create(post=post2, author=self.user, content="comment5")
        ## Post3, 댓글 0개
        self.client.post(self.post_list_url, {"title" : "Post3", "content": "content3", "post_type": "ARTICLE"})

        #API 호출
        response = self.client.get(self.post_list_url, {"sort_type" : "COMMENT"})
        #상태값 검증
        self.assertSuccess(response)
        results = response.data["data"]["results"]
        self.assertEqual(results[0]["title"], "Post2")
        self.assertEqual(results[1]["title"], "Post1")
        self.assertEqual(results[2]["title"], "Post3")

    def test_get_post_detail(self):
        """게시글 상세 정보를 조회할 수 있다."""
        response = self.client.get(self.post_detail_url)
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["title"], self.general_post.title)

    def test_get_post_detail_does_not_exist(self):
        """게시글 상세 정보를 조회할 수 있다."""
        response = self.client.get(self.post_detail_url)
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["title"], self.general_post.title)

    def test_get_post_detail_not_exist(self):
        """존재하지 않는 게시글의 상세 정보를 조회할 수 없다."""
        url = self.reverse("community_post_detail", kwargs={"post_id": 9999})
        response = self.client.get(url)
        self.assertFailed(response, "Post does not exist")

    def test_get_post_detail_private_contest_no_permission(self):
        """대회에 대한 접근 권한이 없는 사용자는 비공개 대회 게시글의 상세 정보를 조회할 수 없다."""
        # 비공개 대회 게시글 생성
        self.client.force_login(self.admin)
        private_post_resp = self.client.post(
            self.post_list_url,
            {
                "title": "Private Contest Post",
                "content": "Content",
                "post_type": "ARTICLE",
                "contest_id": self.private_contest["id"],
            },
        )
        self.assertSuccess(private_post_resp)
        private_post_id = private_post_resp.data["data"]["id"]

        self.client.logout()
        self.client.force_login(self.other_user)

        url = self.reverse("community_post_detail", kwargs={"post_id": private_post_id})
        response = self.client.get(url)
        self.assertFailed(response, "No permission to access this contest's community")

    def test_update_post_by_author(self):
        """게시글 작성자는 게시글을 수정할 수 있다."""
        self.client.force_login(self.user)
        response = self.client.patch(self.post_detail_url, {"title": "Updated Title"})
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["title"], "Updated Title")

    def test_update_post_type_to_announcement_by_non_super_admin(self):
        """일반 사용자는 게시글을 ANNOUNCEMENT 타입으로 변경할 수 없다."""
        self.client.force_login(self.user)
        response = self.client.patch(self.post_detail_url, {"post_type": "ANNOUNCEMENT"})
        self.assertFailed(response, "Only Super Admin can set post type to announcement")

    def test_update_post_type_to_announcement_by_super_admin(self):
        """Super Admin은 게시글을 ANNOUNCEMENT 타입으로 변경할 수 있다."""
        self.client.force_login(self.admin)
        response = self.client.patch(self.post_detail_url, {"post_type": "ANNOUNCEMENT"})
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["post_type"], "ANNOUNCEMENT")

    def test_update_post_by_other_user(self):
        """다른 사용자는 게시글을 수정할 수 없다."""
        self.client.force_login(self.other_user)
        response = self.client.patch(self.post_detail_url, {"title": "Updated by other"})
        self.assertFailed(response, "No permission to edit this post")

    def test_update_post_not_exist(self):
        """존재하지 않는 게시글은 수정할 수 없다."""
        self.client.force_login(self.user)
        url = self.reverse("community_post_detail", kwargs={"post_id": 9999})
        response = self.client.patch(url, {"title": "Updated"})
        self.assertFailed(response, "Post does not exist")

    def test_delete_post_by_author(self):
        """게시글 작성자는 게시글을 삭제할 수 있다."""
        self.client.force_login(self.user)
        response = self.client.delete(self.post_detail_url)
        self.assertSuccess(response)
        self.assertFalse(Post.objects.filter(id=self.general_post.id).exists())

    def test_delete_post_by_admin(self):
        """관리자는 게시글을 삭제할 수 있다."""
        self.client.force_login(self.admin)
        response = self.client.delete(self.post_detail_url)
        self.assertSuccess(response)
        self.assertFalse(Post.objects.filter(id=self.general_post.id).exists())

    def test_delete_post_not_exist(self):
        """존재하지 않는 게시글은 삭제할 수 없다."""
        self.client.force_login(self.user)
        url = self.reverse("community_post_detail", kwargs={"post_id": 9999})
        response = self.client.delete(url)
        self.assertFailed(response, "Post does not exist")

    def test_delete_post_by_other_user(self):
        """다른 사용자는 게시글을 삭제할 수 없다."""
        self.client.force_login(self.other_user)
        response = self.client.delete(self.post_detail_url)
        self.assertFailed(response, "No permission to delete this post")

    def test_get_comment_list(self):
        """게시글의 댓글 목록을 조회할 수 있다."""
        # 댓글 생성
        Comment.objects.create(post=self.general_post, author=self.user, content="Comment 1")
        Comment.objects.create(post=self.general_post, author=self.user, content="Comment 2")

        comment_url = self.reverse("community_post_comments", kwargs={"post_id": self.general_post.id})
        response = self.client.get(comment_url)
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["total"], 2)

    def test_get_comment_list_post_not_exist(self):
        """존재하지 않는 게시글의 댓글 목록을 조회할 수 없다."""
        comment_url = self.reverse("community_post_comments", kwargs={"post_id": 9999})
        response = self.client.get(comment_url)
        self.assertFailed(response, "Post does not exist")

    def test_create_comment(self):
        """로그인 사용자는 댓글을 작성할 수 있다."""
        self.client.force_login(self.user)
        comment_url = self.reverse("community_post_comments", kwargs={"post_id": self.general_post.id})
        response = self.client.post(comment_url, {"content": "This is a comment."})
        self.assertSuccess(response)
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_comment_post_not_exist(self):
        """존재하지 않는 게시글에 댓글을 작성할 수 없다."""
        self.client.force_login(self.user)
        comment_url = self.reverse("community_post_comments", kwargs={"post_id": 9999})
        response = self.client.post(comment_url, {"content": "This is a comment."})
        self.assertFailed(response, "Post does not exist")

    def test_create_comment_without_content(self):
        """내용 없이 댓글을 작성할 수 없다."""
        self.client.force_login(self.user)
        comment_url = self.reverse("community_post_comments", kwargs={"post_id": self.general_post.id})
        response = self.client.post(comment_url, {})
        self.assertFailed(response, "Content is required")

    def test_create_comment_with_parent_comment_not_exist(self):
        """존재하지 않는 부모 댓글을 지정하여 대댓글을 작성할 수 없다."""
        self.client.force_login(self.user)
        comment_url = self.reverse("community_post_comments", kwargs={"post_id": self.general_post.id})
        response = self.client.post(
            comment_url,
            {
                "content": "This is a reply.",
                "parent_comment_id": 9999
            },
        )
        self.assertFailed(response, "Parent comment does not exist")

    def test_create_reply_comment(self):
        """사용자는 대댓글을 작성할 수 있다."""
        self.client.force_login(self.user)
        comment_url = self.reverse("community_post_comments", kwargs={"post_id": self.general_post.id})
        # 부모 댓글 생성
        parent_comment_resp = self.client.post(comment_url, {"content": "Parent comment"})
        self.assertSuccess(parent_comment_resp)
        parent_comment_id = parent_comment_resp.data["data"]["id"]

        # 대댓글 생성
        reply_response = self.client.post(
            comment_url,
            {
                "content": "This is a reply.",
                "parent_comment_id": parent_comment_id
            },
        )
        self.assertSuccess(reply_response)
        self.assertEqual(reply_response.data["data"]["parent_comment"], parent_comment_id)
        self.assertEqual(Comment.objects.count(), 2)

    def test_update_comment_by_author(self):
        """댓글 작성자는 댓글을 수정할 수 있다."""
        self.client.force_login(self.user)
        comment = Comment.objects.create(post=self.general_post, author=self.user, content="Original comment")
        comment_detail_url = self.reverse(
            "community_comment_detail",
            kwargs={
                "post_id": self.general_post.id,
                "comment_id": comment.id
            },
        )
        response = self.client.put(comment_detail_url, {"content": "Updated comment"})
        self.assertSuccess(response)
        self.assertEqual(response.data["data"]["content"], "Updated comment")

    def test_update_comment_comment_not_exist(self):
        """존재하지 않는 댓글은 수정할 수 없다."""
        self.client.force_login(self.user)
        comment_detail_url = self.reverse(
            "community_comment_detail",
            kwargs={
                "post_id": self.general_post.id,
                "comment_id": 9999
            },
        )
        response = self.client.put(comment_detail_url, {"content": "Updated"})
        self.assertFailed(response, "Comment does not exist")

    def test_update_comment_by_other_user(self):
        """다른 사용자는 댓글을 수정할 수 없다."""
        self.client.force_login(self.user)
        comment = Comment.objects.create(post=self.general_post, author=self.user, content="Original comment")
        self.client.logout()

        self.client.force_login(self.other_user)
        comment_detail_url = self.reverse(
            "community_comment_detail",
            kwargs={
                "post_id": self.general_post.id,
                "comment_id": comment.id
            },
        )
        response = self.client.put(comment_detail_url, {"content": "Updated by other"})
        self.assertFailed(response, "No permission to edit this comment")

    def test_update_comment_without_content(self):
        """내용 없이 댓글을 수정할 수 없다."""
        self.client.force_login(self.user)
        comment = Comment.objects.create(post=self.general_post, author=self.user, content="Original comment")
        comment_detail_url = self.reverse(
            "community_comment_detail",
            kwargs={
                "post_id": self.general_post.id,
                "comment_id": comment.id
            },
        )
        response = self.client.put(comment_detail_url, {})
        self.assertFailed(response, "Content cannot be empty")

    def test_delete_comment_by_author(self):
        """댓글 작성자는 댓글을 삭제할 수 있다."""
        self.client.force_login(self.user)
        comment = Comment.objects.create(post=self.general_post, author=self.user, content="To be deleted")
        comment_detail_url = self.reverse(
            "community_comment_detail",
            kwargs={
                "post_id": self.general_post.id,
                "comment_id": comment.id
            },
        )
        response = self.client.delete(comment_detail_url)
        self.assertSuccess(response)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_delete_comment_by_admin(self):
        """관리자는 댓글을 삭제할 수 있다."""
        self.client.force_login(self.user)
        comment = Comment.objects.create(post=self.general_post, author=self.user, content="To be deleted")
        comment_detail_url = self.reverse(
            "community_comment_detail",
            kwargs={
                "post_id": self.general_post.id,
                "comment_id": comment.id
            },
        )
        self.client.logout()

        self.client.force_login(self.admin)
        response = self.client.delete(comment_detail_url)
        self.assertSuccess(response)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_delete_comment_comment_not_exist(self):
        """존재하지 않는 댓글은 삭제할 수 없다."""
        self.client.force_login(self.user)
        comment_detail_url = self.reverse(
            "community_comment_detail",
            kwargs={
                "post_id": self.general_post.id,
                "comment_id": 9999
            },
        )
        response = self.client.delete(comment_detail_url)
        self.assertFailed(response, "Comment does not exist")

    def test_delete_comment_by_other_user(self):
        """다른 사용자는 댓글을 삭제할 수 없다."""
        self.client.force_login(self.user)
        comment = Comment.objects.create(post=self.general_post, author=self.user, content="To be deleted")
        comment_detail_url = self.reverse(
            "community_comment_detail",
            kwargs={
                "post_id": self.general_post.id,
                "comment_id": comment.id
            },
        )
        self.client.logout()

        self.client.force_login(self.other_user)
        response = self.client.delete(comment_detail_url)
        self.assertFailed(response, "No permission to delete this comment")
