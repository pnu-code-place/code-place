<template>
  <div class="bannerBox">
    <Carousel
      autoplay
      loop
      arrow="never"
      :radius-dot="true"
      :autoplaySpeed="3000"
    >
      <CarouselItem v-for="banner in banners">
        <div class="demo-carousel">
          <img
            :src="banner.banner_image"
            width="100%"
            @click="goBannerLink(banner.link_url)"
          />
        </div>
      </CarouselItem>
    </Carousel>
  </div>
</template>

<script>
import api from "@oj/api";

export default {
  name: "HomeBannerListBox",
  data() {
    return {
      banners: [],
    };
  },
  mounted() {
    api.getBanners().then((res) => {
      this.banners = res.data.data;
    });
  },
  methods: {
    goBannerLink(link) {
      window.open(link);
    },
  },
};
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
