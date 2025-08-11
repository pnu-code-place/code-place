<script>
import ChallengeBadge from "./AchievementBadge.vue"

export default {
  name: "challenge-summary",
  components: {
    ChallengeBadge,
  },
  props: {
    achievements: {
      type: Array,
      default() {
        return []
      },
    },
  },
  data() {
    return {}
  },
}
</script>

<template>
  <div class="challenge-summary">
    <div class="badge-wrapper" v-for="achievement in achievements">
      <ChallengeBadge
        :image="achievement.image"
        :description="achievement.description"
        :title="achievement.title"
        :acquireTime="achievement.acquireTime"
        :key="achievement.id"
      ></ChallengeBadge>
    </div>
  </div>
</template>

<style scoped lang="less">
.challenge-summary {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  height: 100%;
  .badge-wrapper {
    width: 70px;
    display: flex;
  }
}
</style>
