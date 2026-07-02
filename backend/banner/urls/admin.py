from django.urls import re_path

from banner.views.admin import AdminBannerAPIView, EditAdminBannerAPIView, ReOrderAdminBannerAPIView

urlpatterns = [
    re_path(r"^banner/?$", AdminBannerAPIView.as_view(), name="banner_admin_api"),
    re_path(r"^banner/edit?$", EditAdminBannerAPIView.as_view(), name="banner_admin_edit_api"),
    re_path(r"^banner/reorder?$", ReOrderAdminBannerAPIView.as_view(), name="banner_admin_reorder_api"),
]
