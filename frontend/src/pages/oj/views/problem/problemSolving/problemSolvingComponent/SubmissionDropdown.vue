<template>
  <tr class="dropdown-row">
    <td colspan="7" class="dropdown-cell">
      <div class="dropdown-content">
        <SubmissionAcceptedDropdown
          v-if="isAccepted"
          :submission="submission"
          :contestID="contestID"
          :isDarkMode="isDarkMode"
        />
        <SubmissionErrorDropdown
          v-else
          :submission="submission"
          :contestID="contestID"
          :isDarkMode="isDarkMode"
        />
      </div>
    </td>
  </tr>
</template>

<script>
import SubmissionAcceptedDropdown from "./SubmissionAcceptedDropdown.vue";
import SubmissionErrorDropdown from "./SubmissionErrorDropdown.vue";

export default {
  name: "SubmissionDropdown",
  components: {
    SubmissionAcceptedDropdown,
    SubmissionErrorDropdown,
  },
  props: {
    submission: {
      type: Object,
      required: true,
    },
    contestID: {
      type: String,
      default: null,
    },
    isDarkMode: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    isAccepted() {
      return this.submission.result === 0;
    },
  },
};
</script>

<style scoped lang="less">
.dropdown-row {
  cursor: default;
}

.dropdown-cell {
  padding: 10px;
  border-bottom: 1px solid var(--dropdown-border);
}

.dropdown-content {
  animation: slideDown 0.8s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
