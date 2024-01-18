<script>
export default {
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
    <div class="gauge" :style="{width : gaugeWidth}">

    </div>
  </div>
</template>

<style scoped lang="less">
.horizontal-gauge {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display : flex;
  justify-content : center;

  .gauge-background {
    width: 100%;
    height: 80%;
    background-color: #dedede;
    position: absolute;
    left: 0;
    top: 10%;
    border-radius: 20px;
  }
  .gauge {
    height: 100%;
    background-color: #22CC77;
    position: absolute;
    top: 0;
    left: 0;
    border-radius: 20px;
  }
}
</style>
