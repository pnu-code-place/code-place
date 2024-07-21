from django.conf.urls import url

from profile.views.oj import ProfileProblemAPIView

urlpatterns = [
    url(r"^profile/problem/?$", ProfileProblemAPIView.as_view(), name="profile_problem_api"),
]