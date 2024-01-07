
<script setup>

</script>

<template>
  <div class="shine-wrapper">
    <slot></slot>
    <div class="overlay"></div>
  </div>
</template>

<style scoped lang="less">
.shine-wrapper {
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 100%;
  border-radius: 5px;
  transition: all 0.3s ease-out;
  cursor: pointer;

  &:hover {
    transform: scale(1.05);
  }

  .overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: linear-gradient(
      to bottom right,
      rgba(255,255,255,0) 0%,
      rgba(255,255,255,0.5) 50%,
      rgba(255,255,255,0) 100%
    );
    animation: shine 3s infinite;

  }
}

@keyframes shine {
  0% {transform:translateX(-100%);}
  100% {transform:translateX(100%);}
}
</style>
