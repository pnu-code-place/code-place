<template>
  <div class="view">
    <section>
      <div class="section-title">
        {{ $t("m.Contest_Submission_Title") }}
        <el-button @click.native="downloadRankCSV()">
          대회 결과표 다운로드
        </el-button>
      </div>
      <div class="section-body">
        <div
          v-if="submissions.length === 0"
          style="text-align: center; font-size: 1rem"
        >
          {{ $t("m.No_Submissions") }}
        </div>
        <div v-else>
          <table>
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
                    {{ submission.create_time | localtime("YYYY-M-D") }}
                  </span>
                  <span>
                    {{ submission.create_time | localtime("HH:mm:SS") }}
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
                  {{
                    submissionTimeFormat(submission.statistic_info.time_cost)
                  }}
                </td>
                <td>
                  {{
                    submissionMemoryFormat(
                      submission.statistic_info.memory_cost
                    )
                  }}
                </td>
                <td>{{ submission.language }}</td>
                <td>{{ submission.username }}</td>
              </tr>
            </tbody>
          </table>
          <Pagination
            :total="totalSubmission"
            :page-size="limit"
            :current.sync="pageSubmission"
            @on-change="changeRoute"
          ></Pagination>
        </div>
      </div>
    </section>
    <section>
      <div class="section-title">
        {{ $t("m.Contest_Submission_User_Title") }}
      </div>
      <div class="section-body">
        <div
          v-if="participants.length === 0"
          style="text-align: center; font-size: 1rem"
        >
          {{ $t("m.Comment_No_Participant") }}
        </div>
        <div v-else>
          <table>
            <thead>
              <th>{{ $t("m.ID") }}</th>
              <th>{{ $t("m.Avatar") }}</th>
              <th>{{ $t("m.Username") }}</th>
              <th>{{ $t("m.School_Email") }}</th>
              <th>{{ $t("m.College") }}</th>
              <th>{{ $t("m.Major") }}</th>
            </thead>
            <tbody>
              <tr v-for="(participant, idx) in participants">
                <td>{{ idx + 1 }}</td>
                <td><img class="avatar" :src="participant.avatar" /></td>
                <td>{{ participant.username }}</td>
                <td>{{ participant.email }}</td>
                <td>{{ participant.school }}</td>
                <td>{{ participant.major }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
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
      submissions: [],
      participants: [],
      totalSubmission: 0,
      totalParticipant: 0,
      limit: 5,
      pageSubmission: 1,
      pageParticipant: 0,
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
      this.pageSubmission = parseInt(query.pageSubmission) || 1;
      this.pageParticipant = parseInt(query.pageParticipant) || 1;
      if (this.pageSubmission < 1) this.pageSubmission = 1;
      if (this.pageParticipant < 1) this.pageParticipant = 1;
      this.getSubmissions();
      this.getParticipants();
    },
    changeRoute() {
      let query = {
        pageSubmission: this.pageSubmission,
      };
      this.$router.push({
        name: "contest-submission",
        params: { contestId: this.contestID },
        query: utils.filterEmptyValue(query),
      });
    },
    buildQuery() {
      return {
        page: this.pageSubmission,
        contest_id: this.contestID,
      };
    },
    getSubmissions() {
      let params = this.buildQuery();
      let offset = (this.pageSubmission - 1) * this.limit;
      api.getContestSubmissionList(offset, this.limit, params).then((res) => {
        let data = res.data.data;
        this.submissions = data.results;
        this.totalSubmission = data.total;
      });
    },
    getParticipants() {
      api.getContestParticipantList(this.contestID).then((res) => {
        this.participants = res.data.data;
      });
    },
    submissionMemoryFormat(memory) {
      return utils.submissionMemoryFormat(memory);
    },
    submissionTimeFormat(time) {
      return utils.submissionTimeFormat(time);
    },
    downloadRankCSV() {
      utils.downloadFile(
        `admin/contest_rank?download_csv=1&contest_id=${this.contestID}`
      );
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
section {
  width: 100%;
  padding: 15px;
  .section-title {
    font-weight: 300;
    font-size: 1.2rem;
    padding: 10px 15px;
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid rgba(0, 0, 0, 0.15);
  }
  .section-body {
    margin-top: 5px;
    padding: 10px;
  }
}
table {
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

.avatar {
  width: 30px;
  border-radius: 50%;
  box-shadow: 0px 0px 1px 0px;
}
</style>
