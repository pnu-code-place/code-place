import MarkdownIt from "markdown-it"
import markdownItCjkFriendly from "markdown-it-cjk-friendly"
import markdownItTexmath from "markdown-it-texmath"
import katex from "katex"
import DOMPurify from "dompurify"

const hljs = require("highlight.js/lib/core")

const LANG_ALIAS = {
  "c++": "cpp",
  c: "cpp",
  py: "python",
  python3: "python",
}

const md = new MarkdownIt({
  html: false, // 답변 속 HTML 은 글자로 표시
  linkify: false,
  breaks: true, // 줄바꿈 한 번을 <br> 로 표시
})
  // 한글 조사가 붙어도 굵게·기울임 인식
  .use(markdownItCjkFriendly)
  // $...$ 수식 KaTeX 렌더링
  .use(markdownItTexmath, {
    engine: katex,
    delimiters: "dollars",
    katexOptions: { throwOnError: false },
  })

function highlightCode(code, rawLang) {
  const lang = LANG_ALIAS[(rawLang || "").toLowerCase()] || rawLang
  if (lang && hljs.getLanguage(lang)) {
    try {
      return hljs.highlight(code, { language: lang, ignoreIllegals: true })
        .value
    } catch (e) {
      // 강조 실패 시 일반 텍스트로 표시
    }
  }
  return md.utils.escapeHtml(code)
}

// 코드 블록: 언어 이름 표시 + 색 강조
md.renderer.rules.fence = (tokens, idx) => {
  const token = tokens[idx]
  const lang = token.info.trim().split(/\s+/)[0]
  const code = token.content.replace(/\n$/, "")
  const langLabel = lang
    ? `<span class="code-lang">${md.utils.escapeHtml(lang)}</span>`
    : ""
  return `<div class="code-block">${langLabel}<pre><code class="hljs">${highlightCode(code, lang)}</code></pre></div>`
}

// 제목은 모두 h4 로 표시
const renderHeading = (tokens, idx, options, env, self) => {
  tokens[idx].tag = "h4"
  return self.renderToken(tokens, idx, options)
}
md.renderer.rules.heading_open = renderHeading
md.renderer.rules.heading_close = renderHeading

// 이미지는 불러오지 않고 대체 글자만 표시
md.renderer.rules.image = (tokens, idx) =>
  md.utils.escapeHtml(tokens[idx].content)

// 표는 가로 스크롤 상자에 넣음
md.renderer.rules.table_open = () => '<div class="table-wrap"><table>'
md.renderer.rules.table_close = () => "</table></div>"

// 링크는 새 탭으로 열기
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  tokens[idx].attrSet("target", "_blank")
  tokens[idx].attrSet("rel", "noopener noreferrer")
  return self.renderToken(tokens, idx, options)
}

/**
 * AI 조교 답변 마크다운 렌더링.
 * 스트리밍 중 닫히지 않은 코드 블록도 문서 끝까지 코드 블록으로 표시된다.
 */
export function renderAIMarkdown(text) {
  if (!text) return ""
  return DOMPurify.sanitize(md.render(text), { ADD_ATTR: ["target"] })
}
