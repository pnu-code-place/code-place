<template>
  <div class="bannerBox">
    <Carousel autoplay loop arrow="never" :radius-dot="true" :autoplaySpeed="3000">
      <CarouselItem>
        <div class="demo-carousel">
          <img src="@/assets/banner1.svg" width="100%"/>
        </div>
      </CarouselItem>
      <CarouselItem>
        <div class="demo-carousel">
          <img src="@/assets/banner2.svg" width="100%"/>
        </div>
      </CarouselItem>
    </Carousel>
  </div>
</template>

<script>
export default {
  name: 'HomeBannerListBox',
}
</script>

<style scoped lang="less">
.bannerBox {
  border-radius: 7px;
  margin-bottom: 20px;
  overflow: hidden;
  .demo-carousel {
    border-radius: 7px;
    width: 100%;
    height: 150px;
    border: 1px solid #dedede;
  }
}
</style>
