from utils.api import APIView, validate_serializer
from account.decorators import login_required
from account.decorators import check_contest_permission

from ..models import Post, Comment
from ..serializers import PostSerializer, CreatePostSerializer, CommentSerializer
from contest.models import Contest, ContestStatus
from problem.models import Problem


class PostAPIView(APIView):
    """게시글 생성 및 목록 조회를 위한 API"""

    @check_contest_permission(check_type="community")
    def _check_contest_permission(self, request):
        """대회에 대한 커뮤니티 접근 권한을 확인합니다."""
        return None

    @validate_serializer(CreatePostSerializer)
    @login_required
    def post(self, request):
        """게시글을 생성하는 API입니다."""
        data = request.data
        contest_id = data.get("contest_id")
        problem_id = data.get("problem_id")

        if contest_id and problem_id:
            return self.error("Cannot specify both contest and problem")

        if contest_id:
            try:
                self.contest = Contest.objects.get(id=contest_id, visible=True)
                error = self._check_contest_permission(request)
                if error:
                    return error
            except Contest.DoesNotExist:
                return self.error("Contest does not exist")

        if problem_id:
            try:
                problem = Problem.objects.get(id=problem_id)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")

        post = Post.objects.create(
            title=data["title"],
            content=data["content"],
            author=request.user,
            post_type=data["post_type"],
            contest_id=contest_id,
            problem_id=problem_id,
        )
        return self.success(PostSerializer(post).data)

    def get(self, request):
        """게시글 목록 조회 (List)"""
        contest_id = request.GET.get("contest_id")
        problem_id = request.GET.get("problem_id")
        post_type = request.GET.get("post_type")

        posts = Post.objects.select_related("author").all()

        if contest_id:
            try:
                self.contest = Contest.objects.get(id=contest_id, visible=True)
                error = self._check_contest_permission(request)
                if error:
                    return error
                posts = posts.filter(contest_id=contest_id)
            except Contest.DoesNotExist:
                return self.error("Contest does not exist")
        elif problem_id:
            posts = posts.filter(problem_id=problem_id, contest__isnull=True)
        else:
            # 일반 커뮤니티 게시글 (대회/문제에 속하지 않음)
            posts = posts.filter(contest__isnull=True, problem__isnull=True)

        if post_type:
            posts = posts.filter(post_type=post_type)

        data = self.paginate_data(request, posts, PostSerializer)
        return self.success(data)


class PostDetailAPIView(APIView):
    """특정 게시글 조회, 수정, 삭제를 위한 API"""

    @check_contest_permission(check_type="community")
    def _check_contest_permission(self, request):
        """대회 커뮤니티 접근 권한 확인"""
        # contest = self.contest
        # if (
        #     contest.status == ContestStatus.CONTEST_NOT_START
        #     and not request.user.is_contest_admin(contest)
        # ):
        #     return self.error("The contest has not started yet")
        return None

    def get(self, request, post_id):
        """특정 게시글 조회 (Retrieve)"""
        try:
            post = Post.objects.select_related("author").get(id=post_id)
        except Post.DoesNotExist:
            return self.error("Post does not exist")

        if post.contest:
            self.contest = post.contest
            error = self._check_contest_permission(request)
            if error:
                return error

        return self.success(PostSerializer(post).data)

    @validate_serializer(CreatePostSerializer)
    @login_required
    def put(self, request, post_id):
        """특정 게시글 수정 (Update)"""
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return self.error("Post does not exist")

        # 작성자 또는 관리자만 수정 가능
        if post.author != request.user and not request.user.is_admin_role():
            return self.error("No permission to edit this post")

        data = request.data
        post.title = data.get("title", post.title)
        post.content = data.get("content", post.content)
        post.post_type = data.get("post_type", post.post_type)
        post.save()

        return self.success(PostSerializer(post).data)

    @login_required
    def delete(self, request, post_id):
        """게시글 삭제 (Delete)"""
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return self.error("Post does not exist")

        # 작성자 또는 관리자만 삭제 가능
        if post.author != request.user and not request.user.is_admin_role():
            return self.error("No permission to delete this post")

        post.delete()
        return self.success()


class CommentAPIView(APIView):
    """특정 게시글의 댓글 생성 및 목록 조회를 위한 API"""

    def get(self, request, post_id):
        """
        댓글 목록 조회
        """
        try:
            Post.objects.get(id=post_id)  # 게시글 존재 여부 확인
        except Post.DoesNotExist:
            return self.error("Post does not exist")

        comments = (Comment.objects.filter(post_id=post_id).select_related("author").order_by("created_at"))

        # 대댓글 구조를 위해 parent_comment가 null인 댓글만 먼저 가져옴
        root_comments = comments.filter(parent_comment__isnull=True)
        data = self.paginate_data(request, root_comments, CommentSerializer)

        # TODO: 대댓글(replies)을 효율적으로 포함시키는 로직 추가 필요 (예: 재귀적 serializer)
        return self.success(data)

    @login_required
    def post(self, request, post_id):
        """
        댓글 생성
        """
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
    """
    특정 댓글 수정 및 삭제를 위한 API
    """

    @login_required
    def put(self, request, comment_id):
        """
        댓글 수정
        """
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return self.error("Comment does not exist")

        if comment.author != request.user and not request.user.is_admin_role():
            return self.error("No permission to edit this comment")

        content = request.data.get("content")
        if not content:
            return self.error("Content cannot be empty")

        comment.content = content
        comment.save()
        return self.success(CommentSerializer(comment).data)

    @login_required
    def delete(self, request, comment_id):
        """댓글 삭제"""
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return self.error("Comment does not exist")

        if comment.author != request.user and not request.user.is_admin_role():
            return self.error("No permission to delete this comment")

        comment.delete()
        return self.success()
