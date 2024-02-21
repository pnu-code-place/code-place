<template>
  <div @click="onClick" class="iconBtnWrapper" :style="{'width': this.wrapperSize+ 'px', 'height': this.wrapperSize+ 'px' }">
    <i :class="this.iconClass" :style="{'width': this.iconSize + 'px', 'height': this.iconSize+ 'px'}"></i>
  </div>
</template>

<script>
export default {
  name: "CustomIconBtn",
  props:{
    wrapperSize:{
      type: Number,
      default: 35
    },
    iconSize:{
      type: Number,
    },
    iconClass:{
      type: String
    },
    iconColor:{
      type: String
    }
  },
  mounted () {

  },
  methods: {
    onClick() {
      // 컴포넌트 사용자가 클릭 이벤트를 듣도록 이벤트를 발생시킵니다.
      this.$emit('click');
    }
  },

}
</script>

<style lang="less">
.iconBtnWrapper{
  width: 35px;
  height: 35px;
  border-radius: 10px;
  cursor: pointer;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}
.iconBtnWrapper:hover{
  background-color: var(--custom-btn-hover-color);
}
</style>
