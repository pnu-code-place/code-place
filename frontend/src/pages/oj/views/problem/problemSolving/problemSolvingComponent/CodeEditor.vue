<template>
  <div>
    <codemirror
      ref="myCm"
      :value="value"
      :key="key"
      :options="cmOptions"
      @ready="onCmReady"
      @input="onCmCodeChange"
      :style="{ 'font-size': fontSize + 'px' }"
    >
    </codemirror>
  </div>
</template>

<script>
// language js
import "codemirror/mode/javascript/javascript.js"
import { codemirror } from "vue-codemirror"

// require styles
import "codemirror/lib/codemirror.css"
import "codemirror/theme/ayu-mirage.css" //dark mode 고정
import "../../../../../../styles/github-light.css" //bright mode 고정

// mode
import "codemirror/mode/clike/clike.js"
import "codemirror/mode/python/python.js"
import "codemirror/mode/go/go.js"
import "codemirror/mode/javascript/javascript.js"

// active-line.js
import "codemirror/addon/selection/active-line.js"
import utils from "../../../../../../utils/utils"

// match-bracket
import "codemirror/addon/edit/matchbrackets.js"

// foldGutter
import "codemirror/addon/fold/foldgutter.css"
import "codemirror/addon/fold/foldgutter.js"
import "codemirror/addon/fold/brace-fold.js"
import "codemirror/addon/fold/indent-fold.js"
import "codemirror/addon/edit/closebrackets.js"
import { mapGetters } from "vuex"

export default {
  name: "CodeEditor",
  components: {
    codemirror,
  },
  props: {
    value: {
      type: String,
      default: "",
    },
    languages: {
      type: Array,
      default: () => {
        return ["C", "C++", "Java", "Python3"]
      },
    },
    language: {
      type: String,
      default: "C++",
    },
    cursorPos: {
      type: Object,
    },
    theme: {
      type: Boolean,
    },
    allowPaste: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      key: 0,
      code: "",
      fontSize: 14,
      cmOptions: {
        tabSize: 4,
        mode: "text/x-csrc",
        theme: this.isDarkMode ? "ayu-mirage" : "github-light",
        lineNumbers: true,
        line: true,
        styleActiveLine: true,
        // 인덴트 사이즈
        indentUnit: 4,
        // 여러 라인을 동시에 탭할때 인덴트 함
        extraKeys: {
          Tab: "indentMore",
        },
        foldGutter: true,
        smartIndent: true,
        autofocus: true,
        autoCloseBrackets: true,
        autoResize: true,
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
        scrollbarStyle: "native",
        matchBrackets: true,
      },
      mode: {
        "C++": "text/x-csrc",
      },
    }
  },
  methods: {
    onCmReady(cm) {
      console.log(this.theme)
    },
    onCmCodeChange(newCode) {
      this.value = newCode
      this.$emit("update:value", newCode)
      this.$emit("update:cursorPos", {
        ln: this.codemirror.doc.getCursor().line,
        ch: this.codemirror.doc.getCursor().ch,
      })
    },
    blockPasteFromExternalSource() {
      let lastInternalText = ""

      // 내부 복사 이벤트 감지
      this.codemirror.on("copy", (cm, e) => {
        lastInternalText = cm.getSelection()
      })

      // 잘라내기 이벤트 감지
      this.codemirror.on("cut", (cm, e) => {
        lastInternalText = cm.getSelection()
      })

      // 붙여넣기 이벤트 처리
      this.codemirror.on("paste", (cm, e) => {
        // 기본 붙여넣기 동작 방지
        e.preventDefault()

        if (this.allowPaste === true) {
          // 붙여넣기 허용 시 기본 동작 수행
          cm.replaceSelection(e.clipboardData.getData("text"))
          return
        }

        // 붙여넣기 금지 시 클립보드 내용 확인
        // 클립보드의 내용 가져오기
        navigator.clipboard.readText().then((clipText) => {
          // 클립보드 내용이 마지막으로 내부에서 복사 또는 잘라내기한 텍스트와 일치하는지 확인
          if (clipText === lastInternalText) {
            // 내부에서 복사 또는 잘라내기한 텍스트라면 붙여넣기 허용
            cm.replaceSelection(clipText)
          } else {
            // 외부 텍스트라면 경고 메시지 표시
            alert(
              "해당 문제에서는 외부 소스로부터의 붙여넣기가 허용되지 않습니다.",
            )
          }
        })
      })
    },
    resetCM() {
      this.value = ""
    },
    onLangChange(newVal) {
      this.codemirror.setOption("mode", this.mode[newVal])
      this.$emit("changeLang", newVal)
    },
    toggleTheme(value) {
      this.codemirror.setOption("theme", value)
    },
  },
  computed: {
    ...mapGetters(["isDarkMode"]),
    codemirror() {
      return this.$refs.myCm.codemirror
    },
  },
  mounted() {
    let customTheme = this.isDarkMode ? "ayu-mirage" : "github-light"
    this.codemirror.setOption("theme", customTheme)
    this.theme = customTheme

    this.code = this.value

    utils.getLanguages().then((languages) => {
      let mode = {}
      languages.forEach((lang) => {
        mode[lang.name] = lang.content_type
      })
      this.mode = mode
      this.codemirror.setOption("mode", this.mode[this.language])
    })

    let checkContest = this.$route.path.split("/").indexOf("contest") > 0
    if (checkContest) {
      this.blockPasteFromExternalSource()
    }
    this.$emit("update:cursorPos", {
      ln: this.codemirror.doc.getCursor().line,
      ch: this.codemirror.doc.getCursor().ch,
    })
  },
  watch: {
    isDarkMode(value) {
      let customTheme = value ? "ayu-mirage" : "github-light"
      this.toggleTheme(customTheme)
      this.theme = value
    },
    language(value) {
      this.codemirror.setOption("mode", this.mode[value])
    },
  },
}
</script>

<style>
.CodeMirror {
  height: calc(100vh - 132px) !important;
  border-radius: 7px;
  border: 1px solid var(--border-color);
}

.cm-s-ayu-mirage .CodeMirror-matchingbracket {
  text-decoration: none !important;
  color: white !important;
  background: #283a61;
}
</style>
