from django.conf.urls import url

from ..views.oj import PostAPI, DetailPostAPI

urlpatterns = [
    url(r"^post/?$", PostAPI.as_view(), name="post_api"),
    url(r"^detail_post/?$", DetailPostAPI.as_view(), name="detail_post_api")
]
