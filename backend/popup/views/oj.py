from popup.models import Popup
from popup.serializers import PopupSerializer
from utils.api import APIView


class PopupAPIView(APIView):

    def get(self, request):
        popups = Popup.objects.filter(visible=True).order_by('order')
        return self.success(PopupSerializer(popups, many=True).data)
