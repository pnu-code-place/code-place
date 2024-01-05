from .models import Post, Comment, CommentComment
from utils.api import serializers


class SimplePostSerializer(serializers.ModelSerializer):    # body는 넘겨주지 않음 -> body는 DetailPost에서 넘겨줌

    class Meta:
        author = serializers.ReadOnlyField(source="User.id")
        related_problem = serializers.ReadOnlyField(source="Problem.id")

        model = Post
        fields = ["id", "category", "title", "author", "create_time", "related_problem"]


class CommentCommentSerializer(serializers.ModelSerializer):
    class Meta:
        author = serializers.ReadOnlyField(source="User.id")
        parent_comment = serializers.ReadOnlyField(source="Comment.id")

        model = CommentComment
        fields = ["id", "parent_comment", "author", "create_time", "body"]
        ordering = ['create_time']


class CommentSerializer(serializers.ModelSerializer):
    commentcomment_set = CommentCommentSerializer(many=True, read_only=True)

    class Meta:
        author = serializers.ReadOnlyField(source="User.id")
        parent_post = serializers.ReadOnlyField(source="Post.id")

        model = Comment
        fields = ["id", "parent_post", "author", "create_time", "body", "commentcomment_set"]
        ordering = ['create_time']


class DetailPostSerializer(serializers.ModelSerializer):
    comment_set = CommentSerializer(many=True, read_only=True)

    class Meta:
        author = serializers.ReadOnlyField(source="User.id")
        related_problem = serializers.ReadOnlyField(source="Problem.id")

        model = Post
        fields = ["id", "category", "title", "author", "create_time", "body", "related_problem", "comment_set"]
