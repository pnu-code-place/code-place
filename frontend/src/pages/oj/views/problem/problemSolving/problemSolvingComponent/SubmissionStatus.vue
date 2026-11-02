<template>
  <!-- 좁은 헤더에서는 제출 전 빈 자리표시를 숨김 -->
  <div
    v-if="!(compact && !statusVisible)"
    class="submissionStatusWrapper"
    :class="{ compact }"
    :title="compact ? compactTitle : null"
  >
    <template v-if="!statusVisible">
      <span>{{ $t("m.Code_Editor_Submission_Result") }}</span>
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
        <span v-if="!compact">{{ submissionStatusLabel }}</span>
      </div>
    </template>
    <template
      v-else-if="
        statusVisible && this.contestID && !OIContestRealTimePermission
      "
    >
      <div class="submission-success">
        <Icon type="ios-checkmark-circle" />
        <span v-if="!compact">{{ $t("m.Submitted_successfully") }}</span>
      </div>
    </template>
  </div>
</template>

<script>
import { defineComponent } from "vue"
import { mapGetters } from "vuex"
import { JUDGE_STATUS } from "../../../../../../utils/constants"

export default defineComponent({
  props: {
    statusVisible: Boolean,
    contestID: [String, Number],
    result: Object,
    submissionId: String,
    // 좁은 헤더에서 아이콘만 표시, 내용은 툴팁
    compact: {
      type: Boolean,
      default: false,
    },
  },
  components: {},
  data() {
    return {}
  },
  methods: {
    handleRoute(route) {
      this.$router.push(route)
    },
  },
  computed: {
    ...mapGetters(["OIContestRealTimePermission"]),
    submissionStatus() {
      return {
        text: JUDGE_STATUS[this.result.result]["name"],
        color: JUDGE_STATUS[this.result.result]["color"],
      }
    },
    submissionStatusLabel() {
      return this.$t("m." + this.submissionStatus.text.replace(/ /g, "_"))
    },
    compactTitle() {
      if (this.contestID && !this.OIContestRealTimePermission) {
        return this.$t("m.Submitted_successfully")
      }
      return this.submissionStatusLabel
    },
  },
})
</script>

<style scoped lang="less">
.submissionStatusWrapper {
  font-weight: 600;
  font-size: 14px;
  bottom: 70px;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  border-radius: 10px;
  padding: 6px 12px;
  cursor: pointer;
  transition: width 0.3s;
  box-shadow: inset 0 0 1px;
  color: var(--submission-result-btn-text-color);
  background-color: var(--submission-result-btn-color);
  white-space: nowrap;

  &.compact {
    padding: 6px 9px;

    .submissionState i {
      margin-right: 0;
    }
  }
}

.submissionState {
  i {
    margin-right: 5px;
  }

  display: flex;
  align-items: center;
  font-size: 14px;
  justify-content: space-evenly;
  color: var(--ps-content-text-color);
}

.submission-success {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--ps-content-text-color);

  .ivu-icon {
    color: #16a34a;
  }
}
</style>
