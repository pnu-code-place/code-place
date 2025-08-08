<template>
  <div class="submission-stats">
    <p class="sub-title">제출 분석</p>
    <div class="stats-grid">
      <div class="stat-box">
        <p class="stat-label">제출 순위</p>
        <div class="stat-value">
          <span class="prefix">#</span>
          <span class="value">{{ stats.solvedRank || "0" }}</span>
        </div>
      </div>
      <div class="stat-box">
        <p class="stat-label">시간 비용</p>
        <div class="stat-value">
          <span class="prefix">상위</span>
          <span class="value">{{ stats.timeCostPercent || "0" }}</span>
          <span class="suffix">%</span>
        </div>
      </div>
      <div class="stat-box">
        <p class="stat-label">메모리 비용</p>
        <div class="stat-value">
          <span class="prefix">상위</span>
          <span class="value">{{ stats.memoryCostPercent || "0" }}</span>
          <span class="suffix">%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SubmissionStats",
  props: {
    stats: {
      type: Object,
      default: () => ({}),
    },
  },
};
</script>

<style scoped lang="less">
.submission-stats {
  .sub-title {
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 12px;
  }

  .stats-grid {
    display: flex;
    justify-content: space-between;
    gap: 16px;
  }

  .stat-box {
    flex: 1;
    text-align: center;
    padding: 16px 12px;
    border-radius: 8px;
    background-color: var(--dropdown-bg);
    color: var(--dropdown-text);
    border: 1px solid var(--border-color);
    box-shadow: var(--box-shadow);
    transition: all 0.2s ease;

    &:hover {
      box-shadow: var(--box-shadow-hover);
    }
  }

  .stat-label {
    font-size: 12px;
    font-weight: bold;
    margin-bottom: 4px;
  }

  .stat-value {
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
}
</style>
