from utils.api import APIView

from announcement.models import Announcement
from announcement.serializers import AnnouncementSerializer


class AnnouncementAPI(APIView):

    def get(self, request):
        id = request.GET.get("id", None)
        announcements = Announcement.objects.filter(visible=True)
        if id is not None:
            announcements = announcements.filter(id=id)
        else:
            category = request.GET.get("category")
            if category == "release":
                announcements = announcements.filter(is_release_note=True)
            elif category == "general":
                announcements = announcements.filter(is_release_note=False)
        return self.success(self.paginate_data(request, announcements, AnnouncementSerializer))
