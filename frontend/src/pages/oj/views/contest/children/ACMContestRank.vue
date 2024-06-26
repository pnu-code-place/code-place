<template>
  <div>
    <div class="ACMRankBox">
      <div class="ACMRankTitle">
        <p>{{ $t('m.Rank') }}</p>
        <div class="ACMRankTitleIcon">
          <screen-full style="height: 18px; width: 18px;"></screen-full>
          <Button v-if="isContestAdmin" size="small" @click="downloadRankCSV">{{$t('m.download_csv')}}</Button>
        </div>
      </div>
      <div v-if="!dataRank.length" style="text-align: center; font-size: 16px;">{{$t('m.No_Submissions')}}</div>
      <table v-else class="ACMRankContent">
        <thead>
          <th style="width: 50px;">#</th>
          <th>{{ $t('m.User_User') }}</th>
          <th>{{ $t('m.Solved_Problems') }}</th>
          <th v-for="problem in contestProblems"><a style="color: #6CCBFF;" @click="goProblemPage(problem._id)">{{problem._id}}</a></th>
        </thead>
        <tbody>
          <tr v-for="rank in dataRank">
            <td>{{rank.idx}}</td>
            <td><a @click="goUserPage(rank.user.username)">{{rank.user.username}}</a></td>
            <td>{{rank.accepted_number}}</td>
            <td v-for="problem in contestProblems">
              <div v-if="rank[problem.id].isSet" style="display: flex; flex-direction: column; align-items: center;">
                <span style="font-size: 12px; background-color: rgb(128, 128, 128); padding: 2px 4px; border-radius: 5px; color: white;">
                  {{rank[problem.id].ac_time | localtime('MM/DD')}}</span>
                {{rank[problem.id].ac_time | localtime('HH:mm:ss')}}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pagination :total="total"
                :page-size.sync="limit"
                :current.sync="page"
                @on-change="updateContestData"
                @on-page-size-change="updateContestData()"
                show-sizer></Pagination>
  </div>
</template>

<script>
  import moment from 'moment'
  import { mapActions } from 'vuex'
  import api from '@oj/api'
  import Pagination from '@oj/components/Pagination'
  import ContestRankMixin from './contestRankMixin'
  import time from '@/utils/time'
  import utils from '@/utils/utils'

  export default {
    name: 'acm-contest-rank',
    components: {
      Pagination
    },
    mixins: [ContestRankMixin],
    data () {
      return {
        total: 0,
        page: 1,
        contestID: '',
        dataRank: [],
      }
    },
    mounted () {
      this.contestID = this.$route.params.contestID
      this.updateContestData()
    },
    methods: {
      ...mapActions(['getContestProblems']),
      updateContestData () {
        let params = {
          offset: (this.page - 1) * this.limit,
          limit: this.limit,
          contest_id: this.$route.params.contestID,
          force_refresh: this.forceUpdate ? '1' : '0'
        }
        api.getContestRank(params).then(res => {
          const data = res.data.data.results
          let dataRank = JSON.parse(JSON.stringify(data))

          this.getContestProblems().then((res) => {
            this.addRankData(dataRank, res.data.data)
          })
          this.total = res.data.data.total
        })
      },
      addRankData (dataRank, problems) {
        problems.forEach(problem => {
          dataRank.forEach((rank, idx) => {
            dataRank[idx][problem.id] = {isSet: false, problemId: problem._id};
          })
        })
        dataRank.forEach((rank, i) => {
          let info = rank.submission_info
          Object.keys(info).forEach(problemID => {
            dataRank[i][problemID].ac_time = moment(this.contest.start_time).add(info[problemID].ac_time, 'seconds').format()
            dataRank[i][problemID].isSet = true
          })
          dataRank[i].idx = (this.page - 1) * this.limit + i + 1;
        })
        this.dataRank = dataRank;
      },
      goUserPage (username) {
        this.$router.push({
          name: 'user-dashboard',
          params: {username: username}
        })
      },
      goProblemPage (problemId) {
        this.$router.push({
          name: 'contest-problem-details',
          params: {
            contestID: this.contestID,
            problemID: problemId
          }
        })
      },
      downloadRankCSV () {
        utils.downloadFile(`contest_rank?download_csv=1&contest_id=${this.$route.params.contestID}&force_refrash=${this.forceUpdate ? '1' : '0'}`)
      }
    }
  }
</script>

<style scoped lang="less">
.ACMRankBox {
  border: 1px solid #e9ece9;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--box-background-color);
  padding: 15px 20px;
  border-radius: 7px;
}
.ACMRankTitle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
  .ACMRankTitleIcon {
    display: flex;
    gap: 10px;
    justify-content: space-between;
    align-items: center;
  }
}
.ACMRankContent {
  text-align: center;
  th {
    width: 80px;
    color: #7E7E7E;
    font-size: 1.3em;
    padding-bottom: 10px;
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
