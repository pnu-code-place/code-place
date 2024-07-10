import os

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from account.decorators import super_admin_required
from banner.models import Banner
from banner.serializers import ImageUploadForm, BannerAdminSerializer
from oj import settings
from utils.api import APIView
from utils.shortcuts import rand_str

import logging
logger = logging.getLogger(__name__)


class AdminBannerAPIView(APIView):
    """
    어드민 페이지( 홈 배너 관리 )
    배너 CRUD API
    """
    @super_admin_required
    def get(self, request):
        """
        어드민 페이지 '홈 배너 관리' 페이지 접속 시
        Banner 모델 데이터를 가져옵니다.
        """
        banners = Banner.objects.all().order_by('order')
        if banners:
            return self.success(BannerAdminSerializer(banners, many=True).data)

    @super_admin_required
    def post(self, request):
        """
        어드민 페이지-홈 배너 관리 페이지에서 배너를 추가합니다.

        다음과 같은 데이터가 필요합니다.
        - 배너 이미지
        - 배너 이미지에 연결할 URL 주소
        """

        link_url = request.data.get('link_url')
        form = ImageUploadForm(request.POST, request.FILES)
        banner_image = None
        suffix = None

        # URL 유효성 검사
        url_validator = URLValidator()
        try:
            url_validator(link_url)
        except ValidationError:
            self.error("Invalid URL")

        # 이미지 폼 유효성 검사
        if form.is_valid():
            banner_image = form.cleaned_data["image"]

            # 파일 크기 검사
            if banner_image.size > 2 * 1024 * 1024:
                self.error("Picture is too large")

            # 파일 확장자 검사
            suffix = os.path.splitext(banner_image.name)[-1].lower()
            if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
                return self.error("Unsupported file format")
        else:
            self.error("Invalid file content")

        # 배너 이미지 주소를 랜덤으로 생성
        name = rand_str(10) + suffix

        # 배너 이미지 저장
        with open(os.path.join(settings.BANNER_DIR, name), "wb") as img:
            for chunk in banner_image:
                img.write(chunk)

        new_banner = Banner(
            banner_image=f"{settings.BANNER_URI_PREFIX}/{name}",
            link_url=link_url,
            visible=False,
            order=None
        )

        new_banner.save()

        return self.success(BannerAdminSerializer(new_banner).data)

    @super_admin_required
    def put(self, request):
        """
        어드민 페이지-홈 배너 관리 페이지에서 등록된 배너를 수정합니다.
        다음과 같은 데이터가 필요할 수 있습니다.
        - 신규 배너 이미지
        - 신규 URL
        """
        pass

    @super_admin_required
    def delete(self, request):
        """
        어드민 페이지-홈 배너 관리 페이지에서 등록된 배너를 삭제합니다.
        """
        # target_banner = Banner.objects.get(id=request.data.get('id'))
        #
        # if not target_banner.order:
        #     target_banner.delete()
        pass







