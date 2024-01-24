<script>
import ChallengeBadge from "./ChallengeBadge.vue";
import {CHALLENGES} from "../ChallengeSection/challenges";

export default {
  name: "challenge-summary",
  components: {
    ChallengeBadge,
  },
  props: {
    achievedChallenges: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  computed: {
    challenges() {
      return this.achievedChallenges.map(chID => CHALLENGES[chID])
    },
    testImage() {
      return require("@/assets/challenges/on_error_image.png")
    }
  },
  data() {
    return {}
  }
}

</script>

<template>
  <div class="challenge-summary">
    <div class="badge-wrapper" v-for="challenge in challenges">
      <ChallengeBadge
          :image="challenge.image"
          :tooltip="challenge.description"
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
