from django.db.models import Count, Q
from account.decorators import check_contest_permission, login_required
from contest.models import Contest
from problem.models import Problem
from utils.api import APIView, validate_serializer

from ..models import Comment, Post
from ..serializers import (CommentSerializer, CreatePostSerializer, PostListSerializer, PostDetailSerializer,
                           PostUpdateSerializer)


class PostAPIView(APIView):
    """게시글 생성 및 목록 조회를 위한 API"""

    @check_contest_permission(check_type="community")
    def _check_contest_permission(self, request):
        """대회에 대한 커뮤니티 접근 권한을 확인합니다."""
        return None

    @validate_serializer(CreatePostSerializer)
    @login_required
    def post(self, request):
        """게시글을 생성합니다."""
        data = request.data
        contest_id = data.get("contest_id")
        problem_id = data.get("problem_id")

        if contest_id and problem_id:
            return self.error("Cannot specify both contest and problem")

        # ANNOUNCEMENT 타입은 Super Admin만 생성 가능
        if data["post_type"] == Post.PostType.ANNOUNCEMENT and not request.user.is_super_admin():
            return self.error("Only Super Admin can create announcement posts")

        post_data = {
            "title": data["title"],
            "content": data["content"],
            "author": request.user,
            "post_type": data["post_type"],
        }

        # 질문 게시글인 경우 기본 상태를 'OPEN'으로 설정
        if data["post_type"] == Post.PostType.QUESTION:
            post_data["question_status"] = Post.QuestionStatus.OPEN

        # contest_id가 주어진 경우 대회 존재 여부 및 접근 권한 확인
        if contest_id:
            try:
                self.contest = Contest.objects.get(id=contest_id, visible=True)
                error = self._check_contest_permission(request)
                if error:
                    return self.error("No permission to access this contest's community")
                post_data["contest_id"] = contest_id
            except Contest.DoesNotExist:
                return self.error("Contest does not exist")

        # problem_id가 주어진 경우 문제 존재 여부 확인
        if problem_id:
            try:
                Problem.objects.get(id=problem_id)
                post_data["problem_id"] = problem_id
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")

        post = Post.objects.create(**post_data)
        return self.success(PostDetailSerializer(post).data)

    def get(self, request):
        """게시글 목록을 조회합니다."""
        contest_id = request.GET.get("contest_id")
        problem_id = request.GET.get("problem_id")
        post_type = request.GET.get("post_type")
        question_status = request.GET.get("question_status")
        keyword = request.GET.get("keyword", "").strip()
        sort_type = request.GET.get("sort_type")

        posts = Post.objects.select_related("author__userprofile").annotate(
            comment_count=Count('comments')).all().order_by("-created_at")
        if contest_id:
            try:
                self.contest = Contest.objects.get(id=contest_id, visible=True)
                error = self._check_contest_permission(request)
                if error:
                    return self.error("No permission to access this contest's community")
                posts = posts.filter(contest_id=contest_id)
            except Contest.DoesNotExist:
                return self.error("Contest does not exist")
        elif problem_id:
            posts = posts.filter(problem_id=problem_id, contest_id__isnull=True)
        else:
            # 질문 내부 문제 커뮤니티에 로드 (추가)
            posts = posts.filter(contest_id__isnull=True)
        if post_type:
            posts = posts.filter(post_type=post_type)

        if question_status:
            posts = posts.filter(question_status=question_status)
        
        if keyword:
            posts = posts.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )

        if sort_type == Post.SortType.NEWEST:
            posts = posts.order_by("-created_at")
        elif sort_type == Post.SortType.OLDEST:
            posts = posts.order_by("created_at")
        elif sort_type == Post.SortType.COMMENT:
            posts = posts.order_by("-comment_count")
        else:
            posts = posts.order_by("-created_at")

        data = self.paginate_data(request, posts, PostListSerializer)
        return self.success(data)


