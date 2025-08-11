<template>
  <div :class="['tooltip', `tooltip-${placement}`]">
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
    placement: {
      type: String,
      default: "top",
      validator: function (value) {
        return ["left", "right", "top", "bottom"].includes(value)
      },
    },
  },
}
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
    font-size: 12px;
    line-height: 1.5;
    font-weight: 700;
    visibility: visible;
    z-index: 1060;
    .tooltip-arrow {
      position: absolute;
      border-color: transparent;
      border-style: solid;
    }
    .tooltip-content {
      padding: 8px 12px;
      color: #fff;
      text-align: left;
      text-decoration: none;
      background-color: rgba(70, 76, 91, 0.9);
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.2);
      border-radius: 4px;
      white-space: nowrap;
    }
  }
}

.tooltip-left .tooltip-popper {
  top: 50%;
  left: -10px;
  transform: translate(-100%, -50%);
  .tooltip-arrow {
    top: 50%;
    left: 100%;
    transform: translate(0, -50%);
    border-width: 5px 0px 5px 5px;
    border-left-color: rgba(70, 76, 91, 0.9);
  }
}
.tooltip-right .tooltip-popper {
  top: 50%;
  left: calc(100% + 10px);
  transform: translate(0, -50%);
  .tooltip-arrow {
    top: 50%;
    transform: translate(-100%, -50%);
    border-width: 5px 5px 5px 0;
    border-right-color: rgba(70, 76, 91, 0.9);
  }
}
.tooltip-top .tooltip-popper {
  top: -45px;
  left: 50%;
  transform: translate(-50%, 0);
  .tooltip-arrow {
    left: 50%;
    transform: translate(-50%, 0);
    border-width: 5px 5px 0;
    border-top-color: rgba(70, 76, 91, 0.9);
  }
}
.tooltip-bottom .tooltip-popper {
  top: calc(100% + 6px);
  left: 50%;
  transform: translate(-50%, 0);
  .tooltip-arrow {
    left: 50%;
    top: 0;
    transform: translate(-50%, -100%);
    border-width: 0 5px 5px;
    border-bottom-color: rgba(70, 76, 91, 0.9);
  }
}
</style>
