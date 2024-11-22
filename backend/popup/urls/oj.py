from django.conf.urls import url

from popup.views.oj import PopupAPIView

urlpatterns = [
    url(r"^popup/?$", PopupAPIView.as_view(), name="popup_api"),
]