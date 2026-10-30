import MarkdownIt from "markdown-it"
import DOMPurify from "dompurify"
import hljs from "highlight.js/lib/core"
import c from "highlight.js/lib/languages/c"
import cpp from "highlight.js/lib/languages/cpp"
import java from "highlight.js/lib/languages/java"
import javascript from "highlight.js/lib/languages/javascript"
import python from "highlight.js/lib/languages/python"

hljs.registerLanguage("c", c)
hljs.registerLanguage("cpp", cpp)
hljs.registerLanguage("java", java)
hljs.registerLanguage("javascript", javascript)
hljs.registerLanguage("python", python)

// AI 조교 답변용 마크다운 렌더러
// - html: false → 답변에 섞인 HTML은 그대로 문자열로 표시
// - 링크/이미지는 렌더링하지 않음 (외부 리소스 로딩·피싱 방지)
const md = new MarkdownIt({
  html: false,
  linkify: false,
  breaks: true,
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang, ignoreIllegals: true })
          .value
      } catch {
        // 하이라이트 실패 시 markdown-it 기본 이스케이프 사용
      }
    }
    return ""
  },
}).disable(["link", "image"])

export function renderMarkdown(text) {
  return DOMPurify.sanitize(md.render(text || ""))
}
