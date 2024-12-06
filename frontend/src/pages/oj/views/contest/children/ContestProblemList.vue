<template>
  <div class="problemBox">
    <div class="problemTitle">
      <div style="display: flex; align-items: center; gap: 10px">
        <p>{{ $t("m.Problems_List") }}</p>
        <CustomTooltip
          v-if="contestRuleType === 'ACM'"
          :content="$t('m.ACM_Contest_Information')"
          placement="right"
        >
          <Icon
            type="ios-information-outline"
            style="font-size: 16px; font-weight: 900"
          ></Icon>
        </CustomTooltip>
      </div>
      <Input
        style="width: 200px"
        v-model="keyword"
        @on-enter="filterByKeyword"
        @on-click="filterByKeyword"
        :placeholder="$t('m.Search_Problem')"
        icon="ios-search-strong"
      />
    </div>
    <div
      v-if="problems.length === 0"
      style="text-align: center; font-size: 16px"
    >
      {{ $t("m.No_Problems") }}
    </div>
    <table
      v-else-if="contestRuleType == 'ACM' || OIContestRealTimePermission"
      class="problemTable"
    >
      <thead>
        <th>
          {{ $t("m.Th_Problem_Id") }}
        </th>
        <th class="TableTitle">{{ $t("m.Th_Problem_Title") }}</th>
        <th>{{ $t("m.Th_Problem_Difficulty") }}</th>
        <th v-if="contestRuleType !== 'ACM'">
          {{ $t("m.Th_Problem_Total_Score") }}
        </th>
        <th>{{ $t("m.Th_Problem_AC_Rate") }}</th>
        <th>{{ $t("m.Th_Problem_Submission_State") }}</th>
      </thead>
      <tbody>
        <tr v-for="problem in problems" @click="goContestProblem(problem._id)">
          <td style="white-space: nowrap; text-align: left">
            {{ problem._id }}
          </td>
          <td class="TableTitle">
            {{ problem.title }}
          </td>
          <td>{{ DIFFICULTY_MAP[problem.difficulty].value }}</td>
          <td v-if="contestRuleType !== 'ACM'">{{ problem.total_score }}</td>
          <td>
            {{ getACRate(problem.accepted_number, problem.submission_number) }}
          </td>
          <td v-html="getSubmissionState(problem.mine_submission_state)"></td>
        </tr>
      </tbody>
    </table>
    <table v-else class="problemTable">
      <thead>
        <th>{{ $t("m.Th_Problem_Id") }}</th>
        <th class="TableTitle">{{ $t("m.Th_Problem_Title") }}</th>
        <th>{{ $t("m.Th_Problem_Submission_State") }}</th>
      </thead>
      <tbody>
        <tr v-for="problem in problems" @click="goContestProblem(problem._id)">
          <td>{{ problem._id }}</td>
          <td class="TableTitle">
            {{ problem.title }}
          </td>
          <td v-html="getSubmissionState(problem.mine_submission_state)"></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import { ProblemMixin } from "@oj/components/mixins";
import { DIFFICULTY_MAP, FIELD_MAP } from "../../../../../utils/constants";
import FieldCategoryBox from "../../../components/FieldCategoryBox.vue";
import CustomTooltip from "@oj/components/CustomTooltip";

export default {
  name: "ContestProblemList",
  components: { FieldCategoryBox, CustomTooltip },
  mixins: [ProblemMixin],
  data() {
    return {
      keyword: "",
    };
  },
  mounted() {
    this.getContestProblems();
  },
  methods: {
    filterByKeyword() {
      this.getContestProblems();
    },
    getContestProblems() {
      this.$store.dispatch("getContestProblems", this.keyword).then((res) => {
        if (this.isAuthenticated) {
          if (this.contestRuleType === "ACM") {
            this.addStatusColumn(this.ACMTableColumns, res.data.data);
          } else if (this.OIContestRealTimePermission) {
            this.addStatusColumn(this.ACMTableColumns, res.data.data);
          }
        }
      });
    },
    goContestProblem(id) {
      this.$router.push({
        name: "contest-problem-details",
        params: {
          contestID: this.$route.params.contestID,
          problemID: id,
        },
      });
    },
    getSubmissionState(state) {
      switch (state) {
        case "Accepted":
          return '<i class="far fa-check-circle" style="color: #63e6be"></i>';
        case "Partially_Accepted":
          return ' <i class="fas fa-adjust" style="color: #b197fc"></i>';
        case "Failed":
          return '<i class="far fa-times-circle" style="color: #e22828"></i>';
        case null:
          return '<i class="far fa-dot-circle" style="color: #bababa"></i>';
        default:
          return null;
      }
    },
  },
  computed: {
    ...mapState({
      problems: (state) => state.contest.contestProblems,
    }),
    ...mapGetters([
      "isAuthenticated",
      "contestRuleType",
      "OIContestRealTimePermission",
    ]),
    DIFFICULTY_MAP() {
      return DIFFICULTY_MAP;
    },
    FIELD_MAP() {
      return FIELD_MAP;
    },
  },
};
</script>

<style scoped lang="less">
.problemBox {
  border: 1px solid #e9ece9;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--box-background-color);
  padding: 15px 20px;
  border-radius: 7px;
}
.problemTitle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
}
.problemTable {
  text-align: center;
  th {
    color: #7e7e7e;
    font-size: 1.3em;
    padding: 10px;
  }
  td {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    padding: 10px;
  }
  tr {
    font-size: 1.05em;
    cursor: pointer;
    td:first-child {
      font-size: 1.2em;
    }
  }
  .TableTitle {
    font-size: 1.3em;
    width: auto;
    text-align: left;
    font-weight: bold;
  }
}
</style>
