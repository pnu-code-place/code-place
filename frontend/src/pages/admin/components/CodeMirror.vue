<template>
  <codemirror
    v-model="currentValue"
    :options="options"
    ref="editor"
  ></codemirror>
</template>
<script>
// import { codemirror } from 'vue-codemirror-lite'
import { codemirror } from "vue-codemirror"
import "codemirror/lib/codemirror.css"
import "codemirror/mode/clike/clike.js"
import "codemirror/mode/python/python.js"
export default {
  name: "CodeMirror",
  data() {
    return {
      currentValue: "",
      options: {
        mode: "text/x-csrc",
        lineNumbers: true,
        lineWrapping: false,
        theme: "default",
        tabSize: 4,
        line: true,
        foldGutter: true,
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
        autofocus: false,
      },
    }
  },
  components: {
    codemirror,
  },
  props: {
    value: {
      type: String,
      default: "",
    },
    mode: {
      type: String,
      default: "text/x-csrc",
    },
  },
  mounted() {
    this.currentValue = this.value
    this.$refs.editor.editor.setOption("mode", this.mode)
  },
  watch: {
    value(val) {
      if (this.currentValue !== val) {
        this.currentValue = val
      }
    },
    currentValue(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.$emit("change", newVal)
        this.$emit("input", newVal)
      }
    },
    mode(newVal) {
      this.$refs.editor.editor.setOption("mode", newVal)
    },
  },
}
</script>

<style>
.CodeMirror {
  height: auto !important;
  font-family: "Courier New", Courier, monospace !important;
  font-size: 14px;
  line-height: 1.6;
  background-color: #f8fafc !important;
  color: #334155 !important;
}

.CodeMirror-scroll {
  height: 300px;
  overflow-y: auto !important;
}

.CodeMirror-lines {
  padding: 8px 0 !important;
}

.CodeMirror-gutters {
  background-color: #f8fafc !important;
  border-right: 1px solid #e2e8f0 !important;
  padding-right: 5px;
}

.CodeMirror-linenumber {
  color: #94a3b8 !important;
}

.CodeMirror-activeline-background {
  background: #f1f5f9 !important;
}

.CodeMirror-selected {
  background: #cbd5e1 !important;
}
</style>
