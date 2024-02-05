<template>
  <div>
    <codemirror ref="myCm"
                :value="code"
                :options="cmOptions"
                @ready="onCmReady"
                @focus="onCmFocus"
                @input="onCmCodeChange">
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
import '../../../styles/neat.css' //bright mode 고정

// mode
import 'codemirror/mode/clike/clike.js'
import 'codemirror/mode/python/python.js'
import 'codemirror/mode/go/go.js'
import 'codemirror/mode/javascript/javascript.js'

// active-line.js
import 'codemirror/addon/selection/active-line.js'
import utils from "../../../utils/utils";

// foldGutter
import 'codemirror/addon/fold/foldgutter.css'
import 'codemirror/addon/fold/foldgutter.js'
import 'codemirror/addon/fold/brace-fold.js'
import 'codemirror/addon/fold/indent-fold.js'
import 'codemirror/addon/edit/closebrackets.js'

export default {
  name:"CodeMirrorTest",
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
        return ['C', 'C++', 'Java', 'Python2']
      }
    },
    language: {
      type: String,
      default: 'C++'
    },
    cursorPos:{
      type: Object
    }
  },
  data () {
    return {
      code: '//Put your code here!',
      cmOptions: {
        tabSize: 4,
        mode: 'text/x-csrc',
        theme: 'neat',
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
      console.log('the editor is readied!', cm)
    },
    onCmFocus(cm) {
      // console.log('the editor is focus!', cm)
    },
    onCmCodeChange(newCode) {
      this.code = newCode
      this.$emit('update:value', newCode)
      let cursorPos = {
        ln: this.codemirror.doc.getCursor().line,
        ch: this.codemirror.doc.getCursor().ch
      }
      this.$emit('update:cursorPos', cursorPos)
    },
    blockPasteFromExternalSource(){
      this.codemirror.on("beforeChange", function(_, change) { // block paste
        if (change.origin == "paste") change.cancel()
      })
    },
    resetCM() {
      this.code = ''
    },
    onLangChange (newVal) {
      this.codemirror.setOption('mode', this.mode[newVal])
      this.$emit('changeLang', newVal)
    },
  },
  computed: {
    codemirror() {
      return this.$refs.myCm.codemirror
    }
  },
  mounted() {
    console.log('this is current codemirror object', this.codemirror)
    utils.getLanguages().then(languages => {
      let mode = {}
      languages.forEach(lang => {
        mode[lang.name] = lang.content_type
      })
      this.mode = mode
      this.editor.setOption('mode', this.mode[this.language])
    })
    this.codemirror.focus()
    this.blockPasteFromExternalSource()
    let cursorPos = {
      ln: this.codemirror.doc.getCursor().line,
      ch: this.codemirror.doc.getCursor().ch
    }
    this.$emit('update:cursorPos', cursorPos)
  }
}
</script>

<style>
.CodeMirror {
  height: 60vh !important;
  //overflow: auto !important;
  //border-top-left-radius: 7px;
  //border-top-right-radius: 7px;
  border-radius: 7px;
  border: 1px solid #e7e7e7;

  //border-top: 1px solid #e7e7e7;
  //border-right: 1px solid #e7e7e7;
  //border-left: 1px solid #e7e7e7;
  font-size: 15px;
}
.CodeMirror-Scroll {
  //min-height: 60vh;
}

</style>


