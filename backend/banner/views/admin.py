import os

from account.decorators import super_admin_required
from banner.models import Banner
from banner.serializers import ImageUploadForm, BannerAdminSerializer
from oj import settings
from utils.api import APIView
from utils.constants import BANNER_VISIBLE_LIMIT
from utils.contents_util import ContentUtil

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
        banner_image = request.data.get('image')

        # URL 유효성 검사
        error = ContentUtil.validateURL(link_url)
        if error:
            return self.error(error)

        error = ContentUtil.validateImage(image=banner_image)
        if error:
            return self.error(error)

        filename = ContentUtil.saveContentWithRandomFileName(banner_image, settings.BANNER_DIR)

        new_banner = Banner(
            banner_image=f"{settings.BANNER_URI_PREFIX}/{filename}", link_url=link_url, visible=False, order=None)

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
        어드민 페이지-홈 배너 관리 페이지(모달창)에서 등록된 배너를 수정합니다.
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
        error = ContentUtil.validateURL(link_url)
        if error is not None:
            return self.error(error)

        target_banner.link_url = link_url

        # 이미지 변경 사항이 있는 경우
        if form.is_valid():
            banner_image = form.cleaned_data["image"]

            error = ContentUtil.validateImage(image=banner_image)
            if error is not None:
                self.error(error)

            # 기존 이미지 삭제
            original_image = target_banner.banner_image
            if os.path.isfile(os.path.join(settings.BANNER_DIR, original_image)):
                os.remove(os.path.join(settings.BANNER_DIR, original_image))

            # 파일 이름 생성하여 저장
            filename = ContentUtil.saveContentWithRandomFileName(banner_image, settings.BANNER_DIR)

            # 신규 경로 지정
            target_banner.banner_image = f"{settings.BANNER_URI_PREFIX}/{filename}"
        else:
            self.error("Invalid file content")

        target_banner.save()
        return self.success(BannerAdminSerializer(target_banner).data)

    @super_admin_required
    def put(self, request):
        """
        어드민 페이지-홈 배너 관리 페이지에서 등록된 배너를 활성화/비활성화합니다.
        """
        banners = Banner.objects.filter(order__isnull=False)
        id = request.GET.get('id')
        visible = request.data.get('visible', None)

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

        return self.success(BannerAdminSerializer(Banner.objects.all(), many=True).data)


class ReOrderAdminBannerAPIView(APIView):
    """
    어드민 페이지-홈 배너 관리 페이지에서 등록된 배너의 순서를 조정합니다.
    """

    @staticmethod
    def find_first_difference(list1, list2):
        for i, (item1, item2) in enumerate(zip(list1, list2)):
            if item1 != item2:
                return i, item1
        return None

    @super_admin_required
    def post(self, request):
        banners = Banner.objects.all()

        banners_with_order = banners.filter(order__isnull=False)
        reorder_list = list(request.data.get('reorder_list', None))
        curr_order_list = list(banners_with_order.values_list('id', flat=True).order_by('order'))

        if sorted(reorder_list) != sorted(curr_order_list):
            return self.error("Invalid order")

        result = self.find_first_difference(curr_order_list, reorder_list)
        if result is None:
            return self.success("no difference")

        index, target_banner_id = result
        reorder_num = reorder_list.index(target_banner_id) + 1

        target_banner = Banner.objects.get(id=target_banner_id)

        try:
            Banner.reorder_swap(target_banner, reorder_num)
        except Exception as e:
            logger.exception(e)
            return self.error("reorder failed")

        return self.success("reorder succeed")
