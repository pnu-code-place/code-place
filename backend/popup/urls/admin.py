from django.urls import re_path

from popup.views.admin import AdminPopupAPIView, EditAdminPopupAPIView, ReOrderAdminPopupAPIView

urlpatterns = [
    re_path(r"^popup/?$", AdminPopupAPIView.as_view(), name="popup_admin_api"),
    re_path(r"^popup/edit?$", EditAdminPopupAPIView.as_view(), name="popup_admin_edit_api"),
    re_path(r"^popup/reorder?$", ReOrderAdminPopupAPIView.as_view(), name="popup_admin_reorder_api"),
]