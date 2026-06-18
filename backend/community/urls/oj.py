from django.urls import re_path

from ..views.oj import (CommentAPIView, CommentDetailAPIView, PostAPIView, PostDetailAPIView)

urlpatterns = [
    re_path(
        r"^community/posts/?$",
        PostAPIView.as_view(),
        name="community_posts",
    ),
    re_path(
        r"^community/posts/(?P<post_id>\d+)/?$",
        PostDetailAPIView.as_view(),
        name="community_post_detail",
    ),
    re_path(
        r"^community/posts/(?P<post_id>\d+)/comments/?$",
        CommentAPIView.as_view(),
        name="community_post_comments",
    ),
    re_path(
        r"^community/posts/(?P<post_id>\d+)/comments/(?P<comment_id>\d+)/?$",
        CommentDetailAPIView.as_view(),
        name="community_comment_detail",
    ),
]
