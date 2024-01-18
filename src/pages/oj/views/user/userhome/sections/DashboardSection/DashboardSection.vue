<script>
import OjSummary from "./OJSummary.vue";

export default {
  name: "dashboard-section",
  data() {
    return {
      ojStatus: {
        rank: 1, // 랭킹
        rank_percent: 0.1, // 랭킹 퍼센트 ( 상위 10% )
        score: 100,
        submission_number: 100,
        accepted_number: 100,
        total_score: 56000, // 현재 점수
        rank_next: 60000, // 다음 랭킹의 허들
        rank_current: 50000, // 이전 랭킹의 허들
        miracle_current : 10, // 현재 연속 코딩일수
        miracle_record : 20 // 최고 연속 코딩일수
      }
    }
  },
  components: {OjSummary}
}
</script>

<template>
  <section>
    <OjSummary :ojStatus="ojStatus"></OjSummary>
  </section>
</template>

<style scoped lang="less">
section {
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 10px;

  h1 {
    text-align: left;
    margin-bottom: 10px;
  }
}
</style>
