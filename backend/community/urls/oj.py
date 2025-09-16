from django.conf.urls import url

from ..views.oj import (CommentAPIView, CommentDetailAPIView, PostAPIView, PostDetailAPIView, PostStatusUpdateAPIView)

urlpatterns = [
    url(
        r"^community/posts/?$",
        PostAPIView.as_view(),
        name="community_posts",
    ),
    url(
        r"^community/posts/(?P<post_id>\d+)/?$",
        PostDetailAPIView.as_view(),
        name="community_post_detail",
    ),
    url(
        r"^community/posts/(?P<post_id>\d+)/status/?$",
        PostStatusUpdateAPIView.as_view(),
        name="community_post_status",
    ),
    url(
        r"^community/posts/(?P<post_id>\d+)/comments/?$",
        CommentAPIView.as_view(),
        name="community_post_comments",
    ),
    url(
        r"^community/posts/(?P<post_id>\d+)/comments/(?P<comment_id>\d+)/?$",
        CommentDetailAPIView.as_view(),
        name="community_comment_detail",
    ),
]
