<script>
export default {
  data() {
    return {}
  },
}
</script>

<template>
  <div class="skeleton"></div>
</template>

<style scoped lang="less">
.skeleton {
  width: 100%;
  height: 100%;
  background-color: #f2f2f2;
  border-radius: 4px;
  animation: loading 1s infinite;
  @keyframes loading {
    0% {
      opacity: 0.5;
    }
    50% {
      opacity: 1;
    }
    100% {
      opacity: 0.5;
    }
  }
}
</style>
