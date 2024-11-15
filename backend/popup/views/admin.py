import os

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from account.decorators import super_admin_required
from popup.models import Popup
from popup.serializers import ImageUploadForm, PopupAdminSerializer
from oj import settings
from utils.api import APIView
from utils.constants import POPUP_VISIBLE_LIMIT
from utils.shortcuts import rand_str

import logging

logger = logging.getLogger(__name__)


class AdminPopupAPIView(APIView):
    """
    어드민 페이지( 홈 팝업 관리 )
    팝업 CRUD API
    """

    @super_admin_required
    def get(self, request):
        """
        어드민 페이지 '홈 팝업 관리' 페이지 접속 시
        Popup 모델 데이터를 조회합니다.
        """
        popups = Popup.objects.all().order_by('order')
        return self.success(PopupAdminSerializer(popups, many=True).data)

    @super_admin_required
    def post(self, request):
        """
        어드민 페이지-홈 팝업 관리 페이지에서 팝업를 추가합니다.

        다음과 같은 데이터가 필요합니다.
        - 팝업 이미지
        - 팝업 이미지에 연결할 URL 주소
        """

        link_url = request.data.get('link_url')
        popup_image = request.data.get('image')

        # URL 유효성 검사
        url_validator = URLValidator()
        try:
            url_validator(link_url)
        except ValidationError:
            return self.error("Invalid URL")

        if popup_image.size > 2 * 1024 * 1024:
            return self.error("Picture is too large")

        popup_image_suffix = os.path.splitext(popup_image.name)[-1].lower()
        if popup_image_suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return self.error("Unsupported file format")

        # 팝업 이미지 주소를 랜덤으로 생성
        name = rand_str(10) + popup_image_suffix

        # 팝업 이미지 저장
        popup_path = os.path.join(settings.BANNER_DIR, name)
        os.makedirs(os.path.dirname(popup_path), exist_ok=True)

        with open(popup_path, "wb") as img:
            for chunk in popup_image:
                img.write(chunk)

        new_popup = Popup(
            popup_image=f"{settings.BANNER_URI_PREFIX}/{name}",
            link_url=link_url,
            visible=False,
            order=None
        )

        new_popup.save()

        return self.success(PopupAdminSerializer(new_popup).data)

    @super_admin_required
    def delete(self, request):
        """
        어드민 페이지-홈 팝업 관리 페이지에서 등록된 팝업를 삭제합니다.
        """
        try:
            target_popup = Popup.objects.get(id=request.data.get('id'))
        except Popup.DoesNotExist:
            return self.error("Invalid Popup")
        Popup.remove(target_popup)
        return self.success("delete success")


class EditAdminPopupAPIView(APIView):

    @super_admin_required
    def post(self, request):
        """
        어드민 페이지-홈 팝업 관리 페이지(모달창)에서 등록된 팝업를 수정합니다.
        다음과 같은 수정 기능을 포함합니다.
        - 팝업 이미지, 연결 링크 수정
        """
        link_url = request.data.get('link_url', None)
        form = ImageUploadForm(request.POST, request.FILES)

        # 수정 타겟
        try:
            target_popup = Popup.objects.get(id=request.GET.get('id'))
        except Popup.DoesNotExist:
            return self.error("Invalid Popup")

        # 연결 링크 변경
        if link_url is not None:
            url_validator = URLValidator()
            # URL 유효성 검사
            try:
                url_validator(link_url)
            except ValidationError:
                return self.error("Invalid URL")
            target_popup.link_url = link_url

        # 이미지 변경 사항이 있는 경우
        if form.is_valid():
            popup_image = form.cleaned_data["image"]
            # 파일 크기 검사
            if popup_image.size > 2 * 1024 * 1024:
                return self.error("Picture is too large")

            # 파일 확장자 검사
            suffix = os.path.splitext(popup_image.name)[-1].lower()
            if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
                return self.error("Unsupported file format")

            # 기존 이미지 삭제
            original_image = target_popup.popup_image
            if os.path.isfile(os.path.join(settings.BANNER_DIR, original_image)):
                os.remove(os.path.join(settings.BANNER_DIR, original_image))

            # 팝업 이미지 주소를 랜덤으로 생성
            name = rand_str(10) + suffix

            # 팝업 이미지 저장
            with open(os.path.join(settings.BANNER_DIR, name), "wb") as img:
                for chunk in popup_image:
                    img.write(chunk)

            # 신규 경로 지정
            target_popup.popup_image = f"{settings.POPUP_URI_PREFIX}/{name}"
        else:
            self.error("Invalid file content")

        target_popup.save()
        return self.success(PopupAdminSerializer(target_popup).data)

    @super_admin_required
    def put(self, request):
        """
        어드민 페이지-홈 팝업 관리 페이지에서 등록된 팝업를 활성화/비활성화합니다.
        """
        popups = Popup.objects.filter(order__isnull=False)
        id = request.GET.get('id')
        visible = request.data.get('visible', None)

        # 수정 타겟
        try:
            target_popup = Popup.objects.get(id=id)
        except Popup.DoesNotExist:
            return self.error("Invalid Popup")

        # 활성화/비활성화
        if visible is not None:
            # POPUP_VISIBLE_LIMIT 한계 수치를 넘어서 visible로 등록하면 오류 발생
            if visible and len(popups) == POPUP_VISIBLE_LIMIT:
                return self.error("You have exceeded the limit of the popup you can activate.")
            if target_popup.visible == visible:
                return self.error("Visible state is same")

            try:
                if visible:
                    Popup.insert(target_popup)
                else:
                    Popup.reorder_swap(target_popup, popups.count())
                    target_popup.order = None
                target_popup.visible = visible
                target_popup.save()
            except Exception as e:
                logger.exception(e)
                return self.error("something went wrong")

        return self.success(PopupAdminSerializer(Popup.objects.all(), many=True).data)


class ReOrderAdminPopupAPIView(APIView):
    """
    어드민 페이지-홈 팝업 관리 페이지에서 등록된 팝업의 순서를 조정합니다.
    """

    @staticmethod
    def find_first_difference(list1, list2):
        for i, (item1, item2) in enumerate(zip(list1, list2)):
            if item1 != item2:
                return i, item1
        return None

    @super_admin_required
    def post(self, request):
        popups = Popup.objects.all()

        popups_with_order = popups.filter(order__isnull=False)
        reorder_list = list(request.data.get('reorder_list', None))
        curr_order_list = list(popups_with_order.values_list('id', flat=True).order_by('order'))

        if sorted(reorder_list) != sorted(curr_order_list):
            return self.error("Invalid order")

        result = self.find_first_difference(curr_order_list, reorder_list)
        if result is None:
            return self.success("no difference")

        index, target_popup_id = result
        reorder_num = reorder_list.index(target_popup_id) + 1

        target_popup = Popup.objects.get(id=target_popup_id)

        try:
            Popup.reorder_swap(target_popup, reorder_num)
        except Exception as e:
            logger.exception(e)
            return self.error("reorder failed")

        return self.success("reorder succeed")
