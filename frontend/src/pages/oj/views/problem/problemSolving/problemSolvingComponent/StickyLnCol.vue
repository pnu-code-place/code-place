<template>
  <div class="sticky_ln_col">Ln {{ cursorPos.ln }}, Col {{ cursorPos.ch }}</div>
</template>

<script>
import {defineComponent} from "vue";

export default defineComponent({
  props:{
    cursorPos: Object
  }
})
</script>

<style lang="less">
.sticky_ln_col {
  position: sticky;
  float: right;
  right: 10px;
  bottom: 20px;
}
</style>
