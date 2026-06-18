<template>
  <pre
    v-highlight="code"
  ><code :class="language" :style="styleObject"></code></pre>
</template>

<script>
export default {
  name: "OjHighlight",
  data() {
    return {
      styleObject: {
        "border-left": "2px solid green",
      },
    }
  },
  props: {
    language: {
      type: String,
    },
    code: {
      required: true,
      type: String,
    },
    borderColor: {
      type: String,
      default: "green",
    },
  },
  watch: {
    borderColor(newVal, oldVal) {
      this.styleObject["border-left"] = "2.5px solid " + newVal
    },
  },
}
</script>

<style scoped lang="less">
pre {
  padding: 0;
  display: block;
  font-family:
    "JetBrains Mono", "Noto Sans KR", "Apple SD Gothic Neo", "Menlo", "Monaco",
    "Consolas", monospace;
  font-variant-ligatures: none;
  code {
    padding: 20px;
    font-size: 1.1em;
    font-family: inherit;
  }
}
</style>
