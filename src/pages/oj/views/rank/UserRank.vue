<script>

import TopRanker from "./TopRanker.vue";
import UserList from "./UserRankList.vue";
import Pagination from "../../components/Pagination.vue";
import SurgeRankList from "./SoaringRank.vue";
import MajorRankList from "./MajorRank.vue";
import {RULE_TYPE} from "../../../../utils/constants";
import api from "../../api";

export default {
  name: 'UserRank',
  components: {
    Pagination, UserList, SurgeRankList, MajorRankList, TopRanker
  },
  data() {
    return {
      page: 1,
      limit: 30,
      total: 0,
      loadingTable: false,
      dataRank: [],
      topUsers: {
        '1': {
          username: 'username',
          avatar: 'https://cdn-icons-png.flaticon.com/512/473/473406.png',
          score: 0,
          solved: 0,
          accuracy: 0.0
        },
        '2': {
          username: 'username',
          avatar: 'https://cdn-icons-png.flaticon.com/512/473/473406.png',
          score: 0,
          solved: 0,
          accuracy: 0.0
        },
        '3': {
          username: 'username',
          avatar: 'https://cdn-icons-png.flaticon.com/512/473/473406.png',
          score: 0,
          solved: 0,
          accuracy: 0.0
        }
      }
    }
  },
  mounted() {
    this.getRankData(1)
  },
  methods: {
    getRankData(page) {
      let offset = (page - 1) * this.limit + 3
      console.log("offset", offset, this.limit, RULE_TYPE.ACM)
      this.loadingTable = true
      api.getUserRank(offset, this.limit, RULE_TYPE.ACM).then(res => {
        this.loadingTable = false
        this.total = res.data.data.total
        this.dataRank = res.data.data.results
      }).catch(() => {
        this.loadingTable = false
      })
    },
    changeCharts(rankData) {
      let [usernames, acData, totalData] = [[], [], []]
      rankData.forEach(ele => {
        usernames.push(ele.user.username)
        acData.push(ele.accepted_number)
        totalData.push(ele.submission_number)
      })
      this.options.xAxis[0].data = usernames
      this.options.series[0].data = acData
      this.options.series[1].data = totalData
    }
  },
  getTopUsers() {
    api.getUserRank(0, 3).then(res => {
      console.log("res", res.data.data.results)
      this.topUsers = res.data.data.results
    })
  }
}
</script>

<template>
  <div class="contents">
    <div class="top-users">
      <div class="top-user sub-top">
        <h2>{{ $t('m.TOP_2') }}</h2>
        <TopRanker :rank=2></TopRanker>
      </div>
      <div class="top-user">
        <h2>{{ $t('m.TOP_1') }}</h2>
        <TopRanker :rank=1></TopRanker>
      </div>
      <div class="top-user sub-top">
        <h2>{{ $t('m.TOP_3') }}</h2>
        <TopRanker :rank=3></TopRanker>
      </div>
    </div>
    <UserList :userList="dataRank" :is-loading="loadingTable" :limit="limit"/>
    <Pagination :total="total" :page-size.sync="limit" :current.sync="page"
                @on-change="getRankData" show-sizer
                @on-page-size-change="getRankData(1)"></Pagination>
  </div>
</template>

<style scoped lang="less">
.contents {
  width: 100%;
  background-color: var(--box-background-color);
  .top-users {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
    gap : 30px;

    .sub-top {
      margin-top: 60px;
    }

    .top-user {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
  }
}
</style>
