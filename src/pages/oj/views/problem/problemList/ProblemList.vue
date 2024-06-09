<template>
  <main>
    <div class="boxWrapper">
      <div class="left-container">
        <ProblemListTableHeader :query="query" :problemList="problemList" @on-change-header="pushRouter"
                                @pick-one="pickOne"/>
        <ProblemListTable :problemList="problemList"/>
        <Pagination
          :total="total" :page-size.sync="query.limit" :current.sync="query.page"
          @on-change="pushRouter" @on-page-size-change="pushRouter"
          :show-sizer="true">
        </Pagination>
      </div>
      <keep-alive>
        <div class="right-container">
          <MostDifficultProblemLastWeekBox/>
          <PersonalRecommendationBox/>
        </div>
      </keep-alive>
    </div>
  </main>
</template>

<script>
import {mapActions, mapGetters} from 'vuex'
import api from '@oj/api'
import utils from '@/utils/utils'
import {ProblemMixin} from '@oj/components/mixins'
import Pagination from '@oj/components/Pagination'
import MostDifficultProblemLastWeekBox from "./rightSideComponent/MostDifficultProblemLastWeekBox.vue";
import ProblemListTable from "./problemListComponent/ProblemListTable.vue";
import ProblemListTableHeader from "./problemListComponent/ProblemListTableHeader.vue";
import PersonalRecommendationBox from "./rightSideComponent/PersonalRecommendationBox.vue";

export default {
  name: 'ProblemList',
  mixins: [ProblemMixin],
  components: {
    PersonalRecommendationBox,
    ProblemListTableHeader,
    ProblemListTable,
    MostDifficultProblemLastWeekBox,
    Pagination,
  },
  data() {
    return {
      tagList: [],
      problemTableColumns: [ // AC Rate 참고용
        {
          title: this.$i18n.t('m.AC_Rate'),
          render: (h, params) => {
            return h('span', this.getACRate(params.row.accepted_number, params.row.submission_number))
          }
        }
      ],
      problemList: [],
      mostDifficultProblem: {},
      limit: 20,
      total: 0,
      loadings: {
        table: true,
        tag: true
      },
      routeName: '',
      query: {
        keyword: '',
        difficulty: '',
        field: '',
        category: '',
        tag: '',
        page: 1,
        limit: 10
      }
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    ...mapActions(['changeDomTitle']),
    async init(simulate = false) {
      this.routeName = this.$route.name
      let query = this.$route.query
      this.query.difficulty = query.difficulty || ''
      this.query.keyword = query.keyword || ''
      this.query.field = query.field || ''
      this.query.tag = query.tag || ''
      this.query.page = parseInt(query.page) || 1
      if (this.query.page < 1) {
        this.query.page = 1
      }
      this.query.limit = parseInt(query.limit) || 10
      if (!simulate) {
        this.getTagList()
      }
      await this.getProblemList()
    },
    pushRouter() {
      this.$router.push({
        name: 'problem-list',
        query: utils.filterEmptyValue(this.query)
      })
    },
    async getProblemList() {
      let offset = (this.query.page - 1) * this.query.limit
      this.loadings.table = true
      await api.getProblemList(offset, this.limit, this.query).then(res => {
        this.loadings.table = true
        this.total = res.data.data.total
        this.problemList = res.data.data.results
      }, res => {
        this.loadings.table = false
      })
    },
    getTagList() {
      api.getProblemTagList().then(res => {
        this.tagList = res.data.data
        this.loadings.tag = false
      }, res => {
        this.loadings.tag = false
      })
    },
    onReset() {
      this.$router.push({name: 'problem-list'})
    },
    pickOne() {
      api.pickone().then(res => {
        this.$router.push({name: 'problem-details', params: {problemID: res.data.data}})
      })
    }
  },
  computed: {
    ...mapGetters(['website', 'modalStatus', 'user', 'isAuthenticated', 'isAdminRole']),
  },
  watch: {
    '$route'(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init(true)
      }
    },
    'isAuthenticated'(newVal) {
      if (newVal === true) {
        this.init()
      }
    }
  }
}
</script>

<style scoped lang="less">
main {
  width: var(--global-width);
  overflow-x: hidden;
}

.boxWrapper {
  display: flex;
  justify-content: space-between;
}

.left-container {
  width: 72%;
  height: 100%;
}

.right-container {
  width: 26%;
  height: auto;
}
</style>
