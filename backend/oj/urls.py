from django.conf.urls import include, url

urlpatterns = [
    url(r"^api/", include("account.urls.oj")),
    url(r"^api/admin/", include("account.urls.admin")),
    url(r"^api/", include("announcement.urls.oj")),
    url(r"^api/admin/", include("announcement.urls.admin")),
    url(r"^api/", include("conf.urls.oj")),
    url(r"^api/admin/", include("conf.urls.admin")),
    url(r"^api/", include("problem.urls.oj")),
    url(r"^api/admin/", include("problem.urls.admin")),
    url(r"^api/", include("contest.urls.oj")),
    url(r"^api/admin/", include("contest.urls.admin")),
    url(r"^api/", include("submission.urls.oj")),
    url(r"^api/admin/", include("submission.urls.admin")),
    url(r"^api/admin/", include("utils.urls")),
    url(r"^api/", include("banner.urls.oj")),
    url(r"^api/admin/", include("banner.urls.admin")),
    url(r"^api/", include("popup.urls.oj")),
    url(r"^api/admin/", include("popup.urls.admin")),
    url(r"^api/", include("profile.urls.oj")),
    url(r"^api/", include("ranking.urls.oj")),
    url(r"^api/", include("school.urls.oj")),
    url(r"^api/", include("contents.urls.oj")),
]
