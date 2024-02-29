<script>
import OjSummary from "./OJSummary.vue";
import FieldSummary from "./FieldSummary.vue";
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
  components: {AchievementsSkeleton, DashboardSkeleton, ChallengeSummary, DifficultySummary, OjSummary, FieldSummary},
  methods: {
    init() {
      api.getDashboardInfo(this.username).then(res => {
        this.dashboardInfo = res.data.data
        this.isLoading = false
      })
    }
  },
  mounted() {
    this.init()
  },
  computed: {
    username() {
      let username = '';

      if (this.$route && this.$route.params && typeof this.$route.params.username === 'string') {
        username = this.$route.params.username;
      }

      if (!username && this.$store && this.$store.state.user && this.$store.state.user.profile && this.$store.state.user.profile.user && typeof this.$store.state.user.profile.user.username === 'string') {
        username = this.$store.state.user.profile.user.username;
      }

      return username;
    }
  }
}
</script>

<template>
  <section>
    <h1>{{$t('m.OJ_Summary')}}</h1>
    <OjSummary v-if="this.dashboardInfo.ojStatus" :ojStatus="this.dashboardInfo.ojStatus"></OjSummary>
    <DashboardSkeleton v-else-if="this.isLoading"></DashboardSkeleton>
    <hr/>
    <h1>{{$t('m.Field_Based_Distribution')}}</h1>
    <FieldSummary v-if="this.dashboardInfo.fieldInfo" :fieldInfo="this.dashboardInfo.fieldInfo"></FieldSummary>
    <DashboardSkeleton v-else-if="this.isLoading"></DashboardSkeleton>
    <hr/>
    <h1>{{$t('m.Difficulty_Based_Distribution')}}</h1>
    <DifficultySummary v-if="this.dashboardInfo.difficultyInfo" :difficultyInfo="this.dashboardInfo.difficultyInfo"></DifficultySummary>
    <DashboardSkeleton v-else-if="this.isLoading"></DashboardSkeleton>
    <hr/>
    <h1>{{ $t('m.Achievement') }}</h1>
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
