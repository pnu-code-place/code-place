from django.urls import re_path

from .views import SimditorImageUploadAPIView, SimditorFileUploadAPIView

urlpatterns = [
    re_path(r"^upload_image/?$", SimditorImageUploadAPIView.as_view(), name="upload_image"),
    re_path(r"^upload_file/?$", SimditorFileUploadAPIView.as_view(), name="upload_file")
]
