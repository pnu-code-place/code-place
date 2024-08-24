<template>
  <main>
    <div class="session-title-wrapper">
      <h1 class="session-title main-title">{{ $t("m.Underway_Contest") }}</h1>
      <div style="display: flex; gap: 10px">
        <RuleTypeDropdown
          :rule_type="this.query.rule_type"
          @onRuleChange="onRuleChange"
        />
        <SearchKeyword @onKeywordChange="onKeywordChange" />
      </div>
    </div>
    <div v-if="underway_contests.length === 0" class="session-not-exist">
      {{ $t("m.Underway_Contest_Not_Exist") }}
    </div>
    <table v-else class="contest-table">
      <thead>
        <th>{{ $t("m.Contest_ID") }}</th>
        <th style="padding-left: 50px; text-align: left">
          {{ $t("m.Contest_Title_Description") }}
        </th>
        <th>{{ $t("m.Start_Date") }}</th>
        <th>{{ $t("m.State") }}</th>
        <th>{{ $t("m.Disclosure") }}</th>
        <th>{{ $t("m.Contest_Type") }}</th>
      </thead>
      <tbody>
        <tr v-for="contest in underway_contests">
          <td>{{ contest.id }}</td>
          <td class="td-title" @click.stop="goContest(contest)">
            <p class="contest-title">{{ contest.title }}</p>
            <div class="contest-description">
              <p v-html="contest.description"></p>
            </div>
          </td>
          <td style="font-size: 13px">
            <p>{{ contest.start_time | localtime("YYYY / MM / DD") }}</p>
            <p>{{ dateFormat(contest.start_time) }}</p>
          </td>
          <td>
            <div class="state-tag">
              {{ CONTEST_STATUS_REVERSE[contest.status].name }}
              <div :style="contestStateStyle(contest.status)"></div>
            </div>
          </td>
          <td style="width: 60px">
            {{ getContestDisclosure(contest) }}
          </td>
          <td style="width: 60px">
            <p class="rule-type-style">{{ contest.rule_type }}</p>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="session-title-wrapper">
      <h1 class="session-title">{{ $t("m.Ended_Contest") }}</h1>
      <span
        style="font-size: 15px; cursor: pointer"
        @click="goContestHistory()"
      >
        {{ $t("m.History_Of_Contest") }}
        <Icon type="arrow-right-b"></Icon>
      </span>
    </div>
    <div v-if="ended_contests.length === 0" class="session-not-exist">
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
        <th>{{ $t("m.Disclosure") }}</th>
        <th>{{ $t("m.Contest_Type") }}</th>
      </thead>
      <tbody>
        <tr v-for="contest in ended_contests">
          <td>{{ contest.id }}</td>
          <td class="td-title" @click.stop="goContest(contest)">
            {{ contest.title }}
          </td>
          <td style="font-size: 13px">
            {{ contest.start_time | localtime("YYYY/MM/DD") }}
          </td>
          <td style="font-size: 13px">
            {{ contest.end_time | localtime("YYYY/MM/DD") }}
          </td>
          <td style="width: 60px">
            {{ getContestDisclosure(contest) }}
          </td>
          <td style="width: 60px">
            <p class="rule-type-style">{{ contest.rule_type }}</p>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="session-title-wrapper">
      <h1 class="session-title">{{ $t("m.Not_Start_Contest") }}</h1>
    </div>
    <div v-if="not_start_contests.length === 0" class="session-not-exist">
      {{ $t("m.Not_Start_Contest_Not_Exist") }}
    </div>
    <table v-else class="contest-table">
      <thead>
        <th>{{ $t("m.Contest_ID") }}</th>
        <th style="padding-left: 50px; text-align: left">
          {{ $t("m.Contest_Title_Description") }}
        </th>
        <th>{{ $t("m.Start_Date") }}</th>
        <th>{{ $t("m.State") }}</th>
        <th>{{ $t("m.Disclosure") }}</th>
        <th>{{ $t("m.Contest_Type") }}</th>
      </thead>
      <tbody>
        <tr v-for="contest in not_start_contests">
          <td>{{ contest.id }}</td>
          <td class="td-title" @click.stop="goContest(contest)">
            <p class="contest-title">{{ contest.title }}</p>
            <div class="contest-description">
              <p v-html="contest.description"></p>
            </div>
          </td>
          <td style="font-size: 13px">
            <p>{{ contest.start_time | localtime("YYYY / MM / DD") }}</p>
            <p>{{ dateFormat(contest.start_time) }}</p>
          </td>
          <td>
            <div class="state-tag">
              {{ CONTEST_STATUS_REVERSE[contest.status].name }}
              <div :style="contestStateStyle(contest.status)"></div>
            </div>
          </td>
          <td style="width: 60px">
            {{ getContestDisclosure(contest) }}
          </td>
          <td style="width: 60px">
            <p class="rule-type-style">{{ contest.rule_type }}</p>
          </td>
        </tr>
      </tbody>
    </table>
  </main>
