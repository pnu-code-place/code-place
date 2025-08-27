<template>
  <div class="expandable-code">
    <div class="code-header">
      <p class="sub-title">{{ title }}</p>
      <span class="expand-hint" v-if="!isExpanded">클릭하여 펼치기</span>
    </div>
    <div
      class="code-wrapper"
      :class="{ expanded: isExpanded }"
      @click="toggleExpansion"
    >
      <CodeHighlight
        :type="codeType"
        :code="code"
        :language="language"
        :isDarkMode="isDarkMode"
      />
    </div>
  </div>
</template>

<script>
import CodeHighlight from "./CodeHighlight.vue"

export default {
  name: "ExpandableCode",
  components: {
    CodeHighlight,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    code: {
      type: String,
      default: "",
    },
    language: {
      type: String,
      default: "plaintext",
    },
    codeType: {
      type: String,
      default: "code",
    },
    isDarkMode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isExpanded: false,
    }
  },
  methods: {
    toggleExpansion() {
      this.isExpanded = !this.isExpanded
    },
  },
}
</script>

<style scoped lang="less">
.expandable-code {
  .code-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .sub-title {
      font-size: 14px;
      font-weight: bold;
      margin-bottom: 12px;
    }

    .expand-hint {
      font-size: 12px;
      color: var(--text-color);
      font-style: italic;
    }
  }

  .code-wrapper {
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 4px;

    &:hover {
      background-color: rgba(0, 0, 0, 0.02);
    }

    /deep/ .code-highlight-wrapper {
      max-height: 300px;
      overflow: hidden;
      transition: max-height 0.3s ease;
    }

    &.expanded {
      /deep/ .code-highlight-wrapper {
        max-height: none;
      }
    }
  }
}
</style>
