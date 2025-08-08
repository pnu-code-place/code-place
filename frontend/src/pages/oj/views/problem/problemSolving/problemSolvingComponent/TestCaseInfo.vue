<template>
  <div class="testcase-info">
    <div class="testcase-header">
      <p class="sub-title">최초 실패 케이스</p>
      <CustomTooltip
        content="테스트케이스 중 최초로 실패한 케이스의 입력값과 기대값입니다."
        placement="right"
      >
        <Icon type="ios-information" />
      </CustomTooltip>
    </div>
    <div class="testcase-content">
      <div class="testcase-section">
        <p class="testcase-label">입력값</p>
        <CodeHighlight
          type="plaintext"
          :code="testCase.input || ''"
          :isDarkMode="isDarkMode"
        />
      </div>
      <div class="testcase-section">
        <p class="testcase-label">기대값</p>
        <CodeHighlight
          type="plaintext"
          :code="testCase.output || ''"
          :isDarkMode="isDarkMode"
        />
      </div>
    </div>
  </div>
</template>

<script>
import CodeHighlight from "./CodeHighlight.vue";
import CustomTooltip from "@oj/components/CustomTooltip";

export default {
  name: "TestCaseInfo",
  components: {
    CodeHighlight,
    CustomTooltip,
  },
  props: {
    testCase: {
      type: Object,
      required: true,
    },
    isDarkMode: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style scoped lang="less">
.testcase-info {
  .testcase-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;

    .sub-title {
      font-size: 14px;
      font-weight: bold;
    }
  }

  .testcase-content {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    gap: 16px;
  }

  .testcase-section {
    flex: 1;
    max-width: 50%;
    display: flex;
    flex-direction: column;

    .testcase-label {
      font-size: 13px;
      font-weight: bold;
      margin-bottom: 8px;
    }

    /deep/ .code-highlight-wrapper {
      flex: 1;
      max-width: 100%;
      max-height: 300px;
      overflow: auto;
    }
  }
}
</style>
