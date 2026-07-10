<template>
  <div class="sticky_ln_col">Ln {{ cursorPos.ln }}, Col {{ cursorPos.ch }}</div>
</template>

<script>
import { defineComponent } from "vue"

export default defineComponent({
  props: {
    cursorPos: Object,
  },
})
</script>

<style lang="less">
.sticky_ln_col {
  position: absolute;
  right: 28px;
  bottom: 14px;
  z-index: 11;
  pointer-events: none;
}
</style>
