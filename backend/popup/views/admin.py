import os

from account.decorators import super_admin_required
from popup.models import Popup
from popup.serializers import ImageUploadForm, PopupAdminSerializer
from oj import settings
from utils.api import APIView
from utils.constants import POPUP_VISIBLE_LIMIT
from utils.contents_util import ContentUtil

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
        - 팝업 이미지 넓이
        """

        link_url = request.data.get('link_url')
        popup_image = request.data.get('image')
        image_width = int(request.data.get('image_width'))

        # URL 유효성 검사
        error = ContentUtil.validateURL(link_url)
        if error is not None:
            return self.error(error)

        # 이미지 유효성 검사
        error = ContentUtil.validateImage(image=popup_image, width=image_width)
        if error is not None:
            return self.error(error)

        filename = ContentUtil.saveContentWithRandomFileName(popup_image, settings.POPUP_DIR)

        new_popup = Popup(popup_image=f"{settings.POPUP_URI_PREFIX}/{filename}",
                          link_url=link_url,
                          popup_image_width=image_width,
                          visible=False,
                          order=None)

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
        - 팝업 이미지, 연결 링크, 이미지 넓이 수정
        """
        link_url = request.data.get('link_url', None)
        image_width = int(request.data.get('image_width', None))
        form = ImageUploadForm(request.POST, request.FILES)

        # 수정 타겟
        try:
            target_popup = Popup.objects.get(id=request.GET.get('id'))
        except Popup.DoesNotExist:
            return self.error("Invalid Popup")

        # 연결 링크 변경
        error = ContentUtil.validateURL(link_url)
        if error is not None:
            return self.error(error)

        target_popup.link_url = link_url

        # 이미지 변경 사항이 있는 경우
        if form.is_valid():

            popup_image = form.cleaned_data["image"]

            error = ContentUtil.validateImage(image=popup_image, width=image_width)
            if error is not None:
                self.error(error)

            # 기존 이미지 삭제
            original_image = target_popup.popup_image
            file_path = os.path.join(settings.POPUP_DIR, original_image)
            if os.path.isfile(file_path):
                os.remove(file_path)

            # 파일을 랜덤 이름을 생성하여 저장
            filename = ContentUtil.saveContentWithRandomFileName(popup_image, settings.POPUP_DIR)

            # 신규 경로 및 이미지 넓이 지정
            target_popup.popup_image = f"{settings.POPUP_URI_PREFIX}/{filename}"
            target_popup.popup_image_width = image_width
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
