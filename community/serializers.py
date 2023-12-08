from .models import Post, Comment, CommentComment
from utils.api import serializers


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        author = serializers.ReadOnlyField(source="User.id")
        related_problem = serializers.ReadOnlyField(source="Problem.id")

        model = Post
        fields = ["id", "category", "title", "author", "create_time", "body", "related_problem"]
