from django import forms

from popup.models import Popup
from utils.api import serializers


class ImageUploadForm(forms.Form):
    image = forms.FileField()


class PopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Popup
        fields = ['id', 'popup_image', 'link_url', 'popup_image_width']


class PopupAdminSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    popup_image = serializers.CharField(max_length=256)
    popup_image_width = serializers.IntegerField()
    link_url = serializers.URLField()
    visible = serializers.BooleanField()
    order = serializers.IntegerField()
    create_time = serializers.DateTimeField()
    last_update_time = serializers.DateTimeField()
