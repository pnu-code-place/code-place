<template>
  <div class="home-family-site-banner-content">
    <div class="home-family-site-banner-image-div">
      <a :href="content.url" target="_blank">
        <div class="home-family-site-banner-image-wrapper">
          <img :src="content.src" />
        </div>
      </a>
    </div>
    <div class="home-family-site-name-wrapper">
      <span class="home-family-site-name">
        {{ content.banner_name.split(":")[0] }}
      </span>
      <br />
      <span class="home-family-site-name">{{
        content.banner_name.split(":")[1]
      }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: "FamilySiteContent",
  props: {
    content: Object,
  },
}
</script>

<style scoped lang="less">
.home-family-site-banner-content {
  padding: 15px 0;
  width: 100%;
  justify-content: center;
  .home-family-site-banner-image-div {
    margin-top: 14px;
    width: 100%;
    display: flex;
    justify-content: center;
    .home-family-site-banner-image-wrapper {
      width: 80px;
      height: 80px;
      padding: 10px;
      background-color: #ffffff;
      border-radius: 50%;
      display: flex;
      justify-content: center;
    }
  }
  .home-family-site-name-wrapper {
    margin-top: 4px;
    text-align: center;
    justify-content: center;
    .home-family-site-name {
      color: #4c515f;
      font-size: 14px;
      font-weight: bold;
    }
  }
}
</style>