class PostDetailAPIView(APIView):
    """특정 게시글 조회, 수정, 삭제를 위한 API"""

    def get_post(self, post_id):
        """특정 ID의 게시글을 조회합니다."""
        try:
            return (Post.objects.select_related("author", "contest", "problem").prefetch_related(
                "comments__author__userprofile", "comments__replies__author__userprofile").get(id=post_id))
        except Post.DoesNotExist:
            return None

    @check_contest_permission(check_type="community")
    def _check_contest_permission(self, request):
        return None

    def get(self, request, post_id):
        """특정 게시글을 조회합니다."""
        post = self.get_post(post_id)
        if not post:
            return self.error("Post does not exist")

        if post.contest:
            self.contest = post.contest
            error = self._check_contest_permission(request)
            if error:
                return self.error("No permission to access this contest's community")

        return self.success(PostDetailSerializer(post).data)

    @validate_serializer(PostUpdateSerializer)
    @login_required
    def patch(self, request, post_id):
        """특정 게시글을 수정합니다."""
        post = self.get_post(post_id)
        if not post:
            return self.error("Post does not exist")

        if post.author != request.user and not request.user.is_super_admin():
            return self.error("No permission to edit this post")

        data = request.data

        # ANNOUNCEMENT 타입으로 변경하려는 경우 Super Admin 권한 체크
        if "post_type" in data and data["post_type"] == Post.PostType.ANNOUNCEMENT:
            if not request.user.is_super_admin():
                return self.error("Only Super Admin can set post type to announcement")

        # 수정 요청 이전의 게시글 종류 저장
        old_post_type = post.post_type

        for key, value in data.items():
            setattr(post, key, value)
        
        # 질문 타입으로 변경 시, 상태가 없거나 이전 타입이 일반글이었다면 미해결로 초기화
        if post.post_type == Post.PostType.QUESTION:
            if old_post_type == Post.PostType.ARTICLE or not post.question_status:
                post.question_status = Post.QuestionStatus.OPEN
        # db저장
        post.save()

        return self.success(PostDetailSerializer(post).data)

    @login_required
    def delete(self, request, post_id):
        """특정 게시글을 삭제합니다."""
        post = self.get_post(post_id)
        if not post:
            return self.error("Post does not exist")

        if post.author != request.user and not request.user.is_super_admin():
            return self.error("No permission to delete this post")

        post.delete()
        return self.success()


class CommentAPIView(APIView):
    """특정 게시글의 댓글 생성 및 목록 조회를 위한 API"""

    def get(self, request, post_id):
        """댓글 목록을 조회합니다."""
        try:
            Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return self.error("Post does not exist")

        comments = (Comment.objects.filter(
            post_id=post_id).select_related("author").prefetch_related("replies__author").order_by("created_at"))

        root_comments = comments.filter(parent_comment__isnull=True)
        data = self.paginate_data(request, root_comments, CommentSerializer)
        return self.success(data)

    @login_required
    def post(self, request, post_id):
        """댓글을 생성합니다."""
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return self.error("Post does not exist")

        content = request.data.get("content")
        parent_comment_id = request.data.get("parent_comment_id")

        if not content:
            return self.error("Content is required")

        parent_comment = None
        if parent_comment_id:
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id, post=post)
            except Comment.DoesNotExist:
                return self.error("Parent comment does not exist")

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent_comment=parent_comment,
        )
        return self.success(CommentSerializer(comment).data)


class CommentDetailAPIView(APIView):
    """특정 댓글 수정 및 삭제를 위한 API"""

    @login_required
    def put(self, request, post_id, comment_id):
        """댓글을 수정합니다."""
        try:
            comment = Comment.objects.get(id=comment_id, post_id=post_id)
        except Comment.DoesNotExist:
            return self.error("Comment does not exist")

        if comment.author != request.user and not request.user.is_super_admin():
            return self.error("No permission to edit this comment")

        content = request.data.get("content")
        if not content:
            return self.error("Content cannot be empty")

        comment.content = content
        comment.save()
        return self.success(CommentSerializer(comment).data)

    @login_required
    def delete(self, request, post_id, comment_id):
        """댓글을 삭제합니다."""
        try:
            comment = Comment.objects.get(id=comment_id, post_id=post_id)
        except Comment.DoesNotExist:
            return self.error("Comment does not exist")

        if comment.author != request.user and not request.user.is_super_admin():
            return self.error("No permission to delete this comment")

        comment.delete()
        return self.success()
