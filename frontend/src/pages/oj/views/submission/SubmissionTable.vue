<script>
import SubmissionListItem from "./SubmissionListItem.vue"

export default {
  name: "SubmissionTable",
  components: { SubmissionListItem },
  props: {
    contestID: {
      type: [String, Number],
      default: "",
    },
    data: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    skeletonRows() {
      return Array.from({ length: 18 }, (_, index) => index)
    },
  },
}
</script>

<template>
  <div class="submission-table-wrap">
    <table>
      <thead>
        <tr>
          <th class="submitted-at">{{ $t("m.When") }}</th>
          <th class="problem-id">{{ $t("m.Problem_ID") }}</th>
          <th class="author">{{ $t("m.Submission_Table_Author") }}</th>
          <th class="result">{{ $t("m.Status") }}</th>
          <th class="language">{{ $t("m.Language") }}</th>
          <th class="metric">{{ $t("m.Time") }}</th>
          <th class="metric">{{ $t("m.Memory") }}</th>
        </tr>
      </thead>
      <tbody>
        <template v-if="!loading">
          <SubmissionListItem
            v-for="item in data"
            :key="item.id"
            :contest-id="contestID"
            :item="item"
          />
        </template>
        <template v-else>
          <tr
            v-for="row in skeletonRows"
            :key="`skeleton-${row}`"
            class="skeleton-row"
          >
            <td class="submitted-at"><span class="skeleton-block date"></span></td>
            <td><span class="skeleton-block short"></span></td>
            <td>
              <div class="skeleton-user">
                <span class="skeleton-avatar"></span>
                <span class="skeleton-block name"></span>
              </div>
            </td>
            <td class="result"><span class="skeleton-pill"></span></td>
            <td class="language"><span class="skeleton-block language"></span></td>
            <td class="metric"><span class="skeleton-block metric"></span></td>
            <td class="metric"><span class="skeleton-block metric"></span></td>
          </tr>
        </template>
        <tr v-if="!loading && data.length === 0">
          <td class="empty" colspan="7">{{ $t("m.No_Submissions") }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped lang="less">
.submission-table-wrap {
  position: relative;
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 820px;
  border-spacing: 0;
  border-collapse: separate;
}

th {
  text-align: left;
  font-size: 13px;
  line-height: 1.4;
  font-weight: 700;
  color: #697386;
  background-color: #f7f8fb;
  padding: 10px 16px;
  border-width: 0;
  border-bottom: 1px solid #e6e9f0;
  white-space: nowrap;
}

.submitted-at {
  width: 172px;
  text-align: right;
}

.problem-id {
  width: 116px;
}

.author {
  width: 170px;
}

.result {
  width: 132px;
  text-align: center;
}

.language {
  width: 96px;
  text-align: center;
}

.metric {
  width: 92px;
  text-align: right;
}

.empty {
  padding: 34px 16px;
  text-align: center;
  color: #8a94a6;
}

.skeleton-row td {
  padding: 10px 16px;
  border-bottom: 1px solid #eef1f5;
}

.skeleton-block,
.skeleton-pill,
.skeleton-avatar {
  display: block;
  position: relative;
  overflow: hidden;
  background: #eef2f7;
}

.skeleton-block::after,
.skeleton-pill::after,
.skeleton-avatar::after {
  position: absolute;
  inset: 0;
  content: "";
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.72) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  animation: skeleton-shimmer 1.2s ease-in-out infinite;
  transform: translateX(-100%);
}

.skeleton-block {
  width: 100%;
  height: 12px;
  border-radius: 4px;
}

.skeleton-block.short {
  width: 58px;
}

.skeleton-block.name {
  width: 72px;
}

.skeleton-block.language {
  width: 68px;
}

.result .skeleton-pill,
.language .skeleton-block {
  margin-right: auto;
  margin-left: auto;
}

.skeleton-block.metric {
  width: 54px;
  margin-left: auto;
}

.skeleton-block.date {
  width: 118px;
  margin-left: auto;
}

.skeleton-pill {
  width: 78px;
  height: 20px;
  border-radius: 4px;
}

.skeleton-user {
  display: flex;
  align-items: center;
  gap: 7px;
}

.skeleton-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

@keyframes skeleton-shimmer {
  100% {
    transform: translateX(100%);
  }
}
</style>
