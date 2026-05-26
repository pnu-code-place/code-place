<template>
  <button type="button" class="submissionBtnWrapper" @click="submitCode">
    <span>제출</span>
  </button>
</template>

<script>
import { defineComponent } from "vue"
import { mapGetters } from "vuex"
import { JUDGE_STATUS } from "../../../../../../utils/constants"

export default defineComponent({
  props: {
    isSubmitting: Boolean,
  },
  methods: {
    submitCode() {
      if (!this.isSubmitting) {
        this.$emit("create-submission")
      }
    },
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
  },
})
</script>

<style scoped lang="less">
.submissionBtnWrapper {
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  border-radius: 10px;
  padding: 6px 12px;
  cursor: pointer;
  transition: width 0.3s;
  border: none;
  background-color: var(--submission-primary-btn-bg);
  color: var(--submission-primary-btn-text-color);
  i {
    font-size: smaller;
  }
}

.submissionBtnWrapper:hover {
  background-color: var(--submission-primary-btn-hover-bg);
  color: var(--submission-primary-btn-hover-text-color);
}
</style>
