<template>
  <div class="tooltip" data-container="body" data-toggle="tooltip">
    <slot></slot>
    <div class="tooltip-popper">
      <div class="tooltip-content">{{ content }}</div>
      <div class="tooltip-arrow"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: "custom-tooltip",
  props: {
    content: HTMLElement,
  },
};
</script>

<style scoped lang="less">
.tooltip {
  position: relative;
  &:hover .tooltip-popper {
    display: block;
  }
  .tooltip-popper {
    display: none;
    position: absolute;
    will-change: top, left;
    top: -40px;
    left: -30px;
    font-size: 12px;
    line-height: 1.5;
    font-weight: 700;
    visibility: visible;
    z-index: 1060;
    .tooltip-arrow {
      position: absolute;
      border-color: transparent;
      border-style: solid;
      left: 50%;
      border-width: 0 5px 5px;
      border-bottom-color: rgba(70, 76, 91, 0.9);
      transform: rotate(180deg) translate(50%, 0);
    }
    .tooltip-content {
      padding: 8px 12px;
      color: #fff;
      text-align: left;
      text-decoration: none;
      background-color: rgba(70, 76, 91, 0.9);
      border-radius: 4px;
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.2);
      white-space: nowrap;
    }
  }
}
</style>
