<template>
  <div class="code-highlight-wrapper" :class="themeClass">
    <code ref="code" :class="languageClass" v-html="highlightedCode"></code>
  </div>
</template>

<script>
import hljs from "highlight.js";
import "highlight.js/styles/solarized-light.css";
import "highlight.js/styles/atom-one-dark.css";

/**
 * 코드 하이라이팅 컴포넌트
 * highlight.js를 사용하여 코드 구문 강조 표시를 제공하며,
 * 라이트/다크 테마 지원 및 에러 메시지 표시 기능을 포함합니다.
 */
export default {
  name: "CodeHighlight",
  
  props: {
    /**
     * 컴포넌트 타입
     * @type {String}
     * @default "code"
     * @description "code" - 일반 코드 하이라이팅, "error" - 에러 메시지 표시 (하이라이팅 없음)
     */
    type: { type: String, default: "code" },
    
    /**
     * 표시할 코드 내용
     * @type {String}
     * @required
     * @description 하이라이팅할 코드 문자열
     */
    code: { type: String, required: true },
    
    /**
     * 프로그래밍 언어 타입
     * @type {String}
     * @default "plaintext"
     * @description highlight.js에서 지원하는 언어 코드 (예: javascript, python, css 등)
     */
    language: { type: String, default: "plaintext" },
    
    /**
     * 테마 설정
     * @type {Boolean}
     * @default false
     * @description false - 라이트 테마, true - 다크 테마
     */
    theme: { type: Boolean, default: false },
  },
  
  computed: {
    /**
     * 하이라이팅된 코드 HTML 반환
     * @returns {String} 하이라이팅된 HTML 코드 또는 원본 코드
     */
    highlightedCode() {
      // 코드가 없으면 빈 문자열 반환
      if (!this.code) return "";
      
      // 에러 타입인 경우 하이라이팅 없이 원본 코드 반환
      if (this.type === "error") {
        return this.code;
      }
      
      try {
        return hljs.highlight(this.language, this.code).value;
      } catch (e) {
        // 언어 지정 실패 시 자동 감지로 하이라이팅
        return hljs.highlightAuto(this.code).value;
      }
    },
    
    /**
     * 코드 태그에 적용할 CSS 클래스 반환
     * @returns {String} hljs 및 언어별 클래스명
     */
    languageClass() {
      return "hljs " + (this.language ? "language-" + this.language : "");
    },
    
    /**
     * 테마 및 타입에 따른 CSS 클래스 반환
     * @returns {String} 테마 클래스 및 에러 클래스 조합
     */
    themeClass() {
      // 기본 테마 클래스 설정 (다크/라이트)
      let themeClass = this.theme ? "dark-theme" : "light-theme";
      
      // 에러 타입인 경우 에러 스타일 클래스 추가
      if (this.type === "error") {
        themeClass += " error-info";
      }
      
      return themeClass;
    }
  },
};
</script>

<style scoped>
.dark-theme {
  --dropdown-bg: #2f3542;
  --dropdown-text: #e6e6e6;
}

.light-theme {
  --dropdown-bg: #f9f9f9;
  --dropdown-text: #222;
}

.error-info {
  background-color: #ffebee !important;
  color: #d32f2f;
}

.code-highlight-wrapper {
  margin: 0;
  padding: 12px;
  border-radius: 6px;
  font-size: 13px;
  font-family: "Fira Mono", "Menlo", "Consolas", monospace;
  white-space: pre-line;
  overflow-x: auto;
  background-color: var(--dropdown-bg);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

code {
  background: unset;
  color: unset;
}
</style>
