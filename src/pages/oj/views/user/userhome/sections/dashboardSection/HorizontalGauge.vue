<script>
export default {
  data() {
    return {
      mounted: false
    }
  },
  mounted() {
    this.mounted = true;
  },
  name : 'horizontal-gauge',
  props: ['progress'],
  computed: {
    gaugeWidth() {
      return `${this.progress * 100}%`;
    }
  }
}
</script>

<template>
  <div class="horizontal-gauge">
    <div class="gauge-background">
    </div>
    <transition name = "gauge">
    <div v-if="this.mounted" class="gauge-bar" :style="{width : gaugeWidth}">
      <div class="overlay"></div>
    </div>
    </transition>
  </div>
</template>

<style scoped lang="less">

.gauge-enter-active, .gauge-leave-active {
  transition: all 1.5s ease-out;
}

.gauge-enter, .gauge-leave-to {
  transform : translateX(-100%);
}

.horizontal-gauge {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display : flex;
  justify-content : center;

  .gauge-background {
    width: 100%;
    height: 90%;
    background-color: #dedede;
    position: absolute;
    left: 0;
    top: 5%;
    border-radius: 20px;
  }
  .gauge-bar {
    height: 100%;
    background-color: #22CC77;
    position: absolute;
    top: 0;
    left: 0;
    border-radius: 20px;

    overflow: hidden;

    .overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 300%;
      height: 100%;
      background-image: linear-gradient(to right,
      rgba(255, 255, 255, 0) 0%,
      rgba(255, 255, 255, 0.6) 10%,
      rgba(255, 255, 255, 0) 20%,
      rgba(255, 255, 255, 0.6) 30%,
      rgba(255, 255, 255, 0) 40%,
      rgba(255, 255, 255, 0.6) 50%,
      rgba(255, 255, 255, 0) 60%,
      rgba(255, 255, 255, 0.6) 70%,
      rgba(255, 255, 255, 0) 80%,
      rgba(255, 255, 255, 0.6) 90%,
      rgba(255, 255, 255, 0) 100%);
      animation: shine 7s linear infinite;
    }
  }
  @keyframes shine {
    0% {
      transform: translate(-60%, 0%);
    }
    100% {
      transform: translate(0%, 0%);
    }
  }
}
</style>
