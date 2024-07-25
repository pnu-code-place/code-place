import os

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction

from account.decorators import super_admin_required
from banner.models import Banner
from banner.serializers import ImageUploadForm, BannerAdminSerializer
from oj import settings
from utils.api import APIView
from utils.constants import BANNER_VISIBLE_LIMIT
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

        # URL 유효성 검사
        url_validator = URLValidator()
        try:
            url_validator(link_url)
        except ValidationError:
            return self.error("Invalid URL")

        # 이미지 폼 유효성 검사
        if form.is_valid():
            banner_image = form.cleaned_data["image"]

            # 파일 크기 검사
            if banner_image.size > 2 * 1024 * 1024:
                return self.error("Picture is too large")

            # 파일 확장자 검사
            suffix = os.path.splitext(banner_image.name)[-1].lower()
            if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
                return self.error("Unsupported file format")

        else:
            return self.error("Invalid file content")

        # 배너 이미지 주소를 랜덤으로 생성
        name = rand_str(10) + suffix

        # 배너 이미지 저장
        banner_path = os.path.join(settings.BANNER_DIR, name)
        os.makedirs(os.path.dirname(banner_path), exist_ok=True)

        with open(banner_path, "wb") as img:
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
    def delete(self, request):
        """
        어드민 페이지-홈 배너 관리 페이지에서 등록된 배너를 삭제합니다.
        """
        try:
            target_banner = Banner.objects.get(id=request.data.get('id'))
        except Banner.DoesNotExist:
            return self.error("Invalid Banner")
        Banner.remove(target_banner)
        return self.success("delete success")


class EditAdminBannerAPIView(APIView):

    @super_admin_required
    def post(self, request):
        """
        어드민 페이지-홈 배너 관리 페이지에서 등록된 배너를 수정합니다.
        다음과 같은 수정 기능을 포함합니다.
        - 배너 이미지, 연결 링크 수정
        """
        link_url = request.data.get('link_url', None)
        form = ImageUploadForm(request.POST, request.FILES)

        # 수정 타겟
        try:
            target_banner = Banner.objects.get(id=request.GET.get('id'))
        except Banner.DoesNotExist:
            return self.error("Invalid Banner")

        # 연결 링크 변경
        if link_url is not None:
            url_validator = URLValidator()
            # URL 유효성 검사
            try:
                url_validator(link_url)
            except ValidationError:
                return self.error("Invalid URL")
            target_banner.link_url = link_url

        # 이미지 변경 사항이 있는 경우
        if form.is_valid():
            banner_image = form.cleaned_data["image"]
            # 파일 크기 검사
            if banner_image.size > 2 * 1024 * 1024:
                return self.error("Picture is too large")

            # 파일 확장자 검사
            suffix = os.path.splitext(banner_image.name)[-1].lower()
            if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
                return self.error("Unsupported file format")

            # 기존 이미지 삭제
            original_image = target_banner.banner_image
            if os.path.isfile(os.path.join(settings.BANNER_DIR, original_image)):
                os.remove(os.path.join(settings.BANNER_DIR, original_image))

            # 배너 이미지 주소를 랜덤으로 생성
            name = rand_str(10) + suffix

            # 배너 이미지 저장
            with open(os.path.join(settings.BANNER_DIR, name), "wb") as img:
                for chunk in banner_image:
                    img.write(chunk)

            # 신규 경로 지정
            target_banner.banner_image = f"{settings.BANNER_URI_PREFIX}/{name}"
        else:
            self.error("Invalid file content")

        target_banner.save()
        return self.success(BannerAdminSerializer(target_banner).data)

    @super_admin_required
    def put(self, request):
        """
        어드민 페이지-홈 배너 관리 페이지에서 등록된 배너를 수정합니다.
        다음과 같은 수정 기능을 포함합니다.
        - 배너 활성화/비활성화
        - 배너 순서 조정
        """
        banners = Banner.objects.filter(order__isnull=False)
        id = request.GET.get('id')
        visible = request.data.get('visible', None)
        reorder = request.data.get('reorder', None)
        # 수정 타겟
        try:
            target_banner = Banner.objects.get(id=id)
        except Banner.DoesNotExist:
            return self.error("Invalid Banner")

        # 활성화/비활성화
        if visible is not None:
            # BANNER_VISIBLE_LIMIT 한계 수치를 넘어서 visible로 등록하면 오류 발생
            if visible and len(banners) == BANNER_VISIBLE_LIMIT:
                return self.error("You have exceeded the limit of the banner you can activate.")
            if target_banner.visible == visible:
                return self.error("Visible state is same")

            try:
                if visible:
                    Banner.insert(target_banner)
                else:
                    Banner.reorder_swap(target_banner, banners.count())
                    target_banner.order = None
                target_banner.visible = visible
                target_banner.save()
            except Exception as e:
                logger.exception(e)
                return self.error("something went wrong")

        if reorder is not None:
            try:
                Banner.reorder_swap(target_banner, reorder)
            except Exception as e:
                logger.exception(e)
                return self.error(e)

        return self.success(BannerAdminSerializer(target_banner).data)
