<script>
export default {
  name: 'ShineWrapper',
  props: {
    disabled: {
      type: Boolean,
      default() {
        return false
      }
    }
  }
}
</script>

<template>
  <div class="shine-wrapper">
    <slot></slot>
    <div class="overlay-wrapper" v-if="!disabled">
      <div class="overlay"></div>
    </div>
  </div>
</template>

<style scoped lang="less">
.shine-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  .overlay-wrapper {
    width: 100%;
    height: 100%;
    overflow: hidden;
    position: absolute;
    .overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 200%;
      height: 200%;
      background-image: linear-gradient(to bottom right,
      rgba(255, 255, 255, 0) 0%,
      rgba(255, 255, 255, 0.5) 50%,
      rgba(255, 255, 255, 0) 100%);
      animation: shine 3s infinite;
    }
  }
}

@keyframes shine {
  0% {
    transform: translate(-100%, -100%);
  }
  100% {
    transform: translate(100%, 100%);
  }
}
</style>
