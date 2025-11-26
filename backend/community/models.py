from django.db import models

from account.models import User
from contest.models import Contest
from problem.models import Problem
from utils.models import RichTextField


class Post(models.Model):
    """커뮤니티 게시글 모델

    Attributes:
        title (CharField): 게시글 제목 (최대 200자)
        content (RichTextField): 게시글 내용
        author (ForeignKey): 작성자 (User 모델 외래 키)
        problem (ForeignKey): 연관된 문제 (Problem 모델 외래 키, community_type이 'PROBLEM'일 경우)
        contest (ForeignKey): 연관된 대회 (Contest 모델 외래 키, community_type이 'CONTEST'일 경우)
        post_type (CharField): 게시글 종류 (질문, 글, 공지)
        question_status (CharField): 질문 상태 (진행중, 해결됨), post_type이 'QUESTION'일 경우
        created_at (DateTimeField): 생성 일시 (자동 생성)
        updated_at (DateTimeField): 수정 일시 (자동 업데이트)
    """

    class CommunityType(models.TextChoices):
        """게시글의 커뮤니티 종류"""

        GENERAL = "GENERAL", "일반"
        PROBLEM = "PROBLEM", "문제"
        CONTEST = "CONTEST", "대회"

    class PostType(models.TextChoices):
        """게시글의 종류"""

        QUESTION = "QUESTION", "질문"
        ARTICLE = "ARTICLE", "글"
        ANNOUNCEMENT = "ANNOUNCEMENT", "공지"

    class QuestionStatus(models.TextChoices):
        """질문 게시글의 상태"""

        OPEN = "OPEN", "진행중"
        CLOSED = "CLOSED", "해결됨"
        
    class SortType(models.TextChoices):
        """게시글 정렬 순서"""

        NEWEST = "NEWEST", "최신순"
        OLDEST = "OLDEST", "오래된순"
        COMMENT = "COMMENT", "댓글순많은순"


    title = models.CharField(max_length=200)
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    problem = models.ForeignKey(Problem, null=True, blank=True, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, null=True, blank=True, on_delete=models.CASCADE)

    post_type = models.CharField(
        max_length=20,
        choices=PostType.choices,
        default=PostType.ARTICLE,
    )

    question_status = models.CharField(
        max_length=20,
        choices=QuestionStatus.choices,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    """게시글 댓글 모델

    Attributes:
        post (ForeignKey): 댓글이 달린 게시글 (Post 모델 외래 키)
        author (ForeignKey): 댓글 작성자 (User 모델 외래 키)
        content (RichTextField): 댓글 내용
        parent_comment (ForeignKey): 부모 댓글 (대댓글의 경우)
        created_at (DateTimeField): 생성 일시 (자동 생성)
        updated_at (DateTimeField): 수정 일시 (자동 업데이트)
    """

    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField()
    parent_comment = models.ForeignKey("self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]  # 댓글은 오래된 순서대로 정렬
