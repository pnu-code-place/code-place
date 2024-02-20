<template>
  <ul>
    <li v-for="i in this.count" :key="i">
      <shine-wrapper>
        <img src="@/assets/challenges/errorMedal.png" class="medal-skeleton" alt="medal"/>
      </shine-wrapper>
    </li>
  </ul>
</template>

<script>

import ShineWrapper from "../../../../components/ShineWrapper.vue";

export default {
  name: 'AchievementsSkeleton',
  data() {
    return {
      image: require("@/assets/challenges/errorMedal.png")
    }
  },
  components: {ShineWrapper},
  props: {
    count: {
      type: Number,
      default: 6
    }
  }
}
</script>

<style scoped lang="less">
ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: 10px;

  li {
    width: 70px;
    height: auto;
    padding: 5px;

    .medal-skeleton {
      width: 100%;
      height: auto;
      opacity: 0.2;
      // 색상 변형
      filter: invert(95%) sepia(0%) saturate(272%) hue-rotate(247deg) brightness(83%) contrast(81%);
    }
  }
}
</style>
