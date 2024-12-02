from django.db import models, transaction

from utils.constants import POPUP_VISIBLE_LIMIT

class Popup(models.Model):
    popup_image = models.TextField()
    popup_image_width = models.IntegerField(null=True)
    link_url = models.TextField()
    visible = models.BooleanField(default=False)
    order = models.PositiveIntegerField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "popup"
        ordering = ("order", "-create_time")

    @classmethod
    def insert(cls, target_popup):
        popups = cls.objects.filter(order__isnull=False).order_by('order')
        if popups.count() == POPUP_VISIBLE_LIMIT:
            raise RuntimeError("You have exceeded the limit of the popup you can activate.")
        with transaction.atomic():
            for popup in popups:
                popup.order = popup.order + 1
                popup.save()
            target_popup.order = 1
            target_popup.save()


    @classmethod
    def reorder_swap(cls, curr_popup, target_loc):
        curr_loc = curr_popup.order
        if curr_loc == target_loc:
            return
        target_popup = cls.objects.get(order=target_loc)
        with transaction.atomic():
            # 타겟 팝업의 order를 현재 배너의 원래 order로 변경
            target_popup.order = curr_loc
            target_popup.save()

            # 현재 팝업의 order를 목표 위치로 변경
            curr_popup.order = target_loc
            curr_popup.save()


    @classmethod
    def remove(cls, target_popup):
        popups = cls.objects.filter(order__isnull=False).order_by('order')

        # 순서가 없는 경우나, 마지막 순서인 경우 즉시 삭제
        if target_popup.order is None:
            target_popup.delete()
        else:
            # 순서가 있는 경우, 타겟 팝업 삭제 후 visible 상태인 팝업들 순서 재조정
            with transaction.atomic():
                len_popups = len(popups)
                target_order = target_popup.order

                for i in range(target_order, len_popups):
                    popups[i].order = i
                    popups[i].save()

                target_popup.delete()