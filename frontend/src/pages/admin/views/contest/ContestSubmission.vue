<template>
  <div class="view">
    <Panel :title="$t('m.Contest_Submission_Title')">
      <div
        v-if="submissions.length === 0"
        style="text-align: center; font-size: 1rem"
      >
        {{ $t("m.No_Submissions") }}
      </div>
      <div v-else>
        <table class="submissionContent">
          <thead>
            <th>{{ $t("m.When") }}</th>
            <th>{{ $t("m.Status") }}</th>
            <th>{{ $t("m.Problem") }}</th>
            <th>{{ $t("m.Time") }}</th>
            <th>{{ $t("m.Memory") }}</th>
            <th>{{ $t("m.Language") }}</th>
            <th>{{ $t("m.Submission_Table_Author") }}</th>
          </thead>
          <tbody>
            <tr v-for="submission in submissions">
              <td
                style="
                  cursor: default;
                  display: flex;
                  flex-direction: column;
                  justify-content: center;
                "
              >
                <span>
                  {{ submission.time_cost | localtime("YYYY-M-D") }}
                </span>
                <span>
                  {{ submission.time_cost | localtime("HH:mm:SS") }}
                </span>
              </td>
              <td>
                <Tag
                  style="cursor: default"
                  :color="JUDGE_STATUS[submission.result].color"
                  >{{ JUDGE_STATUS[submission.result].name }}</Tag
                >
              </td>
              <td>{{ submission.problem }}</td>
              <td>
                {{ submissionTimeFormat(submission.statistic_info.time_cost) }}
              </td>
              <td>
                {{
                  submissionMemoryFormat(submission.statistic_info.memory_cost)
                }}
              </td>
              <td>{{ submission.language }}</td>
              <td>{{ submission.username }}</td>
            </tr>
          </tbody>
        </table>
        <Pagination
          :total="total"
          :page-size="limit"
          :current.sync="page"
        ></Pagination>
      </div>
    </Panel>
    <Panel :title="$t('m.Contest_Submission_User_Title')"> </Panel>
  </div>
</template>

<script>
import api from "../../api.js";

import { JUDGE_STATUS, USER_TYPE } from "@/utils/constants";
import utils from "@/utils/utils";
import time from "@/utils/time";
import Pagination from "@/pages/admin/components/Pagination";

export default {
  name: "ContestSubmission",
  components: {
    Pagination,
  },
  data() {
    return {
      loadingTable: false,
      submissions: [],
      total: 0,
      limit: 5,
      page: 1,
      contestID: 0,
      JUDGE_STATUS: "",
      rejudge_column: false,
    };
  },
  mounted() {
    this.init();
    this.JUDGE_STATUS = Object.assign({}, JUDGE_STATUS);
  },
  methods: {
    init() {
      this.contestID = this.$route.params.contestId;
      let query = this.$route.query;
      this.page = parseInt(query.page) || 1;
      if (this.page < 1) {
        this.page = 1;
      }
      this.getSubmissions();
    },
    buildQuery() {
      return {
        page: this.page,
        contest_id: this.contestID,
      };
    },
    getSubmissions() {
      let params = this.buildQuery();
      let offset = (this.page - 1) * this.limit;
      this.loadingTable = true;
      api
        .getContestSubmissionList(offset, this.limit, params)
        .then((res) => {
          let data = res.data.data;
          for (let v of data.results) {
            v.loading = false;
          }
          this.loadingTable = false;
          this.submissions = data.results;
          this.total = data.total;
        })
        .catch(() => {
          this.loadingTable = false;
        });
    },
    submissionMemoryFormat(memory) {
      return utils.submissionMemoryFormat(memory);
    },
    submissionTimeFormat(time) {
      return utils.submissionTimeFormat(time);
    },
  },
  watch: {
    $route(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init();
      }
    },
  },
};
</script>

<style scoped lang="less">
.submissionContent {
  width: 100%;
  text-align: center;
  th {
    width: 80px;
    color: #7e7e7e;
    font-size: 1.1em;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  }
  td {
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    padding: 10px 0px;
    cursor: default;
  }
  tr {
    font-size: 1.05em;
  }
}
</style>
