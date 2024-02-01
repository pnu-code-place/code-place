<script>
import ChallengeBadge from "./ChallengeBadge.vue";
import {CHALLENGES} from "../challengeSection/challenges";

export default {
  name: "challenge-summary",
  components: {
    ChallengeBadge,
  },
  props: {
    achieves: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    return {}
  }
}

</script>

<template>
  <div class="challenge-summary">
    <div class="badge-wrapper" v-for="challenge in achieves">
      <ChallengeBadge
          :image="challenge.image"
          :description="challenge.description"
          :title="challenge.title"
          :key="challenge.id"
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
    width: 50px;
    display: flex;
  }
}
</style>
