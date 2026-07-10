from django.urls import include, re_path

from utils.observability_metrics import register_codeplace_metrics

register_codeplace_metrics()

urlpatterns = [
    re_path(r"^", include("django_prometheus.urls")),
    re_path(r"^api/", include("account.urls.oj")),
    re_path(r"^api/admin/", include("account.urls.admin")),
    re_path(r"^api/", include("announcement.urls.oj")),
    re_path(r"^api/admin/", include("announcement.urls.admin")),
    re_path(r"^api/", include("community.urls.oj")),
    re_path(r"^api/", include("conf.urls.oj")),
    re_path(r"^api/admin/", include("conf.urls.admin")),
    re_path(r"^api/", include("problem.urls.oj")),
    re_path(r"^api/admin/", include("problem.urls.admin")),
    re_path(r"^api/", include("contest.urls.oj")),
    re_path(r"^api/admin/", include("contest.urls.admin")),
    re_path(r"^api/", include("submission.urls.oj")),
    re_path(r"^api/admin/", include("submission.urls.admin")),
    re_path(r"^api/admin/", include("utils.urls")),
    re_path(r"^api/", include("banner.urls.oj")),
    re_path(r"^api/admin/", include("banner.urls.admin")),
    re_path(r"^api/", include("popup.urls.oj")),
    re_path(r"^api/admin/", include("popup.urls.admin")),
    re_path(r"^api/", include("profile.urls.oj")),
    re_path(r"^api/", include("ranking.urls.oj")),
    re_path(r"^api/", include("school.urls.oj")),
    re_path(r"^api/", include("contents.urls.oj")),
]
