<template>
  <div class="contestBox">
    <div class="contestTitle">
      <p>{{contest.title}}</p>
      <div slot="extra">
        <Tag type="dot" :color="countdownColor">
          <span id="countdown">{{countdown}}</span>
        </Tag>
      </div>
    </div>
    <div class="contestContent">
      <div v-html="contest.description" class="markdown-body"></div>
      <div class="contestPassword" v-if="passwordFormVisible">
        <Input v-model="contestPassword" type="password"
               :placeholder="$t('m.Contest_Password_Placeholder')" class="contestPasswordInput"
               @on-enter="checkPassword"/>
        <Button type="info" @click="checkPassword">{{$t('m.Button_Enter')}}</Button>
      </div>
    </div>
    <div class="contestFooter">
      <div style="display: flex; flex-direction: column; gap: 5px;">
        <li style="display: inline-block;">
          <Icon type="calendar" color="#3091f2"></Icon> 시작일 : {{contest.start_time | localtime('YYYY-M-D') }}
        </li>
        <li style="display: inline-block;">
          <Icon type="calendar" color="#3091f2"></Icon> 종료일 : {{contest.end_time | localtime('YYYY-M-D') }}
        </li>
      </div>
      <div style="display: flex; flex-direction: column; gap: 5px;">
        <div style="display: flex; align-items: center;">
          대회 종류 :
          <div class="contestTag">
            {{contest.contest_type}}
          </div>
        </div>
        <div style="display: flex; align-items: center;">
          대회 규칙 :
          <div class="contestTag">
            {{contest.rule_type}}
          </div>
        </div>
      </div>
      <div style="font-size: 18px; font-weight: bold; width: 80px;">
        {{contest.created_by.username}}
      </div>
    </div>
  </div>
</template>

<script>
  import moment from 'moment'
  import api from '@oj/api'
  import { mapState, mapGetters, mapActions } from 'vuex'
  import { types } from '@/store'
  import { CONTEST_STATUS_REVERSE, CONTEST_STATUS } from '@/utils/constants'
  import time from '@/utils/time'

  export default {
    name: 'ContestDetail',
    components: {},
    data () {
      return {
        CONTEST_STATUS: CONTEST_STATUS,
        route_name: '',
        btnLoading: false,
        contestID: '',
        contestPassword: '',
        columns: [
          {
            title: this.$i18n.t('m.StartAt'),
            render: (h, params) => {
              return h('span', time.utcToLocal(params.row.start_time))
            }
          },
          {
            title: this.$i18n.t('m.EndAt'),
            render: (h, params) => {
              return h('span', time.utcToLocal(params.row.end_time))
            }
          },
          {
            title: this.$i18n.t('m.ContestType'),
            render: (h, params) => {
              return h('span', this.$i18n.t('m.' + params.row.contest_type ? params.row.contest_type.replace(' ', '_') : ''))
            }
          },
          {
            title: this.$i18n.t('m.Rule'),
            render: (h, params) => {
              return h('span', this.$i18n.t('m.' + params.row.rule_type))
            }
          },
          {
            title: this.$i18n.t('m.Creator'),
            render: (h, data) => {
              return h('span', data.row.created_by.username)
            }
          }
        ]
      }
    },
    mounted () {
      this.contestID = this.$route.params.contestID
      this.route_name = this.$route.name
      this.$store.dispatch('getContest').then(res => {
        this.changeDomTitle({title: res.data.data.title})
        let data = res.data.data
        let endTime = moment(data.end_time)
        if (endTime.isAfter(moment(data.now))) {
          this.timer = setInterval(() => {
            this.$store.commit(types.NOW_ADD_1S)
          }, 1000)
        }
      })
    },
    methods: {
      ...mapActions(['changeDomTitle']),
      handleRoute (route) {
        this.$router.push(route)
      },
      checkPassword () {
        if (this.contestPassword === '') {
          this.$error('Password can\'t be empty')
          return
        }
        this.btnLoading = true
        api.checkContestPassword(this.contestID, this.contestPassword).then((res) => {
          this.$success('Succeeded')
          this.$store.commit(types.CONTEST_ACCESS, {access: true})
          this.btnLoading = false
        }, (res) => {
          this.btnLoading = false
        })
      }
    },
    computed: {
      ...mapState({
        showMenu: state => state.contest.itemVisible.menu,
        contest: state => state.contest.contest,
        contest_table: state => [state.contest.contest],
        now: state => state.contest.now
      }),
      ...mapGetters(
        ['contestMenuDisabled', 'contestRuleType', 'contestStatus', 'countdown', 'isContestAdmin',
          'OIContestRealTimePermission', 'passwordFormVisible']
      ),
      countdownColor () {
        if (this.contestStatus) {
          return CONTEST_STATUS_REVERSE[this.contestStatus].color
        }
      },
    },
    watch: {
      '$route' (newVal) {
        this.route_name = newVal.name
        this.contestID = newVal.params.contestID
        this.changeDomTitle({title: this.contest.title})
      }
    },
    beforeDestroy () {
      clearInterval(this.timer)
      this.$store.commit(types.CLEAR_CONTEST)
    }
  }
</script>

<style lang="less" scoped>
.contestBox {
  border: 1px solid #e9ece9;
  display: flex;
  flex-direction: column;
  gap: 32px;
  background: var(--box-background-color);
  padding: 15px 20px;
  border-radius: 7px;
}
.contestTitle {
  display: flex;
  justify-content: space-between;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
  #countdown {
    font-size: 16px;
  }
}
.contestContent {
  padding: 0px 10px;
  .contestPassword {
    display: flex;
    gap: 10px;
    .contestPasswordInput {
      width: 200px;
    }
  }
}
.contestFooter {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  .contestTag {
    width: fit-content;
    background-color: #F7F7F7; 
    border: 1px solid #DDDEE1; 
    border-radius: 32px;
    margin-left: 4px;
    padding: 2px 7px;
  }
}
</style>
