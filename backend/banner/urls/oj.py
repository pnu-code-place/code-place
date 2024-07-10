from django.conf.urls import url

from banner.views.oj import BannerAPIView

urlpatterns = [
    url(r"^banner/?$", BannerAPIView.as_view(), name="banner_api"),
]