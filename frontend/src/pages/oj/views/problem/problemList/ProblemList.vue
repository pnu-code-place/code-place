<template>
  <main>
    <div class="boxWrapper">
      <div class="left-container">
        <ProblemListTableHeader
          :query="query"
          :tagList="tagList"
          @update-query="updateQuery"
          @pick-one="pickOne"
        />
        <ProblemListTable
          :problemList="problemList"
          :loading="loadings.table"
          :skeletonCount="query.limit"
          :showTags="!isTagHidden"
          :sort="query.sort"
          @sort-change="sortProblems"
          @select-tag="filterByTag"
        />
        <div class="problem-list-pagination">
          <Pagination
            v-if="!loadings.table"
            :total="total"
            :page-size.sync="query.limit"
            :current.sync="query.page"
            :page-size-opts="[15, 30, 50, 100, 200]"
            @on-change="pushRouter"
            @on-page-size-change="pushRouter"
            :show-sizer="true"
          >
          </Pagination>
          <div v-else class="pagination-skeleton" aria-hidden="true">
            <span class="pagination-skeleton-button"></span>
            <span class="pagination-skeleton-page"></span>
            <span class="pagination-skeleton-page"></span>
            <span class="pagination-skeleton-page"></span>
            <span class="pagination-skeleton-button"></span>
          </div>
        </div>
      </div>
      <keep-alive>
        <div class="right-container">
          <MostDifficultProblemLastWeekBox :showTags="!isTagHidden" />
          <PersonalRecommendationBox :showTags="!isTagHidden" />
        </div>
      </keep-alive>
    </div>
  </main>
</template>

<script>
import { mapActions, mapGetters } from "vuex"
import api from "@oj/api"
import utils from "@/utils/utils"
import { ProblemMixin } from "@oj/components/mixins"
import Pagination from "@oj/components/Pagination"
import MostDifficultProblemLastWeekBox from "./rightSideComponent/MostDifficultProblemLastWeekBox.vue"
import ProblemListTable from "./problemListComponent/ProblemListTable.vue"
import ProblemListTableHeader from "./problemListComponent/ProblemListTableHeader.vue"
import PersonalRecommendationBox from "./rightSideComponent/PersonalRecommendationBox.vue"

export default {
  name: "ProblemList",
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
      problemTableColumns: [
        // AC Rate 참고용
        {
          title: this.$i18n.t("m.AC_Rate"),
          render: (h, params) => {
            return h(
              "span",
              this.getACRate(
                params.row.accepted_number,
                params.row.submission_number,
              ),
            )
          },
        },
      ],
      problemList: [],
      mostDifficultProblem: {},
      limit: 20,
      total: 0,
      loadings: {
        table: true,
        tag: true,
      },
      routeName: "",
      query: {
        keyword: "",
        difficulty: "",
        field: "",
        category: "",
        tag: "",
        hideTag: "",
        sort: "",
        page: 1,
        limit: 15,
      },
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    ...mapActions(["changeDomTitle"]),
    async init(simulate = false) {
      this.routeName = this.$route.name
      let query = this.$route.query
      this.query.difficulty = query.difficulty || ""
      this.query.keyword = query.keyword || ""
      this.query.field = query.field || ""
      this.query.tag = query.tag || ""
      this.query.hideTag = query.hideTag === "1" ? "1" : ""
      this.query.sort = query.sort || ""
      this.query.page = parseInt(query.page) || 1
      if (this.query.page < 1) {
        this.query.page = 1
      }
      this.query.limit = parseInt(query.limit) || 15
      if (!simulate) {
        this.getTagList()
      }
      await this.getProblemList()
    },
    pushRouter(queryPatch) {
      if (queryPatch && typeof queryPatch === "object") {
        Object.assign(this.query, queryPatch)
      }
      this.$router.push({
        name: "problem-list",
        query: utils.filterEmptyValue(this.query),
      })
    },
    updateQuery(patch) {
      this.query = Object.assign({}, this.query, patch)
      this.pushRouter()
    },
    async getProblemList() {
      let offset = (this.query.page - 1) * this.query.limit
      this.loadings.table = true
      await api.getProblemList(offset, this.query.limit, this.query).then(
        (res) => {
          this.loadings.table = false
          this.total = res.data.data.total
          this.problemList = res.data.data.results
        },
        () => {
          this.loadings.table = false
        },
      )
    },
    getTagList() {
      api.getProblemTagList().then(
        (res) => {
          this.tagList = Array.isArray(res.data.data) ? res.data.data : []
          this.loadings.tag = false
        },
        () => {
          this.loadings.tag = false
        },
      )
    },
    onReset() {
      this.$router.push({ name: "problem-list" })
    },
    pickOne() {
      api.pickone().then((res) => {
        this.$router.push({
          name: "problem-details",
          params: { problemID: res.data.data },
        })
      })
    },
    filterByTag(tag) {
      this.updateQuery({ tag, page: 1 })
    },
    sortProblems(sort) {
      this.updateQuery({ sort, page: 1 })
    },
  },
  computed: {
    ...mapGetters([
      "website",
      "modalStatus",
      "user",
      "isAuthenticated",
      "isAdminRole",
    ]),
    isTagHidden() {
      return this.query.hideTag === "1"
    },
  },
  watch: {
    $route(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init(true)
      }
    },
    isAuthenticated(newVal) {
      if (newVal === true) {
        this.init()
      }
    },
  },
}
</script>

<style scoped lang="less">
main {
  width: 100%;
  max-width: var(--global-width);
  padding: 0 30px;
  box-sizing: border-box;
  overflow-x: hidden;

  @media (max-width: 1024px) {
    padding: 0 20px;
  }
  @media (max-width: 768px) {
    padding: 0 14px;
  }
}

.boxWrapper {
  display: flex;
  justify-content: space-between;
  gap: 20px;

  @media (max-width: 1024px) {
    flex-direction: column;
  }
}

.left-container {
  flex: 1;
  min-width: 0;
  height: 100%;
}

.problem-list-pagination {
  min-height: 42px;
}

.pagination-skeleton {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 42px;
}

.pagination-skeleton-button,
.pagination-skeleton-page {
  display: inline-block;
  border-radius: 6px;
  background: #f1f3f5;
}

.pagination-skeleton-button {
  width: 58px;
  height: 30px;
}

.pagination-skeleton-page {
  width: 30px;
  height: 30px;
}

.right-container {
  width: 280px;
  flex-shrink: 0;
  height: auto;

  @media (max-width: 1024px) {
    width: 100%;
  }
}
</style>
