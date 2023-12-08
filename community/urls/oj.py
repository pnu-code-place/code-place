from django.conf.urls import url

from ..views.oj import PostAPI

urlpatterns = [
    url(r"^post/?$", PostAPI.as_view(), name="post_api")
]
