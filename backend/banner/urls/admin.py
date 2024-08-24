from django.conf.urls import url

from banner.views.admin import AdminBannerAPIView, EditAdminBannerAPIView, ReOrderAdminBannerAPIView

urlpatterns = [
    url(r"^banner/?$", AdminBannerAPIView.as_view(), name="banner_admin_api"),
    url(r"^banner/edit?$", EditAdminBannerAPIView.as_view(), name="banner_admin_edit_api"),
    url(r"^banner/reorder?$", ReOrderAdminBannerAPIView.as_view(), name="banner_admin_reorder_api"),
]
