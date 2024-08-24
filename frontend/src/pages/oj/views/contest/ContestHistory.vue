<template>
  <main>
    <div class="title-wrapper">
      <h1 class="title">{{ $t("m.Contest_History") }}</h1>
      <div style="display: flex; gap: 12px">
        <YearDropdown :year="this.query.year" @onYearChange="onYearChange" />
        <MonthDropdown
          :month="this.query.month"
          @onMonthChange="onMonthChange"
        />
        <RuleTypeDropdown
          :rule_type="this.query.rule_type"
          @onRuleChange="onRuleChange"
        />
        <SearchKeyword @onKeywordChange="onKeywordChange" />
      </div>
    </div>
    <div
      style="
        width: 100%;
        padding: 0 20px;
        border: 1px solid var(--container-border-color);
        border-radius: var(--container-border-radius);
        background-color: var(--bg-color);
      "
    >
      <div v-if="contests.length === 0" class="session-not-exist">
        {{ $t("m.Ended_Contest_Not_Exist") }}
      </div>
      <table v-else class="contest-table">
        <thead>
          <th>{{ $t("m.Contest_ID") }}</th>
          <th style="padding-left: 50px; text-align: left">
            {{ $t("m.Contest_Title") }}
          </th>
          <th>{{ $t("m.Start_Date") }}</th>
          <th>{{ $t("m.End_Date") }}</th>
          <th>{{ $t("m.State") }}</th>
          <th>{{ $t("m.Disclosure") }}</th>
          <th>{{ $t("m.Contest_Type") }}</th>
        </thead>
        <tbody>
          <tr v-for="contest in contests">
            <td>{{ contest.id }}</td>
            <td class="td-title" @click="goContest(contest)">
              {{ contest.title }}
            </td>
            <td style="font-size: 13px; width: 100px">
              {{ contest.start_time | localtime("YYYY/MM/DD") }}
            </td>
            <td style="font-size: 13px; width: 100px">
              {{ contest.end_time | localtime("YYYY/MM/DD") }}
            </td>
            <td>
              <div class="state-tag">
                {{ CONTEST_STATUS_REVERSE[contest.status].name }}
                <div :style="contestStateStyle(contest.status)"></div>
              </div>
            </td>
            <td>
              {{ getContestDisclosure(contest) }}
            </td>
            <td>
              <p class="rule-type-style">{{ contest.rule_type }}</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pagination
      :total="total"
      :page-size="limit"
      :current.sync="page"
      @on-change="getContestHistoryList"
    ></Pagination>
  </main>
</template>

<script>
import api from "@oj/api";
import utils from "@/utils/utils";
import YearDropdown from "./components/YearDropdown";
import MonthDropdown from "./components/MonthDropdown";
import RuleTypeDropdown from "./components/RuleTypeDropdown";
import SearchKeyword from "./components/SearchKeyword";
import Pagination from "@/pages/oj/components/Pagination";
import { CONTEST_STATUS, CONTEST_TYPE, MONTH } from "@/utils/constants";
import {CONTEST_STATUS_REVERSE} from "../../../../utils/constants";

export default {
  name: "contest-history-list",
  computed: {
    CONTEST_STATUS_REVERSE() {
      return CONTEST_STATUS_REVERSE
    }
  },
  components: {
    YearDropdown,
    MonthDropdown,
    RuleTypeDropdown,
    SearchKeyword,
    Pagination,
  },
  data() {
    return {
      query: {
        year: "",
        month: "",
        rule_type: "",
        keyword: "",
      },
      contests: [],
      count: 0,
      total: 0,
      limit: 10,
      page: 1,
    };
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      api
        .getContestHistoryList((vm.page - 1) * vm.limit, vm.limit)
        .then((res) => {
          vm.contests = res.data.data.results;
          vm.total = res.data.data.total;
        });
    });
  },
  methods: {
    getContestHistoryList() {
      const { month, ...rest } = this.query;
      const query = {
        ...rest,
        month: month === "" ? month : MONTH[month].number,
      };
      api
        .getContestHistoryList((this.page - 1) * this.limit, this.limit, query)
        .then((res) => {
          this.contests = res.data.data.results;
          this.total = res.data.data.total;
        });
    },
    contestStateStyle(state) {
      return {
        width: "16px",
        height: "16px",
        "border-radius": "100%",
        "background-color": CONTEST_STATUS_REVERSE[state].color,
      };
    },
    onYearChange(year) {
      this.page = 1;
      this.query.year = year;
      this.getContestHistoryList();
    },
    onMonthChange(month) {
      this.page = 1;
      this.query.month = month;
      this.getContestHistoryList();
    },
    onRuleChange(rule) {
      this.page = 1;
      this.query.rule_type = rule;
      this.getContestHistoryList();
    },
    onKeywordChange(keyword) {
      this.page = 1;
      this.query.keyword = keyword;
      this.getContestHistoryList();
    },
    getContestDisclosure(contest) {
      return contest.contest_type === "Public"
        ? this.$i18n.t("m.Public")
        : this.$i18n.t("m.Private");
    },
    goContest(contest) {
      if (
        contest.contest_type !== CONTEST_TYPE.PUBLIC &&
        !this.isAuthenticated
      ) {
        this.$error(this.$i18n.t("m.Please_login_first"));
        this.$store.dispatch("changeModalStatus", { visible: true });
      } else {
        this.$router.push({
          name: "contest-overview",
          params: { contestID: contest.id },
        });
      }
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

<style lang="less" scoped>
main {
  width: 1200px;

  .title-wrapper {
    margin: 20px 4px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .title {
    font-weight: 700;
  }

  .session-not-exist {
    height: 120px;
    line-height: 120px;
    text-align: center;
    font-size: 18px;
    font-weight: 700;
  }

  .contest-table {
    text-align: center;
    th {
      padding: 10px 0px;
      font-size: 16px;
      font-weight: 600;
      color: var(--container-comment-color);
    }
    td {
      cursor: default;
      width: 60px;
      padding: 10px;
      font-size: 15px;
      color: black;
      border-top: 1px solid var(--container-border-color);
      .state-tag {
        display: flex;
        gap: 10px;
        align-items: center;
        justify-content: center;
      }
      .rule-type-style {
        width: 50px;
        margin: auto;
        padding: 4px;
        border: 1px solid var(--rule-type-border-color);
        border-radius: var(--container-border-radius);
      }
    }
    .td-title {
      cursor: pointer;
      width: 350px;
      padding-left: 50px;
      text-align: left;
    }
  }
}
</style>
