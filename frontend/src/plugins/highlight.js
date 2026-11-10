const hljs = require("highlight.js/lib/core")
const c = require("highlight.js/lib/languages/c")
const cpp = require("highlight.js/lib/languages/cpp")
const go = require("highlight.js/lib/languages/go")
const java = require("highlight.js/lib/languages/java")
const javascript = require("highlight.js/lib/languages/javascript")
const python = require("highlight.js/lib/languages/python")
import "highlight.js/styles/atom-one-light.css"

hljs.registerLanguage("c", c)
hljs.registerLanguage("cpp", cpp)
hljs.registerLanguage("go", go)
hljs.registerLanguage("java", java)
hljs.registerLanguage("javascript", javascript)
hljs.registerLanguage("python", python)

const languagePattern = /\blang(?:uage)?-(\S+)/

function highlightCodeBlocks(el) {
  Array.from(el.querySelectorAll("pre > code")).forEach((target) => {
    const match = target.className.match(languagePattern)
    if (match && hljs.getLanguage(match[1])) {
      target.innerHTML = hljs.highlight(target.textContent, {
        language: match[1],
        ignoreIllegals: true,
      }).value
      target.classList.add("hljs")
    }
  })
}

export default {
  install(Vue, options) {
    Vue.directive("highlight", {
      deep: true,
      bind: function (el, binding) {
        // on first bind, highlight all targets
        Array.from(el.querySelectorAll("code")).forEach((target) => {
          // if a value is directly assigned to the directive, use this
          // instead of the element content.
          if (binding.value) {
            target.textContent = binding.value
          }
          hljs.highlightBlock(target)
        })
      },
      componentUpdated: function (el, binding) {
        // after an update, re-fill the content and then highlight
        Array.from(el.querySelectorAll("code")).forEach((target) => {
          if (binding.value) {
            target.textContent = binding.value
          }
          hljs.highlightBlock(target)
        })
      },
    })
    Vue.directive("highlight-code", {
      inserted: highlightCodeBlocks,
      componentUpdated: highlightCodeBlocks,
    })
  },
}
