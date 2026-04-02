<template>
  <div>
    <div class="ACMRankBox">
      <div class="ACMRankTitle">
        <p>{{ $t("m.Rank") }}</p>
      </div>
      <div
        v-if="!loadingRank && !dataRank.length"
        style="text-align: center; font-size: 16px; padding-top: 50px"
      >
        {{ $t("m.No_Submissions") }}
      </div>
      <table v-else class="ACMRankContent">
        <thead>
          <th style="min-width: 50px">{{ $t("m.Contest_Rank") }}</th>
          <th>{{ $t("m.Contest_Participant") }}</th>
          <th>
            {{ $t("m.Solved_Problems") }}
          </th>
          <th v-for="problem in contestProblems">
            <CustomTooltip :content="problem.title" placement="top">
              <a
                style="
                  color: #6ccbff;
                  display: block;
                  max-width: 100px;
                  overflow: hidden;
                  text-overflow: ellipsis;
                  white-space: nowrap;
                "
                @click="goProblemPage(problem._id)"
              >
                {{ problem._id }}
              </a>
            </CustomTooltip>
          </th>
        </thead>
        <tbody v-if="loadingRank">
          <tr
            v-for="row in 5"
            :key="`acm-rank-skeleton-${row}`"
          >
            <td><div class="rank-skeleton-box rank-skeleton-box-sm"><SkeletonBox /></div></td>
            <td>
              <div class="rank-skeleton-user">
                <div class="rank-skeleton-avatar"><SkeletonBox /></div>
                <div class="rank-skeleton-box rank-skeleton-box-md"><SkeletonBox /></div>
              </div>
            </td>
            <td><div class="rank-skeleton-box rank-skeleton-box-sm"><SkeletonBox /></div></td>
            <td
              v-for="problem in skeletonProblemCount"
              :key="`acm-rank-skeleton-problem-${row}-${problem}`"
            >
              <div class="rank-skeleton-box rank-skeleton-box-sm"><SkeletonBox /></div>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr v-for="rank in dataRank">
            <td>{{ rank.idx }}</td>
            <td>
              <a
                @click="goUserPage(rank.user.username)"
                style="display: flex; align-items: center; gap: 10px"
              >
                <img
                  :src="rank.user.avatar"
                  style="
                    width: 36px;
                    height: 36px;
                    border-radius: 100%;
                    border: 2px solid #eaeefb;
                  "
                />
                {{ rank.user.username }}
              </a>
            </td>
            <td>
              <span class="accepted-count-value">{{ rank.accepted_number }}</span>
            </td>
            <td v-for="problem in contestProblems">
              <CustomTooltip
                v-if="rank[problem.id].status === 'ac'"
                :content="`${rank[problem.id].attempt_count}회 시도`"
                placement="top"
              >
                <div class="problem-status ac">
                  <span class="problem-status-date">
                    {{ rank[problem.id].ac_time | localtime("MM/DD") }}
                  </span>
                  <span class="problem-status-time">
                    {{ rank[problem.id].ac_time | localtime("HH:mm:ss") }}
                  </span>
                </div>
              </CustomTooltip>
              <div
                v-else-if="rank[problem.id].status"
                class="problem-status"
                :class="rank[problem.id].status"
              >
                <span class="problem-status-label">WA</span>
                <span class="problem-status-time">
                  {{ rank[problem.id].error_number || "-" }}
                </span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pagination
      :total="total"
      :page-size.sync="limit"
      :current.sync="page"
      @on-change="updateContestData"
      @on-page-size-change="updateContestData()"
      show-sizer
    ></Pagination>
  </div>
</template>

<script>
import moment from "moment"
import { mapActions } from "vuex"
import api from "@oj/api"
import Pagination from "@oj/components/Pagination"
import ContestRankMixin from "./contestRankMixin"
import time from "@/utils/time"
import utils from "@/utils/utils"
import CustomTooltip from "@oj/components/CustomTooltip"
import SkeletonBox from "@oj/components/SkeletonBox"

