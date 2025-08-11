<template>
  <div>
    <div class="OIRankBox">
      <div class="OIRankTitle">
        <p>{{ $t("m.Rank") }}</p>
      </div>
      <div
        v-if="!myDataRank.length"
        style="text-align: center; font-size: 16px; padding-top: 50px"
      >
        {{ $t("m.No_Submissions") }}
      </div>
      <table v-else class="OIRankContent">
        <thead>
          <th style="width: 50px">{{ $t("m.Contest_Rank") }}</th>
          <th>{{ $t("m.Contest_Participant") }}</th>
          <th>{{ $t("m.Total_Score") }}</th>
          <th v-for="problem in contestProblems">
            <CustomTooltip :content="problem._id" placement="top">
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
        <tbody>
          <tr v-for="rank in myDataRank">
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
            <td>{{ rank.total_score }}</td>
            <td v-for="problem in contestProblems">
              <div v-if="rank[problem.id].isSet">
                {{ rank[problem.id].total_score }}
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
import { mapActions } from "vuex"
import api from "@oj/api"
import Pagination from "@oj/components/Pagination"
import ContestRankMixin from "./contestRankMixin"
import utils from "@/utils/utils"
import CustomTooltip from "@oj/components/CustomTooltip"

export default {
  name: "acm-contest-rank",
  components: {
    Pagination,
    CustomTooltip,
  },
  mixins: [ContestRankMixin],
  data() {
    return {
      total: 0,
      page: 1,
      contestID: "",
      myDataRank: [],
    }
  },
  mounted() {
    this.contestID = this.$route.params.contestID
    this.updateContestData()
  },
  methods: {
    ...mapActions(["getContestProblems"]),
    updateContestData() {
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
        })
        this.total = res.data.data.total
      })
    },
    addRankData(dataRank, problems) {
      problems.forEach((problem) => {
        dataRank.forEach((rank, idx) => {
          dataRank[idx][problem.id] = { isSet: false, problemId: problem._id }
        })
      })
      dataRank.forEach((rank, i) => {
        let info = rank.submission_info
        Object.keys(info).forEach((problemID) => {
          dataRank[i][problemID].total_score = info[problemID]
          dataRank[i][problemID].isSet = true
        })
        dataRank[i].idx = (this.page - 1) * this.limit + i + 1
      })
      this.myDataRank = dataRank
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
.OIRankBox {
  border: 1px solid #e9ece9;
  background: var(--box-background-color);
  padding: 15px 20px 40px;
  border-radius: 7px;
}
.OIRankTitle {
  position: absolute;
  display: flex;
  justify-content: space-between;
  align-items: center;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
}
.OIRankContent {
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
</style>
