from django import forms

from banner.models import Banner
from utils.api import serializers


class ImageUploadForm(forms.Form):
    image = forms.FileField()


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = ['banner_image', 'link_url']


class BannerAdminSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    banner_image = serializers.CharField(max_length=256)
    link_url = serializers.URLField()
    visible = serializers.BooleanField()
    order = serializers.IntegerField()
    create_time = serializers.DateTimeField()
    last_update_time = serializers.DateTimeField()