export default {
  name: "acm-contest-rank",
  components: {
    Pagination,
    CustomTooltip,
    SkeletonBox,
  },
  mixins: [ContestRankMixin],
  data() {
    return {
      total: 0,
      page: 1,
      contestID: "",
      dataRank: [],
      loadingRank: false,
    }
  },
  computed: {
    skeletonProblemCount() {
      return this.contestProblems.length || 4
    },
  },
  mounted() {
    this.contestID = this.$route.params.contestID
    this.updateContestData()
  },
  methods: {
    ...mapActions(["getContestProblems"]),
    updateContestData() {
      this.loadingRank = true
      let params = {
        offset: (this.page - 1) * this.limit,
        limit: this.limit,
        contest_id: this.$route.params.contestID,
        force_refresh: this.forceUpdate ? "1" : "0",
      }
      api.getContestRank(params).then((res) => {
        const data = res.data.data.results
        let dataRank = JSON.parse(JSON.stringify(data))

        this.getContestProblems().then((res) => {
          this.addRankData(dataRank, res.data.data)
          this.loadingRank = false
        })
        this.total = res.data.data.total
      }).catch(() => {
        this.loadingRank = false
      })
    },
    addRankData(dataRank, problems) {
      problems.forEach((problem) => {
        dataRank.forEach((rank, idx) => {
          dataRank[idx][problem.id] = {
            status: "",
            error_number: 0,
            problemId: problem._id,
          }
        })
      })
      dataRank.forEach((rank, i) => {
        let info = rank.submission_info
        Object.keys(info).forEach((problemID) => {
          if (!dataRank[i][problemID]) return
          dataRank[i][problemID].error_number = info[problemID].error_number || 0
          if (info[problemID].is_ac) {
            dataRank[i][problemID].ac_time = moment(this.contest.start_time)
              .add(info[problemID].ac_time, "seconds")
              .format()
            dataRank[i][problemID].attempt_count =
              dataRank[i][problemID].error_number + 1
            dataRank[i][problemID].status = "ac"
          } else {
            dataRank[i][problemID].status = "wa"
          }
        })
        dataRank[i].idx = (this.page - 1) * this.limit + i + 1
      })
      this.dataRank = dataRank
    },
    goUserPage(username) {
      this.$router.push({
        name: "user-dashboard",
        params: { username: username },
      })
    },
    goProblemPage(problemId) {
      this.$router.push({
        name: "contest-problem-details",
        params: {
          contestID: this.contestID,
          problemID: problemId,
        },
      })
    },
  },
}
</script>

<style scoped lang="less">
.ACMRankBox {
  border: 1px solid #e9ece9;
  background: var(--box-background-color);
  padding: 15px 20px 40px;
  border-radius: 7px;
}
.ACMRankTitle {
  position: absolute;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
}
.ACMRankContent {
  text-align: center;
  display: block;
  padding-top: 50px;
  max-width: 928px;
  overflow-y: visible;
  overflow-x: scroll;
  white-space: nowrap;
  th {
    color: #7e7e7e;
    font-size: 1.3em;
    padding: 0px 7.5px 10px 7.5px;
  }
  td {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    padding: 10px 0px;
  }
  tr {
    font-size: 1.05em;
  }
}

.problem-status {
  display: inline-flex;
  min-width: 58px;
  flex-direction: column;
  align-items: center;
  border-radius: 8px;
  padding: 6px 8px;
  font-weight: 700;
  line-height: 1.2;
}

.problem-status-date,
.problem-status-label {
  font-size: 11px;
}

.problem-status-time {
  font-size: 12px;
  margin-top: 2px;
}

.problem-status.ac {
  background: #e8f7ee;
  color: #1f8f52;
}

.problem-status.wa {
  background: #f3f4f7;
  color: #5b6472;
}

.accepted-count-value {
  font-size: 20px;
  font-weight: 600;
  line-height: 1;
  color: #2f3c57;
}

.rank-skeleton-user {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}

.rank-skeleton-avatar {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.rank-skeleton-avatar /deep/ .skeleton {
  border-radius: 50%;
}

.rank-skeleton-user-text {
  width: 120px;
  height: 18px;
}

.rank-skeleton-box {
  height: 18px;
  margin: 0 auto;
}

.rank-skeleton-box-sm {
  width: 42px;
}

.rank-skeleton-box-md {
  width: 120px;
}
</style>
