<template>
  <div>
    <codemirror ref="myCm"
                :value="value"
                :key="key"
                :options="cmOptions"
                @ready="onCmReady"
                @input="onCmCodeChange"
                :style="{'font-size': fontSize+'px'}">
    </codemirror>
  </div>
</template>

<script>
// language js
import 'codemirror/mode/javascript/javascript.js'
import { codemirror } from 'vue-codemirror'

// require styles
import 'codemirror/lib/codemirror.css'
import 'codemirror/theme/ayu-mirage.css' //dark mode 고정
import '../../../../../../styles/github-light.css'//bright mode 고정

// mode
import 'codemirror/mode/clike/clike.js'
import 'codemirror/mode/python/python.js'
import 'codemirror/mode/go/go.js'
import 'codemirror/mode/javascript/javascript.js'

// active-line.js
import 'codemirror/addon/selection/active-line.js'
import utils from "../../../../../../utils/utils";

// foldGutter
import 'codemirror/addon/fold/foldgutter.css'
import 'codemirror/addon/fold/foldgutter.js'
import 'codemirror/addon/fold/brace-fold.js'
import 'codemirror/addon/fold/indent-fold.js'
import 'codemirror/addon/edit/closebrackets.js'
import {mapGetters} from "vuex";

export default {
  name:"CodeEditor",
  components:{
    codemirror
  },
  props: {
    value: {
      type: String,
      default: ''
    },
    languages: {
      type: Array,
      default: () => {
        return ['C', 'C++', 'Java', 'Python3']
      }
    },
    language: {
      type: String,
      default: 'C++'
    },
    cursorPos:{
      type: Object
    },
    fontSize:{
      type: Number
    },
    theme:{
      type: Boolean
    }
  },
  data () {
    return {
      key: 0,
      code: "",
      cmOptions: {
        tabSize: 4,
        mode: 'text/x-csrc',
        theme: this.isDarkMode ? 'ayu-mirage' : 'github-light',
        lineNumbers: true,
        line: true,
        foldGutter: true,
        smartIndent: true,
        autofocus: true,
        autoCloseBrackets: true,
        autoResize: true,
        gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
        scrollbarStyle: 'native',
      },
      mode: {
        'C++': 'text/x-csrc'
      }
    }
  },
  methods: {
    onCmReady(cm) {
      console.log(this.theme)
    },
    onCmCodeChange(newCode) {
      this.value = newCode
      this.$emit('update:value', newCode)
      this.$emit('update:cursorPos', {
        ln: this.codemirror.doc.getCursor().line,
        ch: this.codemirror.doc.getCursor().ch
      })
    },
    blockPasteFromExternalSource(){
      this.codemirror.on("beforeChange", function(_, change) { // block paste
        if (change.origin == "paste") change.cancel()
      })
    },
    resetCM() {
      this.value = ''
    },
    onLangChange (newVal) {
      this.codemirror.setOption('mode', this.mode[newVal])
      this.$emit('changeLang', newVal)
    },
    toggleTheme(value){
        this.codemirror.setOption('theme', value)
    },
    changeFontSize(value){
      this.fontSize = value
      // this.key++
    }
  },
  computed: {
    ...mapGetters(['isDarkMode']),
    codemirror() {
      return this.$refs.myCm.codemirror
    },
  },
  mounted() {
    let customTheme = this.isDarkMode ? 'ayu-mirage' : 'github-light'
    this.codemirror.setOption('theme', customTheme)
    this.theme = customTheme

    this.code = this.value

    utils.getLanguages().then(languages => {
      let mode = {}
      languages.forEach(lang => {
        mode[lang.name] = lang.content_type
      })
      this.mode = mode
      this.codemirror.setOption('mode', this.mode[this.language])
    })


    // this.blockPasteFromExternalSource()
    this.$emit('update:cursorPos', {
      ln: this.codemirror.doc.getCursor().line,
      ch: this.codemirror.doc.getCursor().ch
    })

    console.log('this is current codemirror object', this.codemirror)
    console.log("In Codemirror",this.value)
  },
  watch:{
    isDarkMode(value){
      let customTheme = value ? 'ayu-mirage' : 'github-light'
      this.toggleTheme(customTheme)
      this.theme = value
    }
  }
}
</script>

<style>
.CodeMirror {
  height: calc(100vh - 132px) !important;
  border-radius: 7px;
  border: 1px solid var(--border-color);
}

</style>


