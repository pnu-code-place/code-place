from banner.models import Banner
from banner.serializers import BannerSerializer
from utils.api import APIView


class BannerAPIView(APIView):

    def get(self, request):
        banners = Banner.objects.filter(visible=True).order_by('order')
        return self.success(BannerSerializer(banners, many=True).data)
