from django.urls import re_path

from banner.views.oj import BannerAPIView

urlpatterns = [
    re_path(r"^banner/?$", BannerAPIView.as_view(), name="banner_api"),
]