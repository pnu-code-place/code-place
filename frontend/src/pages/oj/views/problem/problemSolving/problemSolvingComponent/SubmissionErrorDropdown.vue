<template>
  <div class="submission-error-dropdown">
    <!-- 에러 메시지 섹션 -->
    <div class="error-message">
      <p class="sub-title">에러 메시지</p>
      <CodeHighlight
        type="error"
        :code="submission.statistic_info.err_info || 'No error information'"
        :theme.sync="theme"
      />
    </div>

    <!-- 테스트케이스 정보 섹션 -->
    <div v-if="hasFailedTestCase">
      <div class="failed-tc-header">
        <p>최초 실패 케이스</p>
        <CustomTooltip
          content="테스트케이스 중 최초로 실패한 케이스의 입력값과 기대값입니다."
          placement="right"
        >
          <Icon type="ios-information" />
        </CustomTooltip>
      </div>
      <div class="testcase-info">
        <div class="testcase-input">
          <p>입력값</p>
          <CodeHighlight
            type="plaintext"
            :code="submission.first_failed_tc_io.input || ''"
            :theme.sync="theme"
          />
        </div>
        <div class="testcase-output">
          <p>기대값</p>
          <CodeHighlight
            type="plaintext"
            :code="submission.first_failed_tc_io.output || ''"
            :theme.sync="theme"
          />
        </div>
      </div>
    </div>

    <!-- 제출 코드 섹션 -->
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
import CustomTooltip from "@oj/components/CustomTooltip";
import { HIGHLIGHT_JS_LANGUAGES } from "../../../../../../utils/constants";

export default {
  name: "SubmissionErrorDropdown",
  components: {
    CodeHighlight,
    CustomTooltip,
  },
  props: {
    submission: {
      type: Object,
      required: true,
    },
    theme: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    hasFailedTestCase() {
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
  gap: 24px;
}

.sub-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
}

.error-message {
  /deep/ .code-highlight-wrapper {
    max-width: 100%;
    max-height: 300px;
    overflow: auto;
  }
}

.failed-tc-header {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  font-weight: bold;
  gap: 8px;
}

.testcase-info {
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  gap: 16px;

  p {
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 8px;
  }
}

.testcase-input,
.testcase-output {
  flex: 1;
  max-width: 50%;
  display: flex;
  flex-direction: column;

  /deep/ .code-highlight-wrapper {
    flex: 1;
    max-width: 100%;
    max-height: 300px;
    overflow: auto;
  }
}
</style>
