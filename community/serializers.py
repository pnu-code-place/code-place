from .models import Post, Comment, CommentComment
from utils.api import serializers


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        author = serializers.ReadOnlyField(source="User.id")
        related_problem = serializers.ReadOnlyField(source="Problem.id")

        model = Post
        fields = ["id", "category", "title", "author", "create_time", "related_problem"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        author = serializers.ReadOnlyField(source="User.id")
        parent_post = serializers.ReadOnlyField(source="Post.id")

        model = Comment
        fields = ["id", "parent_post", "author", "create_time", "body"]


class CommentCommentSerializer(serializers.ModelSerializer):
    class Meta:
        author = serializers.ReadOnlyField(source="User.id")
        parent_comment = serializers.ReadOnlyField(source="Comment.id")

        model = CommentComment
        fields = ["id", "author", "parent_comment", "create_time"]