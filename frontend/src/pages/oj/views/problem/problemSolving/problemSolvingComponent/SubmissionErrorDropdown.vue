<template>
  <div class="submission-error-dropdown">
    <div>
      <p class="sub-title">에러 메시지</p>
      <CodeHighlight
        type="error"
        :code="submission.statistic_info.err_info || 'No error information'"
        :theme.sync="theme"
      />
    </div>
    <div>
      <p class="sub-title">제출 코드</p>
      <CodeHighlight
        type="code"
        :code="submission.code || ''"
        :language="getHljsLanguage(submission.language)"
        :theme.sync="theme"
      />
    </div>
  </div>
</template>

<script>
import CodeHighlight from "./CodeHighlight.vue";
import { HIGHLIGHT_JS_LANGUAGES } from "../../../../../../utils/constants";

export default {
  name: "SubmissionErrorDropdown",
  components: {
    CodeHighlight,
  },
  props: {
    submission: {
      type: Object,
    },
    theme: {
      type: Boolean,
      default: false, // Default to light theme
    }
  },
  mounted() {
    console.log("submission:", this.submission);
  },
  methods: {
    getHljsLanguage(language) {
      return HIGHLIGHT_JS_LANGUAGES[language] || "plaintext";
    },
  },
};
</script>

<style scoped lang="less">
.submission-error-dropdown {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.error-info {
  padding: 10px;
  background-color: var(--error-message-bg);
  color: var(--error-message-text);
  border-radius: 6px;
  font-family: "Fira Mono", "Menlo", "Consolas", monospace;
  font-size: 13px;
  white-space: pre-line;
  word-break: break-all;
  border: 1px solid var(--dropdown-border);
  box-shadow: 0 1px 4px 0 rgba(0, 0, 0, 0.08);
}

.submitted-code {
  padding: 10px;
  background-color: var(--dropdown-bg);
  color: var(--text-color);
  font-size: 13px;
  border-radius: 5px;
  font-family: monospace;
  white-space: pre-line;
  word-break: break-all;
  border: 1px solid var(--dropdown-border);
  box-shadow: 0 1px 4px 0 rgba(0, 0, 0, 0.08);
}

.sub-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
}
</style>
