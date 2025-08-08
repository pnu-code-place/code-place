<template>
  <div class="submissionStatusWrapper">
    <template v-if="!statusVisible">
      <span>제출결과</span>
    </template>
    <template
      v-else-if="
        statusVisible &&
        (!this.contestID || (this.contestID && OIContestRealTimePermission))
      "
    >
      <div
        class="submissionState"
        @click="handleRoute('/status/' + submissionId)"
      >
        <i
          v-if="
            submissionStatus.text === 'Submitting' ||
            submissionStatus.text === 'Judging'
          "
          class="fas fa-circle-notch fa-spin"
          style="color: #e39530"
        />
        <i
          v-else
          class="fas fa-circle"
          :style="{ color: submissionStatus.color }"
        />
        {{ $t("m." + submissionStatus.text.replace(/ /g, "_")) }}
      </div>
    </template>
    <template
      v-else-if="
        statusVisible && this.contestID && !OIContestRealTimePermission
      "
    >
      <Alert type="success" show-icon>{{
        $t("m.Submitted_successfully")
      }}</Alert>
    </template>
  </div>
</template>

<script>
import { defineComponent } from "vue";
import { mapGetters } from "vuex";
import { JUDGE_STATUS } from "../../../../../../utils/constants";

export default defineComponent({
  props: {
    statusVisible: Boolean,
    contestID: String,
    result: Object,
    submissionId: String,
  },
  components: {},
  data() {
    return {};
  },
  methods: {
    handleRoute(route) {
      this.$router.push(route);
    },
  },
  computed: {
    ...mapGetters(["OIContestRealTimePermission"]),
    submissionStatus() {
      return {
        text: JUDGE_STATUS[this.result.result]["name"],
        color: JUDGE_STATUS[this.result.result]["color"],
      };
    },
  },
});
</script>

<style scoped lang="less">
.submissionStatusWrapper {
  font-weight: 700;
  font-size: medium;
  bottom: 70px;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  border-radius: 10px;
  padding-right: 10px;
  padding-left: 10px;
  height: 32px;
  cursor: pointer;
  transition: width 0.3s;
  margin-left: 10px;
  box-shadow: inset 0 0 1px;
  color: var(--submission-result-btn-text-color);
  background-color: var(--submission-result-btn-color);
}

.submissionState {
  i {
    margin-right: 5px;
  }

  display: flex;
  align-items: center;
  font-size: small;
  justify-content: space-evenly;
  color: var(--ps-content-text-color);
}
</style>
