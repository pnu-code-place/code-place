<script>
import OjSummary from "./OJSummary.vue";
import CategorySummary from "./CategorySummary.vue";
import DifficultySummary from "./DifficultySummary.vue";

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
      },

      category_info : {
        data_structure: {
          solve_number: 33,
          ranking: 60,
          ranking_percent: 0.3,
        },
        mathematics: {
          solve_number: 20,
          ranking: 101,
          ranking_percent: 0.505,
        },
        sorting: {
          solve_number: 45,
          ranking: 34,
          ranking_percent: 0.17,
        },
        implementation: {
          solve_number: 61,
          ranking: 20,
          ranking_percent: 0.101,
        },
        searching: {
          solve_number: 3,
          ranking: 190,
          ranking_percent: 0.95,
        }
      },

      difficulty_info : {
        very_easy: {
          solve_number: 33,
          ranking: 60,
          ranking_percent: 0.3,
        },
        easy: {
          solve_number: 20,
          ranking: 101,
          ranking_percent: 0.505,
        },
        medium: {
          solve_number: 45,
          ranking: 34,
          ranking_percent: 0.17,
        },
        hard: {
          solve_number: 61,
          ranking: 20,
          ranking_percent: 0.101,
        },
        very_hard: {
          solve_number: 3,
          ranking: 190,
          ranking_percent: 0.95,
        }
      }
    }
  },
  components: {DifficultySummary, OjSummary, CategorySummary},
}
</script>

<template>
  <section>
    <h1>OJ 랭크</h1>
    <OjSummary :ojStatus="ojStatus"></OjSummary>
    <h1>영역별 분포</h1>
    <CategorySummary :category_info="category_info"></CategorySummary>
    <h1>난이도 분포</h1>
    <DifficultySummary :difficulty_info="difficulty_info"></DifficultySummary>
  </section>
</template>

<style scoped lang="less">
section {
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 20px;
  gap: 10px;
  display : flex;
  flex-direction: column;

  h1 {
    text-align: left;
    margin-bottom: 10px;
  }
}
</style>
