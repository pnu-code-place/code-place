<script>
// TODO : static하게 이미지를 처리하기 위해 다음과 같이 적용했습니다. 실제 프로젝트에서는 서버에 이미지를 저장하고, 해당 이미지를 불러오는 방식으로 구현해야 합니다.

export default {
  props: {
    tooltip: {
      type: String,
      required: true
    },
    image: {
      type: String,
      required: true
    },
  },
  data() {
    return {
      displayImage : this.image
    }
  },
  computed: {
    fallbackMedal() {
      return require("@/assets/challenges/on_error_image.png")
    }
  },
  methods: {
    onMedalError() {
      this.displayImage = this.fallbackMedal
    }
  }
}
</script>

<template>
  <Tooltip :content="tooltip" placement="bottom" class="tooltip">
    <img :src="displayImage" alt="badge" @error="onMedalError"/>
  </Tooltip>
</template>

<style scoped lang="less">
.tooltip {
  display: flex;
  justify-content: center;
  align-items: center;
}

img {
  width:100%;
  height:auto;
}
img:hover {
  transform: scale(1.1);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
</style>
