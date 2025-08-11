<script>
import SubmissionListItem from "./SubmissionListItem.vue"

export default {
  name: "SubmissionTable",
  components: { SubmissionListItem },
  props: {
    data: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

<template>
  <table>
    <thead>
      <tr>
        <th class="large">{{ $t("m.When") }}</th>
        <th class="large">{{ $t("m.ID") }}</th>
        <th class="large">{{ $t("m.Status") }}</th>
        <th class="small">{{ $t("m.Problem") }}</th>
        <th class="small">{{ $t("m.Time") }}</th>
        <th class="small">{{ $t("m.Memory") }}</th>
        <th class="small">{{ $t("m.Language") }}</th>
        <th class="medium">{{ $t("m.Author") }}</th>
      </tr>
    </thead>
    <tbody>
      <SubmissionListItem v-for="item in data" :key="item.id" :item="item" />
    </tbody>
  </table>
</template>

<style scoped lang="less">
table {
  border-spacing: 0;
  margin-bottom: 10px;
}

th {
  text-align: center;
  font-size: 1em;
  font-weight: 600;
  background-color: var(--pale-point-color);
  padding: 10px 0;
  border-width: 0;
  border-bottom: 1px solid #e0e0e0;
}

.large {
  width: 12.5%;
}

.medium {
  width: 14%;
}

.small {
  width: 7%;
}
</style>
