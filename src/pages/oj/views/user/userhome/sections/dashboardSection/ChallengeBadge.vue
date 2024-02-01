<script>
export default {
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    },
    image: {
      type: String,
      required: true
    },
    date: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      displayImage : this.image
    }
  },
  computed: {
    tooltip() {
      return `${this.title} : ${this.description}`
    },
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
    <img :src="image" alt="badge" @error="onMedalError"/>
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
