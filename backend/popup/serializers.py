from django import forms

from popup.models import Popup
from utils.api import serializers


class ImageUploadForm(forms.Form):
    image = forms.FileField()


class PopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Popup
        fields = ['id', 'popup_image', 'link_url']


class PopupAdminSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    popup_image = serializers.CharField(max_length=256)
    link_url = serializers.URLField()
    visible = serializers.BooleanField()
    order = serializers.IntegerField()
    create_time = serializers.DateTimeField()
    last_update_time = serializers.DateTimeField()
