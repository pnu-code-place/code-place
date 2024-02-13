<script>
import GoalCard from "./AchievementCard.vue";
import api from "@oj/api";

export default {
  name: 'challenge-section',
  components: {GoalCard},
  data() {
    return {
      value : 0,
      errorMedal: "@/assets/challenges/errorMedal.png",
      achievements : {
        acquired: [],
        not_acquired: []
      },
      image: "https://cdn-icons-png.flaticon.com/512/473/47340.png",
      loading : true,
      error : null
    }
  },
  methods: {
    init() {
      api.getUserAchievement().then(res => {
        this.achievements = res.data.data
      })
    }
  },
  mounted() {
    this.init();
  },
  computed: {
  }
}
</script>

<template>
  <section class="challenge-section">
    <h1>{{ $t('m.Achieved') }}</h1>
    <ul>
      <GoalCard v-for="goal in achievements.acquired" :key="goal.id" :achievement="goal"
                :acquired="true"></GoalCard>
    </ul>
    <h1>{{ $t('m.NotAchieved') }}</h1>
    <ul>
      <GoalCard v-for="goal in achievements.not_acquired" :key="goal.id" :achievement="goal"
                :acquired="false"></GoalCard>
    </ul>
  </section>
</template>

<style scoped lang="less">
section {
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 20px;

  h1 {
    margin-bottom: 10px;
    text-align: left;
  }

  ul {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    padding: 0;
    margin: 0;
    list-style: none;
  }
}
</style>
