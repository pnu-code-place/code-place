from utils.api import APIView

from announcement.models import Announcement
from announcement.serializers import AnnouncementSerializer


class AnnouncementAPI(APIView):

    def get(self, request):
        id = request.GET.get('id', None)
        announcements = Announcement.objects.filter(visible=True)
        if id is not None:
            announcements = announcements.filter(id=id)
        return self.success(self.paginate_data(request, announcements, AnnouncementSerializer))
