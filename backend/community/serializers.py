from account.models import User
from community.models import Comment, Post
from contest.models import Contest
from problem.models import Problem
from rest_framework import serializers


class ReplySerializer(serializers.ModelSerializer):
    """대댓글을 위한 Serializer (재귀 호출의 깊이를 제한)"""

    author_name = serializers.CharField(source="author.username", read_only=True)
    author_avatar = serializers.CharField(source="author.userprofile.avatar", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "author_name",
            "author_avatar",
            "content",
            "parent_comment",
            "created_at",
            "updated_at",
        ]


class CommentSerializer(serializers.ModelSerializer):
    """댓글과 대댓글을 포함하는 Serializer"""

    author_name = serializers.CharField(source="author.username", read_only=True)
    author_avatar = serializers.CharField(source="author.userprofile.avatar", read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "author_name",
            "author_avatar",
            "content",
            "parent_comment",
            "created_at",
            "updated_at",
            "replies",
        ]
        read_only_fields = ["post", "author"]


class PostListSerializer(serializers.ModelSerializer):
    """게시글 목록을 위한 Serializer"""

    content_preview = serializers.SerializerMethodField()
    author_name = serializers.CharField(source="author.username", read_only=True)
    author_avatar = serializers.CharField(source="author.userprofile.avatar", read_only=True)
    community_type = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content_preview",
            "author",
            "author_name",
            "author_avatar",
            "community_type",
            "post_type",
            "question_status",
            "created_at",
            "updated_at",
            "problem",
            "contest",
            "comment_count",
        ]

    def get_content_preview(self, obj):
        """게시글 내용의 미리보기(처음 100자)를 반환합니다."""
        return obj.content[:100] + ("..." if len(obj.content) > 100 else "")

    def get_community_type(self, obj):
        """게시글이 속한 커뮤니티 유형을 반환합니다."""
        if obj.problem_id:
            return Post.CommunityType.PROBLEM
        elif obj.contest_id:
            return Post.CommunityType.CONTEST
        return Post.CommunityType.GENERAL


class PostDetailSerializer(serializers.ModelSerializer):
    """게시글을 위한 Serializer"""

    author_name = serializers.CharField(source="author.username", read_only=True)
    author_avatar = serializers.CharField(source="author.userprofile.avatar", read_only=True)
    community_type = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_name",
            "author_avatar",
            "community_type",
            "post_type",
            "question_status",
            "created_at",
            "updated_at",
            "problem",
            "contest",
            "comments",
        ]

    def get_community_type(self, obj):
        if obj.problem_id:
            return Post.CommunityType.PROBLEM
        elif obj.contest_id:
            return Post.CommunityType.CONTEST
        return Post.CommunityType.GENERAL

    def get_comments(self, obj):
        """게시글에 달린 댓글 중 최상위 댓글(대댓글이 아닌)만 필터링하여 반환합니다."""
        # view에서 prefetch_related를 사용했기 때문에 추가 쿼리가 발생하지 않습니다.
        top_level_comments = [comment for comment in obj.comments.all() if comment.parent_comment_id is None]
        serializer = CommentSerializer(top_level_comments, many=True)
        return serializer.data


class CreatePostSerializer(serializers.Serializer):
    """게시글 생성을 위한 Serializer"""

    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    problem_id = serializers.IntegerField(required=False, allow_null=True)
    contest_id = serializers.IntegerField(required=False, allow_null=True)
    post_type = serializers.ChoiceField(choices=Post.PostType.choices, default=Post.PostType.ARTICLE)


class PostUpdateSerializer(serializers.Serializer):
    """게시글 수정을 위한 Serializer"""

    title = serializers.CharField(max_length=200, required=False)
    content = serializers.CharField(required=False)
    post_type = serializers.ChoiceField(choices=Post.PostType.choices, required=False)
    question_status = serializers.ChoiceField(choices=Post.QuestionStatus.choices, required=False)
