from django.conf.urls import url

from popup.views.admin import AdminPopupAPIView, EditAdminPopupAPIView, ReOrderAdminPopupAPIView

urlpatterns = [
    url(r"^popup/?$", AdminPopupAPIView.as_view(), name="popup_admin_api"),
    url(r"^popup/edit?$", EditAdminPopupAPIView.as_view(), name="popup_admin_edit_api"),
    url(r"^popup/reorder?$", ReOrderAdminPopupAPIView.as_view(), name="popup_admin_reorder_api"),
]