</template>

<script>
import api from "@oj/api";
import { mapGetters } from "vuex";
import utils from "@/utils/utils";
import time from "@/utils/time";
import {
  CONTEST_STATUS,
  CONTEST_STATUS_REVERSE,
  CONTEST_TYPE,
} from "@/utils/constants";
import SearchKeyword from "./components/SearchKeyword";
import RuleTypeDropdown from "./components/RuleTypeDropdown";

export default {
  name: "contest-list",
  components: {
    SearchKeyword,
    RuleTypeDropdown,
  },
  data() {
    return {
      query: {
        keyword: "",
        rule_type: "",
      },
      underway_contests: [],
      not_start_contests: [],
      ended_contests: [],
      CONTEST_STATUS_REVERSE: CONTEST_STATUS_REVERSE,
    };
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      api.getUnderwayContestList().then((res) => {
        vm.underway_contests = res.data.data;
      });
      api.getNotStartedContestList().then((res) => {
        vm.not_start_contests = res.data.data;
      });
      api.getContestHistoryList(0, 5).then((res) => {
        vm.ended_contests = res.data.data.results;
      });
    });
  },
  methods: {
    getUnderwayContestList() {
      api.getUnderwayContestList(this.query).then((res) => {
        this.underway_contests = res.data.data;
      });
    },
    onRuleChange(rule) {
      this.query.rule_type = rule;
      this.getUnderwayContestList();
    },
    onKeywordChange(keyword) {
      this.query.keyword = keyword;
      this.getUnderwayContestList();
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
    goContestHistory() {
      this.$router.push({
        name: "contest-history-list",
      });
    },
    dateFormat(date) {
      const formattedDate = new Date(date);

      const hour = formattedDate.getHours();
      const min = formattedDate.getMinutes();
      const sec = formattedDate.getSeconds();

      let result = "";
      if (hour > 12) result = "오후 " + (hour - 12) + "시 ";
      else result = "오전 " + hour + "시 ";

      if (min !== 0) result = result + min + "분 ";
      if (sec !== 0) result = result + sec + "초";

      return result;
    },
    contestStateStyle(state) {
      return {
        width: "16px",
        height: "16px",
        "border-radius": "100%",
        "background-color": CONTEST_STATUS_REVERSE[state].color,
      };
    },
    getContestDisclosure(contest) {
      return contest.contest_type === "Public"
        ? this.$i18n.t("m.Public")
        : this.$i18n.t("m.Private");
    },
  },
  computed: {
    ...mapGetters(["isAuthenticated", "user"]),
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
  width: var(--global-width);

  .session-not-exist {
    width: 100%;
    height: 120px;
    margin-bottom: 20px;
    line-height: 120px;
    text-align: center;
    font-size: 18px;
    font-weight: 700;
    background-color: white;
    border: 1px solid var(--container-border-color);
    border-radius: var(--container-border-radius);
  }

  .session-title-wrapper {
    margin: 0 4px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .session-title {
    font-weight: 700;
  }
  .dropdown {
    color: var(--container-font-color);
    font-size: 14px;
    span {
      width: 100px;
      height: 35px;
      padding: 5px 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-weight: 700;
      cursor: default;
      background-color: white;
      border: 1px solid var(--container-border-color);
      border-radius: var(--container-border-radius);
    }
  }

  .contest-table {
    margin-bottom: 20px;
    border: 1px solid var(--container-border-color);
    border-radius: var(--container-border-radius);
    background-color: white;
    text-align: center;
    th {
      padding: 10px 0px;
      font-size: 16px;
      font-weight: 600;
      color: var(--container-comment-color);
    }
    td {
      cursor: default;
      width: 80px;
      padding: 10px;
      font-size: 15px;
      border-top: 1px solid var(--container-border-color);
      .state-tag {
        display: flex;
        gap: 10px;
        align-items: center;
        justify-content: center;
      }
      .rule-type-style {
        width: 60px;
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
      .contest-title {
        font-size: 18px;
        font-weight: 600;
      }
      .contest-description {
        font-size: 14px;
        font-weight: 400;
        text-overflow: ellipsis;
        overflow: hidden;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 1;
      }
    }
  }
}
</style>
