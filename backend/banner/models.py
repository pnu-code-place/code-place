from django.db import models, transaction

from utils.constants import BANNER_VISIBLE_LIMIT


class Banner(models.Model):
    banner_image = models.TextField()
    link_url = models.URLField()
    visible = models.BooleanField(default=False)
    order = models.PositiveIntegerField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "banner"
        ordering = ("order", "-create_time")

    @classmethod
    def insert(cls, target_banner):
        banners = cls.objects.filter(order__isnull=False).order_by('order')
        if banners.count() == BANNER_VISIBLE_LIMIT:
            raise RuntimeError("You have exceeded the limit of the banner you can activate.")
        with transaction.atomic():
            for banner in banners:
                banner.order = banner.order + 1
                banner.save()
            target_banner.order = 1
            target_banner.save()

    @classmethod
    def reorder_swap(cls, curr_banner, target_loc):
        curr_loc = curr_banner.order
        if curr_loc == target_loc:
            return
        target_banner = cls.objects.get(order=target_loc)
        with transaction.atomic():
            # 타겟 배너의 order를 현재 배너의 원래 order로 변경
            target_banner.order = curr_loc
            target_banner.save()

            # 현재 배너의 order를 목표 위치로 변경
            curr_banner.order = target_loc
            curr_banner.save()



    @classmethod
    def remove(cls, target_banner):
        banners = cls.objects.filter(order__isnull=False).order_by('order')

        # 순서가 없는 경우나, 마지막 순서인 경우 즉시 삭제
        if target_banner.order is None:
            target_banner.delete()
        else:
            # 순서가 있는 경우, 타겟 배너 삭제 후 visible 상태인 배너들 순서 재조정
            with transaction.atomic():
                len_banners = len(banners)
                target_order = target_banner.order

                for i in range(target_order, len_banners):
                    banners[i].order = i
                    banners[i].save()

                target_banner.delete()


