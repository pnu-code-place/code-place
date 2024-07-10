from django.conf.urls import url

from banner.views.admin import AdminBannerAPIView

urlpatterns = [
    url(r"^banner/?$", AdminBannerAPIView.as_view(), name="banner_admin_api"),
]
