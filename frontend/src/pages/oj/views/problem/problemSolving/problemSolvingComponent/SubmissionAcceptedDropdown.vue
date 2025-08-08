<template>
  <div class="submission-accepted-dropdown" :class="themeClass">
    <!-- 제출 통계 섹션 (contestID가 없을 때만 표시) -->
    <SubmissionStats v-if="!contestID" :stats="submissionRank" />

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
import api from "@oj/api";
import SubmissionStats from "./SubmissionStats.vue";
import ExpandableCode from "./ExpandableCode.vue";
import { HIGHLIGHT_JS_LANGUAGES } from "../../../../../../utils/constants";

export default {
  name: "SubmissionAcceptedDropdown",
  components: {
    SubmissionStats,
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
  data() {
    return {
      submissionRank: {},
    };
  },
  computed: {
    themeClass() {
      return this.isDarkMode ? "dark-theme" : "light-theme";
    },
  },
  mounted() {
    // contestID가 없을 때만 제출 통계를 가져옴
    if (!this.contestID) {
      this.fetchSubmissionRank();
    }
  },
  methods: {
    getHljsLanguage(language) {
      return HIGHLIGHT_JS_LANGUAGES[language] || "plaintext";
    },

    async fetchSubmissionRank() {
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
    },
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
  gap: 36px;
}
</style>
