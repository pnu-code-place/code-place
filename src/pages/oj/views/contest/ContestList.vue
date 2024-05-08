<template>
  <main>
    <Col :span="24">
    <Panel id="contest-card" dis-hover>
      <div slot="title" style="font-size: medium; font-weight: bold">{{query.rule_type === '' ? this.$i18n.t('m.All') : query.rule_type}} {{$t('m.Contests')}}</div>
      <div slot="extra">
        <ul class="filter">
          <li>
            <Dropdown @on-click="onRuleChange">
              <span>{{query.rule_type === '' ? this.$i18n.t('m.Rule') : this.$i18n.t('m.' + query.rule_type)}}
                <Icon type="arrow-down-b"></Icon>
              </span>
              <Dropdown-menu slot="list">
                <Dropdown-item name="">{{$t('m.All')}}</Dropdown-item>
                <Dropdown-item name="OI">{{$t('m.OI')}}</Dropdown-item>
                <Dropdown-item name="ACM">{{$t('m.ACM')}}</Dropdown-item>
              </Dropdown-menu>
            </Dropdown>
          </li>
          <li>
            <Dropdown @on-click="onStatusChange">
              <span>{{query.status === '' ? this.$i18n.t('m.Status') : this.$i18n.t('m.' + CONTEST_STATUS_REVERSE[query.status].name.replace(/ /g,"_"))}}
                <Icon type="arrow-down-b"></Icon>
              </span>
              <Dropdown-menu slot="list">
                <Dropdown-item name="">{{$t('m.All')}}</Dropdown-item>
                <Dropdown-item name="0">{{$t('m.Underway')}}</Dropdown-item>
                <Dropdown-item name="1">{{$t('m.Not_Started')}}</Dropdown-item>
                <Dropdown-item name="-1">{{$t('m.Ended')}}</Dropdown-item>
              </Dropdown-menu>
            </Dropdown>
          </li>
          <li>
            <Input id="keyword" @on-enter="changeRoute" @on-click="changeRoute" v-model="query.keyword"
                   icon="ios-search-strong" placeholder="키워드"/>
          </li>
        </ul>
      </div>
      <p id="no-contest" v-if="contests.length == 0">{{$t('m.No_contest')}}</p>
    </Panel>
    <div class="contestLayer">
      <template v-for="contest in contests">
        <div @click.stop="goContest(contest)" class="contestBox" :key="contest.id">
          <div class="contestTitle">
            <p>
              <Icon v-if="contest.contest_type != 'Public'" type="ios-locked-outline" size="20" style="font-weight: 900;"></Icon>
              {{contest.title}}
            </p>
            <Tag style="flex-shrink: 0; margin: 0; width: 84px;" type="dot" :color="CONTEST_STATUS_REVERSE[contest.status].color">{{CONTEST_STATUS_REVERSE[contest.status].name}}</Tag>
          </div>
          <div class="contestContent">
            <p v-html="contest.description"></p>
          </div>
          <div class="contestFooter">
            <div class="contestTag">
              {{contest.rule_type}}
            </div>
            <div>
              <Icon type="calendar"></Icon>
              {{contest.start_time | localtime('YYYY-M-D HH:mm') }}
            </div>
          </div>
        </div>
      </template>
    </div>
    <Pagination :total="total" :page-size.sync="limit" @on-change="changeRoute" :current.sync="page" :show-sizer="true" @on-page-size-change="changeRoute"></Pagination>
    </Col>
  </main>
</template>

<script>
  import api from '@oj/api'
  import { mapGetters } from 'vuex'
  import utils from '@/utils/utils'
  import Pagination from '@/pages/oj/components/Pagination'
  import time from '@/utils/time'
  import { CONTEST_STATUS_REVERSE, CONTEST_TYPE } from '@/utils/constants'

  const limit = 10

  export default {
    name: 'contest-list',
    components: {
      Pagination
    },
    data () {
      return {
        page: 1,
        query: {
          status: '',
          keyword: '',
          rule_type: ''
        },
        limit: limit,
        total: 0,
        rows: '',
        contests: [],
        CONTEST_STATUS_REVERSE: CONTEST_STATUS_REVERSE,
        cur_contest_id: ''
      }
    },
    beforeRouteEnter (to, from, next) {
      api.getContestList(0, limit).then((res) => {
        next((vm) => {
          vm.contests = res.data.data.results
          vm.total = res.data.data.total
        })
      }, (res) => {
        next()
      })
    },
    methods: {
      init () {
        let route = this.$route.query
        this.query.status = route.status || ''
        this.query.rule_type = route.rule_type || ''
        this.query.keyword = route.keyword || ''
        this.page = parseInt(route.page) || 1
        this.limit = parseInt(route.limit) || 10
        this.getContestList(this.page)
      },
      getContestList (page = 1) {
        let offset = (page - 1) * this.limit
        api.getContestList(offset, this.limit, this.query).then((res) => {
          this.contests = res.data.data.results
          this.total = res.data.data.total
        })
      },
      changeRoute () {
        let query = Object.assign({}, this.query)
        query.page = this.page
        query.limit = this.limit

        this.$router.push({
          name: 'contest-list',
          query: utils.filterEmptyValue(query)
        })
      },
      onRuleChange (rule) {
        this.query.rule_type = rule
        this.page = 1
        this.changeRoute()
      },
      onStatusChange (status) {
        this.query.status = status
        this.page = 1
        this.changeRoute()
      },
      goContest (contest) {
        this.cur_contest_id = contest.id
        if (contest.contest_type !== CONTEST_TYPE.PUBLIC && !this.isAuthenticated) {
          this.$error(this.$i18n.t('m.Please_login_first'))
          this.$store.dispatch('changeModalStatus', {visible: true})
        } else {
          this.$router.push({name: 'contest-overview', params: {contestID: contest.id}})
        }
      },
    },
    computed: {
      ...mapGetters(['isAuthenticated', 'user'])
    },
    watch: {
      '$route' (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.init()
        }
      }
    }

  }
</script>
<style lang="less" scoped>
main{
  width: 1200px;
  #contest-card {
    background-color: var(--box-background-color);
    #keyword {
      width: 80%;
      margin-right: 30px;
    }
    #no-contest {
      text-align: center;
      font-size: 16px;
      padding: 20px;
    }
  }
  .contestLayer {
    margin-top: 10px;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    align-items: center;
    gap: 10px;
  }
  .contestBox {
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 20px;
    width: 393px;
    border-radius: 7px;
    border: 1px solid #e9ece9;
    background-color: var(--box-background-color);
  }
  .contestTitle {
    display: flex;
    justify-content: space-between;
    align-items: center;
    p {
      padding-left: 2px;
      font-size: 18px;
      font-weight: bold;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    p:hover {
      white-space: wrap;
    }
  }
  .contestContent {
    margin: 0px 0px 6px 6px;
    width: 280px;

    height: 18px;
    text-overflow: ellipsis;
    overflow: hidden;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 1;
  }
  .contestFooter {
    display: flex;
    justify-content: space-between;
    align-items: center;
    li {
      display: inline-block;
    }
    .contestTag {
      background-color: #F7F7F7; 
      border: 1px solid #DDDEE1; 
      border-radius: 32px; 
      padding: 2px 7px;
    }
  }
}

</style>
