from utils.api import APIView

from announcement.models import Announcement, LinkAnnouncement
from announcement.serializers import AnnouncementSerializer, LinkAnnouncementSerializer
from utils.constants import LINK_NOTICE_LIMIT


class AnnouncementAPI(APIView):
    def get(self, request):
        announcements = Announcement.objects.filter(visible=True)
        return self.success(self.paginate_data(request, announcements, AnnouncementSerializer))

class SWAnnouncementAPI(APIView):
    def get(self, request):
        link_announcements = LinkAnnouncement.objects.order_by('-la_id')[:LINK_NOTICE_LIMIT]
        serializer = LinkAnnouncementSerializer(link_announcements, many=True)
        return self.success(serializer.data)