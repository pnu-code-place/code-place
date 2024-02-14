<script>
import OjSummary from "./OJSummary.vue";
import CategorySummary from "./CategorySummary.vue";
import DifficultySummary from "./DifficultySummary.vue";
import ChallengeSummary from "./AchievementSummary.vue";
import api from "@oj/api";
import DashboardSkeleton from "./DashboardSkeleton.vue";
import AchievementsSkeleton from "../AchievementsSkeleton.vue";

export default {
  name: "dashboard-section",
  data() {
    return {
      isLoading : true,
      dashboardInfo: {}
    }
  },
  components: {AchievementsSkeleton, DashboardSkeleton, ChallengeSummary, DifficultySummary, OjSummary, CategorySummary},
  methods: {
    init() {
      api.getDashboardInfo().then(res => {
        this.dashboardInfo = res.data.data
        this.isLoading = false
      })
    }
  },
  mounted() {
    this.init()
  }
}
</script>

<template>
  <section>
    <h1>OJ 랭크</h1>
    <OjSummary v-if="this.dashboardInfo.ojStatus" :ojStatus="this.dashboardInfo.ojStatus"></OjSummary>
    <DashboardSkeleton v-else-if="this.isLoading"></DashboardSkeleton>
    <hr/>
    <h1>영역별 분포</h1>
    <CategorySummary v-if="this.dashboardInfo.categoryInfo" :categoryInfo="this.dashboardInfo.categoryInfo"></CategorySummary>
    <DashboardSkeleton v-else-if="this.isLoading"></DashboardSkeleton>
    <hr/>
    <h1>난이도 분포</h1>
    <DifficultySummary v-if="this.dashboardInfo.difficultyInfo" :difficultyInfo="this.dashboardInfo.difficultyInfo"></DifficultySummary>
    <DashboardSkeleton v-else-if="this.isLoading"></DashboardSkeleton>
    <hr/>
    <h1>도전과제</h1>
    <ChallengeSummary v-if="this.dashboardInfo.achievements" :achievements="this.dashboardInfo.achievements"></ChallengeSummary>
    <AchievementsSkeleton v-else-if="this.isLoading"></AchievementsSkeleton>
  </section>
</template>

<style scoped lang="less">
section {
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 20px;
  gap: 15px;
  display: flex;
  flex-direction: column;

  hr {
    border: 0.5px solid #dedede;
    margin: 10px 10px 10px 0;
  }

  h1 {
    text-align: left;
    margin-left: 10px;
    margin-bottom: 15px;
  }
}
</style>
