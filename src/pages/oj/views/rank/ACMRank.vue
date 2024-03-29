<template>
  <div class="acm-rank">
    <div class="acm-rank__contents">
      <div class="acm-rank__left rank-container">
        <div class="title">
          <h1>{{ $t('m.Top_Users') }}</h1>
<!--          <Button type="dashed" @click="getRankData()">{{ $t('m.My_Ranking')}}</Button>-->
        </div>
        <div class="top-users">
          <div class="top2 top-user">
            <h2>{{ $t('m.TOP_2') }}</h2>
            <TopRanker :rank=2></TopRanker>
          </div>
          <div class="top1 top-user">
            <h2>{{ $t('m.TOP_1') }}</h2>
            <TopRanker :rank=1></TopRanker>
          </div>
          <div class="top3 top-user">
            <h2>{{ $t('m.TOP_3') }}</h2>
            <TopRanker :rank=3></TopRanker>
          </div>
        </div>
        <UserList :userList="dataRank" :is-loading="loadingTable" :limit="limit"/>
        <Pagination :total="total" :page-size.sync="limit" :current.sync="page"
                    @on-change="getRankData" show-sizer
                    @on-page-size-change="getRankData(1)"></Pagination>
      </div>
      <div class="acm-rank__right">
        <div class="surge-user rank-container">
          <h2>{{ $t('m.Today_Surge_User') }}</h2>
          <SurgeRankList></SurgeRankList>
        </div>
        <div class="major-rank rank-container">
          <h2>{{ $t('m.Major_Rank') }}</h2>
          <MajorRankList></MajorRankList>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'
import Pagination from '@oj/components/Pagination'
import {RULE_TYPE} from '@/utils/constants'
import UserList from "./userRankList/UserRankList.vue";
import SurgeRankList from "./userRankList/SurgeRankList.vue";
import MajorRankList from "./userRankList/MajorRankList.vue";
import TopRanker from "./TopRanker.vue";

export default {
  name: 'acm-rank',
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
      // columns: [
      //   {
      //     align: 'center',
      //     width: 60,
      //     render: (h, params) => {
      //       return h('span', {}, params.index + (this.page - 1) * this.limit + 1)
      //     }
      //   },
      //   {
      //     title: this.$i18n.t('m.User_User'),
      //     align: 'center',
      //     render: (h, params) => {
      //       return h('a', {
      //         style: {
      //           'display': 'inline-block',
      //           'max-width': '200px'
      //         },
      //         on: {
      //           click: () => {
      //             this.$router.push(
      //               {
      //                 name: 'user-home',
      //                 query: {username: params.row.user.username}
      //               })
      //           }
      //         }
      //       }, params.row.user.username)
      //     }
      //   },
      //   {
      //     title: this.$i18n.t('m.mood'),
      //     align: 'center',
      //     key: 'mood'
      //   },
      //   {
      //     title: this.$i18n.t('m.AC'),
      //     align: 'center',
      //     key: 'accepted_number'
      //   },
      //   {
      //     title: this.$i18n.t('m.Total'),
      //     align: 'center',
      //     key: 'submission_number'
      //   },
      //   {
      //     title: this.$i18n.t('m.Rating'),
      //     align: 'center',
      //     render: (h, params) => {
      //       return h('span', utils.getACRate(params.row.accepted_number, params.row.submission_number))
      //     }
      //   }
      // ],
      // options: {
      //   tooltip: {
      //     trigger: 'axis'
      //   },
      //   legend: {
      //     data: [this.$i18n.t('m.AC'), this.$i18n.t('m.Total')]
      //   },
      //   grid: {
      //     x: '3%',
      //     x2: '3%'
      //   },
      //   toolbox: {
      //     show: true,
      //     feature: {
      //       dataView: {show: true, readOnly: true},
      //       magicType: {show: true, type: ['line', 'bar', 'stack']},
      //       saveAsImage: {show: true}
      //     },
      //     right: '10%'
      //   },
      //   calculable: true,
      //   xAxis: [
      //     {
      //       type: 'category',
      //       data: ['root'],
      //       axisLabel: {
      //         interval: 0,
      //         showMinLabel: true,
      //         showMaxLabel: true,
      //         align: 'center',
      //         formatter: (value, index) => {
      //           return utils.breakLongWords(value, 10)
      //         }
      //       }
      //     }
      //   ],
      //   yAxis: [
      //     {
      //       type: 'value'
      //     }
      //   ],
      //   series: [
      //     {
      //       name: this.$i18n.t('m.AC'),
      //       type: 'bar',
      //       data: [0],
      //       markPoint: {
      //         data: [
      //           {type: 'max', name: 'max'}
      //         ]
      //       }
      //     },
      //     {
      //       name: this.$i18n.t('m.Total'),
      //       type: 'bar',
      //       data: [0],
      //       markPoint: {
      //         data: [
      //           {type: 'max', name: 'max'}
      //         ]
      //       }
      //     }
      //   ]
      // }
    }
  },
  mounted() {
    this.getRankData(1)
  },
  methods: {
    getRankData(page) {
      let offset = (page - 1) * this.limit + 3
      // let bar = this.$refs.chart
      // bar.showLoading({maskColor: 'rgba(250, 250, 250, 0.8)'})
      console.log("offset", offset, this.limit, RULE_TYPE.ACM)
      this.loadingTable = true
      api.getUserRank(offset, this.limit, RULE_TYPE.ACM).then(res => {
        this.loadingTable = false
        if (page === 1) {
          // this.changeCharts(res.data.data.results.slice(0, 10))
        }
        this.total = res.data.data.total
        this.dataRank = res.data.data.results
        // bar.hideLoading()
      }).catch(() => {
        this.loadingTable = false
        // bar.hideLoading()
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

<style scoped lang="less">

.rank-container {
  padding: 20px 30px;
  border: 1px solid #dedede;
  border-radius: 7px;
}

.acm-rank {
  width: 1200px;
  padding: 0 20px;

  .acm-rank__contents {
    display: flex;
    justify-content: space-between;
    gap: 30px;


    .acm-rank__left {
      width: 75%;

      .top-users {
        display: flex;
        justify-content: center;
        margin: 20px 0;
        gap: 50px;

        h1 {
          font-size: 20px;
          margin-bottom: 20px;
        }
      }
    }

    .acm-rank__right {
      width: 25%;
      gap: 20px;
      display: flex;
      flex-direction: column;

      .acm-rank__right__title {
        h1 {
          font-size: 20px;
          margin-bottom: 20px;
        }
      }

      .acm-rank__right__content {
        .acm-rank__right__content__description {
          margin-bottom: 20px;
        }
      }
    }
  }
}

.top-user {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 10px;

  h2 {
    font-size: 20px;
  }

  img {
    width: 50px;
    height: 50px;
    border-radius: 50%;
  }
}

.top2 {
  margin-top: 20px;
}

.top3 {
  margin-top: 20px;
}
</style>
