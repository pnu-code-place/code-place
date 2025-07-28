<template>
  <div class="submission-accepted-dropdown" :class="themeClass">
    <!-- 제출 통계 섹션 -->
    <div>
      <p class="sub-title">제출 분석</p>
      <div class="submission-ranking">
        <div class="ranking-box">
          <p class="sub-title">제출 순위</p>
          <div class="ranking-content">
            <span class="prefix">#</span>
            <span class="value">{{ submissionRank.solvedRank || '0' }}</span>
          </div>
        </div>
        <div class="ranking-box">
          <p class="sub-title">시간 비용</p>
          <div class="ranking-content">
            <span class="prefix">상위</span>
            <span class="value">{{ submissionRank.timeCostPercent || '0' }}</span>
            <span class="suffix">%</span>
          </div>
        </div>
        <div class="ranking-box">
          <p class="sub-title">메모리 비용</p>
          <div class="ranking-content">
            <span class="prefix">상위</span>
            <span class="value">{{ submissionRank.memoryCostPercent || '0' }}</span>
            <span class="suffix">%</span>
          </div>
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
import api from '@oj/api';
import CodeHighlight from "./CodeHighlight.vue";
import { HIGHLIGHT_JS_LANGUAGES } from "../../../../../../utils/constants";

export default {
  name: "SubmissionAcceptedDropdown",
  components: {
    CodeHighlight,
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
  mounted() {
    this.getSubmissionRank();
  },
  computed: {
    themeClass() {
      return this.theme ? 'dark-theme' : 'light-theme';
    }
  },
  data() {
    return {
      submissionRank: {},
    }
  },
  methods: {
    getHljsLanguage(language) {
      return HIGHLIGHT_JS_LANGUAGES[language] || "plaintext";
    },
    async getSubmissionRank() {
      try {
        const res = await api.getSubmissionRank(this.submission.id);
        this.submissionRank = {
          solvedRank: res.data.data.solved_rank,
          timeCostPercent: res.data.data.time_cost_percent,
          memoryCostPercent: res.data.data.memory_cost_percent,
        };
      } catch (error) {
        console.error("Failed to fetch submission rank:", error);
      }
    }
  },
};
</script>

<style scoped lang="less">
.dark-theme {
  --dropdown-bg: #1e1e1e;
  --dropdown-text: #d4d4d4;
  --border-color: #333333;
  --box-shadow: 0 2px 8px rgba(255, 255, 255, 0.06);
  --box-shadow-hover: 0 4px 12px rgba(255, 255, 255, 0.1);
}

.light-theme {
  --dropdown-bg: #ffffff;
  --dropdown-text: #1f2937;
  --border-color: #e5e7eb;
  --box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  --box-shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.submission-accepted-dropdown {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.sub-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
}

.submission-ranking {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.ranking-box {
  flex: 1;
  text-align: center;
  padding: 16px 12px;
  border-radius: 8px;
  background-color: var(--dropdown-bg);
  color: var(--dropdown-text);
  border: 1px solid var(--border-color);
  box-shadow: var(--box-shadow);
  transition: all 0.2s ease;
}

.ranking-box:hover {
  box-shadow: var(--box-shadow-hover);
}

.ranking-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-top: 4px;
}

.prefix,
.suffix {
  font-size: 12px;
  font-weight: normal;
}

.value {
  font-size: 24px;
  font-weight: bold;
}
</style>
