<template>
  <div class="bannerBox">
    <Carousel v-model="value1" autoplay loop arrow="never" radius-dot="true" autoplaySpeed="3000">
      <CarouselItem>
        <div class="demo-carousel">Banner 1</div>
      </CarouselItem>
      <CarouselItem>
        <div class="demo-carousel">Banner 2</div>
      </CarouselItem>
      <CarouselItem>
        <div class="demo-carousel">Banner 3</div>
      </CarouselItem>
      <CarouselItem>
        <div class="demo-carousel">Banner 4</div>
      </CarouselItem>
    </Carousel>
  </div>
</template>

<script>
import api from '@oj/api'

export default {
  name: 'HomeBannerListBox',
  components: {

  },
  data () {
    return {
      value1: 0
    }
  },
}
</script>

<style scoped lang="less">
.bannerBox {
  margin-bottom: 20px;
  .demo-carousel{
    cursor: pointer;
    border-radius: 7px;
    width: 100%;
    height: 150px;
    line-height: 150px;
    border: 1px solid #dedede;
    text-align: center;
    background-color: #ffffff;
    font-size: 20px;
  }
}
</style>
