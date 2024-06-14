<template>
  <main>
    <div class="title-wrapper">
      <span class="title">{{ $t("m.Contest_History") }}</span>
      <div style="display: flex; gap: 12px">
        <YearDropdown :year="this.query.year" @onYearChange="onYearChange" />
        <MonthDropdown
          :month="this.query.month"
          @onMonthChange="onMonthChange"
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
      <div v-if="display_contests.length === 0" class="session-not-exist">
        {{ $t("m.Ended_Contest_Not_Exist") }}
      </div>
      <table v-else class="contest-table">
        <thead>
          <th>{{ $t("m.Contest_ID") }}</th>
          <th style="padding-left: 50px; text-align: left">
            {{ $t("m.Contest_Title") }}
          </th>
          <th>{{ $t("m.Start_Date") }}</th>
          <th>{{ $t("m.State") }}</th>
          <th>{{ $t("m.Disclosure") }}</th>
          <th>{{ $t("m.Contest_Type") }}</th>
        </thead>
        <tbody>
          <tr
            v-for="contest in display_contests.slice(
              (page - 1) * limit,
              page * limit
            )"
          >
            <td>{{ contest.id }}</td>
            <td class="td-title" @click="goContest(contest)">
              {{ contest.title }}
            </td>
            <td style="font-size: 13px; width: 100">
              {{ contest.start_time | localtime("YYYY/MM/DD") }}
            </td>
            <td style="font-size: 13px; width: 100">
              {{ contest.end_time | localtime("YYYY/MM/DD") }}
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
      @on-change="updateContestData"
    ></Pagination>
  </main>
</template>

<script>
import api from "@oj/api";
import utils from "@/utils/utils";
import YearDropdown from "./components/YearDropdown";
import MonthDropdown from "./components/MonthDropdown";
import SearchKeyword from "./components/SearchKeyword";
import Pagination from "@/pages/oj/components/Pagination";
import { CONTEST_STATUS, CONTEST_TYPE, MONTH } from "@/utils/constants";

export default {
  name: "contest-history-list",
  components: {
    YearDropdown,
    MonthDropdown,
    SearchKeyword,
    Pagination,
  },
  data() {
    return {
      query: {
        year: "",
        month: "",
        keyword: "",
      },
      contests: [],
      display_contests: [],
      count: 0,
      total: 0,
      limit: 10,
      page: 1,
    };
  },
  beforeRouteEnter(to, from, next) {
    api.getContestList(0, 250).then(
      (res) => {
        next((vm) => {
          vm.contests = res.data.data.results;
          vm.display_contests = res.data.data.results.filter(
            (item) => item.status === CONTEST_STATUS.ENDED
          );
          vm.total = vm.display_contests.length;
        });
      },
      (res) => {
        next();
      }
    );
  },
  methods: {
    init() {
      let route = this.$route.query;
      this.query.year = route.year || "";
      this.query.month = route.month || "";
      this.query.keyword = route.keyword || "";
      this.getDisplayContestList();
    },
    getDisplayContestList() {
      // TODO api 호출하여 필터링하는 방식으로 바꾸기.
    },
    changeRoute() {
      let contests = this.contests.filter(
        (item) => item.status === CONTEST_STATUS.ENDED
      );
      if (this.query.year !== "") {
        contests = contests.filter((item) => {
          const date = new Date(item.start_time);
          return date.getFullYear() === parseInt(this.query.year);
        });
      }
      if (this.query.month !== "") {
        contests = contests.filter((item) => {
          const date = new Date(item.start_time);
          return date.getMonth() + 1 === MONTH[this.query.month].number;
        });
      }
      if (this.query.keyword !== "") {
        contests = contests.filter((item) => {
          const str = JSON.stringify(item);
          return str.includes(this.query.keyword);
        });
      }
      this.display_contests = contests;

      // TODO api 호출하여 필터링하는 방식으로 바뀌면 주석 풀기
      // let query = Object.assign({}, this.query);
      // this.$router.push({
      //   name: "contest-history-list",
      //   query: utils.filterEmptyValue(query),
      // });
    },
    onYearChange(year) {
      this.query.year = year;
      this.changeRoute();
    },
    onMonthChange(month) {
      this.query.month = month;
      this.changeRoute();
    },
    onKeywordChange(keyword) {
      this.query.keyword = keyword;
      this.changeRoute();
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
    font-size: 18px;
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
