<template>
  <div class="submission-error-dropdown">
    <!-- 에러 메시지 섹션 -->
    <div class="error-message">
      <p class="sub-title">에러 메시지</p>
      <CodeHighlight
        type="error"
        :code="submission.statistic_info.err_info || 'No error information'"
        :isDarkMode="isDarkMode"
      />
    </div>

    <!-- 테스트케이스 정보 섹션 (contestID가 없을 때만 표시) -->
    <TestCaseInfo
      v-if="shouldShowTestCase"
      :testCase="submission.first_failed_tc_io"
      :isDarkMode="isDarkMode"
    />

    <!-- 제출 코드 섹션 -->
    <ExpandableCode
      title="제출 코드"
      :code="submission.code || ''"
      :language="getHljsLanguage(submission.language)"
      :isDarkMode="isDarkMode"
    />
  </div>
</template>

<script>
import CodeHighlight from "./CodeHighlight.vue";
import TestCaseInfo from "./TestCaseInfo.vue";
import ExpandableCode from "./ExpandableCode.vue";
import { HIGHLIGHT_JS_LANGUAGES } from "../../../../../../utils/constants";

export default {
  name: "SubmissionErrorDropdown",
  components: {
    CodeHighlight,
    TestCaseInfo,
    ExpandableCode,
  },
  props: {
    submission: {
      type: Object,
      required: true,
    },
    contestID: {
      type: String,
      default: null,
    },
    isDarkMode: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    shouldShowTestCase() {
      // contestID가 없고, 실패한 테스트케이스 정보가 있을 때만 표시
      if (this.contestID) return false;

      const tcInfo = this.submission.first_failed_tc_io;
      return tcInfo && tcInfo.input && tcInfo.output;
    },
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
  gap: 36px;
}

.sub-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 12px;
}

.error-message {
  /deep/ .code-highlight-wrapper {
    // max-width: 100%;
    max-height: 300px;
    overflow: auto;
  }
}
</style>
