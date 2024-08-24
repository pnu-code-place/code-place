<template>
  <div>
    <div class="submissionBox">
      <div class="submissionTitle">
        <p>{{$t('m.Submissions')}}</p>
        <div style="display: flex; align-items: center; gap: 20px;">
          <Dropdown @on-click="handleResultChange">
            <span style="cursor: default;">{{status}}
              <Icon type="arrow-down-b"></Icon>
            </span>
            <Dropdown-menu slot="list">
              <Dropdown-item name="">{{$t('m.All')}}</Dropdown-item>
              <Dropdown-item v-for="status in Object.keys(JUDGE_STATUS)" :key="status" :name="status">
                {{$t('m.' + JUDGE_STATUS[status].name.replace(/ /g, "_"))}}
              </Dropdown-item>
            </Dropdown-menu>
          </Dropdown>
          <i-switch size="large" v-model="formFilter.myself" @on-change="handleQueryChange">
            <span slot="open">{{$t('m.Mine')}}</span>
            <span slot="close">{{$t('m.All')}}</span>
          </i-switch>
          <Input v-model="formFilter.username" :placeholder="$t('m.Search_Author')" @on-enter="handleQueryChange" style="width: 150px;"/>
          <Button type="info" icon="refresh" @click="getSubmissions">{{$t('m.Refresh')}}</Button>
        </div>
      </div>
      <div v-if="submissions.length === 0" style="text-align: center; font-size: 16px;">{{ $t('m.No_Submissions') }}</div>
      <table v-else class="submissionContent">
        <thead>
          <th>{{ $t('m.When') }}</th>
          <th>{{ $t('m.ID') }}</th>
          <th>{{ $t('m.Status') }}</th>
          <th>{{ $t('m.Problem') }}</th>
          <th>{{ $t('m.Time') }}</th>
          <th>{{ $t('m.Memory') }}</th>
          <th>{{ $t('m.Language') }}</th>
          <th>{{ $t('m.Submission_Table_Author') }}</th>
        </thead>
        <tbody>
          <tr v-for="submission in submissions">
            <td style="cursor: default;">{{submission.time_cost | localtime('YYYY-M-D')}}</td>
            <td><a @click="goSubmissionDetail(submission.id)">{{submission.id.slice(0,12)}}</a></td>
            <td><Tag style="cursor: default;" :color="JUDGE_STATUS[submission.result].color">{{JUDGE_STATUS[submission.result].name}}</Tag></td>
            <td><a @click="goProblemDetail(submission.problem)">{{submission.problem}}</a></td>
            <td style="cursor: default;">{{submissionTimeFormat(submission.statistic_info.time_cost)}}</td>
            <td style="cursor: default;">{{submissionMemoryFormat(submission.statistic_info.memory_cost)}}</td>
            <td style="cursor: default;">{{submission.language}}</td>
            <td><a @click="goUserHome(submission.username)">{{submission.username}}</a></td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pagination :total="total" :page-size="limit" @on-change="changeRoute" :current.sync="page"></Pagination>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import api from '@oj/api'
  import { JUDGE_STATUS, USER_TYPE } from '@/utils/constants'
  import utils from '@/utils/utils'
  import time from '@/utils/time'
  import Pagination from '@/pages/oj/components/Pagination'

  export default {
    name: 'submissionList',
    components: {
      Pagination
    },
    data () {
      return {
        formFilter: {
          myself: false,
          result: '',
          username: ''
        },
        loadingTable: false,
        submissions: [],
        total: 30,
        limit: 12,
        page: 1,
        contestID: '',
        problemID: '',
        routeName: '',
        JUDGE_STATUS: '',
        rejudge_column: false
      }
    },
    mounted () {
      this.init()
      this.JUDGE_STATUS = Object.assign({}, JUDGE_STATUS)
      delete this.JUDGE_STATUS['9']
      delete this.JUDGE_STATUS['2']
    },
    methods: {
      init () {
        this.contestID = this.$route.params.contestID
        let query = this.$route.query
        this.problemID = query.problemID
        this.formFilter.myself = query.myself === '1'
        this.formFilter.result = query.result || ''
        this.formFilter.username = query.username || ''
        this.page = parseInt(query.page) || 1
        if (this.page < 1) {
          this.page = 1
        }
        this.routeName = this.$route.name
        this.getSubmissions()
      },
      buildQuery () {
        return {
          myself: this.formFilter.myself === true ? '1' : '0',
          result: this.formFilter.result,
          username: this.formFilter.username,
          page: this.page
        }
      },
      getSubmissions () {
        let params = this.buildQuery()
        params.contest_id = this.contestID
        params.problem_id = this.problemID
        let offset = (this.page - 1) * this.limit
        let func = this.contestID ? 'getContestSubmissionList' : 'getSubmissionList'
        this.loadingTable = true
        api[func](offset, this.limit, params).then(res => {
          let data = res.data.data
          for (let v of data.results) {
            v.loading = false
          }
          this.adjustRejudgeColumn()
          this.loadingTable = false
          this.submissions = data.results
          this.total = data.total
        }).catch(() => {
          this.loadingTable = false
        })
      },
      changeRoute () {
        let query = utils.filterEmptyValue(this.buildQuery())
        query.contestID = this.contestID
        query.problemID = this.problemID
        let routeName = query.contestID ? 'contest-submission-list' : 'submission-list'
        this.$router.push({
          name: routeName,
          query: utils.filterEmptyValue(query)
        })
      },
      goRoute (route) {
        this.$router.push(route)
      },
      adjustRejudgeColumn () {
        if (!this.rejudgeColumnVisible || this.rejudge_column) {
          return
        }
        const judgeColumn = {
          title: this.$i18n.t('m.Option'),
          fixed: 'right',
          align: 'center',
          width: 90,
          render: (h, params) => {
            return h('Button', {
              props: {
                type: 'primary',
                size: 'small',
                loading: params.row.loading
              },
              on: {
                click: () => {
                  this.handleRejudge(params.row.id, params.index)
                }
              }
            }, this.$i18n.t('m.Rejudge'))
          }
        }
        this.columns.push(judgeColumn)
        this.rejudge_column = true
      },
      handleResultChange (status) {
        this.page = 1
        this.formFilter.result = status
        this.changeRoute()
      },
      handleQueryChange () {
        this.page = 1
        this.changeRoute()
      },
      handleRejudge (id, index) {
        this.submissions[index].loading = true
        api.submissionRejudge(id).then(res => {
          this.submissions[index].loading = false
          this.$success('Succeeded')
          this.getSubmissions()
        }, () => {
          this.submissions[index].loading = false
        })
      },
      goSubmissionDetail (id) {
        this.$router.push({
          name: 'submission-details',
          params: {
            id: id
          }
        })
      },
      goProblemDetail (id) {
        this.$router.push({
          name: 'contest-problem-details',
          params: {
            problemID: id, 
            contestID: this.contestID
          }
        })
      },
      goUserHome (username) {
        this.$router.push({
          name: 'user-home',
          query: {username: username}
        })
      },
      submissionMemoryFormat (memory) {
        return utils.submissionMemoryFormat(memory);
      },
      submissionTimeFormat (time) {
        return utils.submissionTimeFormat(time);
      },
    },
    computed: {
      ...mapGetters(['isAuthenticated', 'user']),
      status () {
        return this.formFilter.result === '' ? this.$i18n.t('m.Status') : this.$i18n.t('m.' + JUDGE_STATUS[this.formFilter.result].name.replace(/ /g, '_'))
      },
      rejudgeColumnVisible () {
        return !this.contestID && this.user.admin_type === USER_TYPE.SUPER_ADMIN
      },
    },
    watch: {
      '$route' (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.init()
        }
      },
      'rejudgeColumnVisible' () {
        this.adjustRejudgeColumn()
      },
      'isAuthenticated' () {
        this.init()
      }
    }
  }
</script>

<style scoped lang="less">
.submissionBox {
  border: 1px solid #e9ece9;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--box-background-color);
  padding: 15px 20px;
  border-radius: 7px;
}
.submissionTitle {
  display: flex;
  justify-content: space-between;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
}
.submissionContent {
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
