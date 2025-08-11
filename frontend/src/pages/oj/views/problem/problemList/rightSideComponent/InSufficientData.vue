<template>
  <div class="insufficient-data-wrapper">
    <img src="@/assets/icon_thinking.png" width="60" />
    <template v-if="type">
      <div style="margin-top: 15px">
        <span style="font-size: 15px; font-weight: bold; margin-bottom: 5px">
          데이터가 부족해서 통계를 볼 수 없어요</span
        >
        <br />
        <span style="font-size: medium; font-weight: bold"
          >문제를 더 많이 풀어주세요</span
        >
      </div>
    </template>
    <template v-else>
      <div style="margin-top: 15px">
        <span style="font-size: 15px; font-weight: bold; margin-bottom: 5px">
          문제 데이터가 부족해요</span
        >
      </div>
    </template>
  </div>
</template>

<script>
import { defineComponent } from "vue"

export default defineComponent({
  props: {
    type: Boolean,
  },
})
</script>

<style scoped lang="less">
.insufficient-data-wrapper {
  border-radius: 10px;
  border: 1px solid rgba(230, 229, 229, 0.24);
  background-color: rgba(244, 244, 244, 0.24);
  box-shadow: 0 3px 2px -3px #333;
  padding-top: 20px;
  padding-bottom: 20px;
  margin-bottom: 20px;
  justify-content: center;
  align-items: center;
  span {
    color: #5c6773;
  }
}
</style>
