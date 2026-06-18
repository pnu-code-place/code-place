from django.urls import re_path

from popup.views.oj import PopupAPIView

urlpatterns = [
    re_path(r"^popup/?$", PopupAPIView.as_view(), name="popup_api"),
]