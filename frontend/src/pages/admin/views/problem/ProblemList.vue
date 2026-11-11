<template>
  <div class="view">
    <Panel
      :title="
        contestId
          ? this.$i18n.t('m.Contest_Problem_List')
          : this.$i18n.t('m.Problem_List')
      "
    >
      <div slot="header">
        <el-row type="flex">
          <template v-if="!contestId">
            <el-col class="filter-col">
              <el-select
                v-model="sourceFilter"
                placeholder="출처"
                @change="(value) => changeFilter('sourceFilter', value)"
              >
                <el-option label="전체" value="all"></el-option>
                <el-option label="백준" value="boj"></el-option>
              </el-select>
            </el-col>
            <el-col class="filter-col">
              <el-select
                v-model="visibleFilter"
                placeholder="상태"
                @change="(value) => changeFilter('visibleFilter', value)"
              >
                <el-option label="전체" value="all"></el-option>
                <el-option label="활성화" value="true"></el-option>
                <el-option label="비활성화" value="false"></el-option>
              </el-select>
            </el-col>
          </template>
          <el-col>
            <el-input
              v-model="keyword"
              prefix-icon="el-icon-search"
              placeholder="Keywords"
            >
            </el-input>
          </el-col>
        </el-row>
      </div>
      <el-table
        v-loading="loading"
        element-loading-text="loading"
        ref="table"
        :data="problemList"
        @row-dblclick="handleDblclick"
        @selection-change="(rows) => (selectedProblems = rows)"
        style="width: 100%"
      >
        <el-table-column v-if="!contestId" type="selection" width="55">
        </el-table-column>
        <el-table-column width="100" prop="id" :label="$t('m.ProblemList_ID')">
        </el-table-column>
        <el-table-column prop="title" :label="$t('m.ProblemList_Title')">
          <template slot-scope="{ row }">
            <span v-show="!row.isEditing">{{ row.title }}</span>
            <el-input
              v-show="row.isEditing"
              v-model="row.title"
              @keyup.enter.native="handleInlineEdit(row)"
            >
            </el-input>
          </template>
        </el-table-column>
        <el-table-column
          prop="created_by.username"
          :label="$t('m.ProblemList_Author')"
        >
        </el-table-column>
        <el-table-column
          width="250"
          prop="create_time"
          :label="$t('m.ProblemList_Create_Time')"
        >
          <template slot-scope="scope">
            {{ scope.row.create_time | localtime }}
          </template>
        </el-table-column>
        <el-table-column
          width="150"
          prop="visible"
          :label="$t('m.ProblemList_Visible')"
        >
          <template slot-scope="scope">
            <el-switch
              v-model="scope.row.visible"
              active-text=""
              inactive-text=""
              @change="updateProblem(scope.row)"
            >
            </el-switch>
          </template>
        </el-table-column>
        <el-table-column
          fixed="right"
          width="250"
          :label="$t('m.ProblemList_Operation')"
        >
          <div slot-scope="scope">
            <icon-btn
              v-if="!contestId"
              name="미리보기"
              icon="eye"
              @click.native="previewProblem(scope.row)"
            ></icon-btn>
            <icon-btn
              :name="$t('m.Icon_Edit')"
              icon="edit"
              @click.native="goEdit(scope.row.id)"
            ></icon-btn>
            <icon-btn
              v-if="contestId"
              :name="$t('m.Icon_Make_Public')"
              icon="clone"
              @click.native="makeContestProblemPublic(scope.row.id)"
            ></icon-btn>
            <icon-btn
              icon="download"
              :name="$t('m.Icon_Download_TestCase')"
              @click.native="downloadTestCase(scope.row.id)"
            ></icon-btn>
            <icon-btn
              icon="trash"
              :name="$t('m.Icon_Delete')"
              @click.native="deleteProblem(scope.row.id)"
            ></icon-btn>
          </div>
        </el-table-column>
      </el-table>
      <div class="panel-options">
        <el-button
          type="primary"
          size="small"
          @click="goCreateProblem"
          icon="el-icon-plus"
          >{{ $t("m.Button_Create") }}
        </el-button>
        <template v-if="selectedProblems.length">
          <el-button
            type="primary"
            size="small"
            icon="el-icon-fa-eye"
            @click="changeVisibility(true)"
            >선택 활성화 ({{ selectedProblems.length }})
          </el-button>
          <el-button
            size="small"
            icon="el-icon-fa-eye-slash"
            @click="changeVisibility(false)"
            >선택 비활성화 ({{ selectedProblems.length }})
          </el-button>
        </template>
        <el-button
          v-if="!contestId && sourceFilter === 'boj'"
          type="danger"
          size="small"
          icon="el-icon-fa-eye-slash"
          @click="hideBOJProblems"
          >백준 문제 전체 비활성화
        </el-button>
        <el-button
          v-if="contestId"
          type="primary"
          size="small"
          icon="el-icon-plus"
          @click="addProblemDialogVisible = true"
          >{{ $t("m.Button_Add_Public_Problem") }}
        </el-button>
        <el-button
          v-if="contestId"
          type="primary"
          size="small"
          icon="el-icon-plus"
          @click="importProblemDialogVisible = true"
          >{{ $t("m.Button_Add_From_Contest") }}
        </el-button>
        <el-pagination
          class="page"
          layout="prev, pager, next"
          @current-change="currentChange"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
        >
        </el-pagination>
      </div>
    </Panel>
    <el-dialog
      title="문제 미리보기"
      width="80%"
      :visible.sync="previewDialogVisible"
    >
      <problem-preview
        v-if="previewProblemData"
        :problem="previewProblemData"
      ></problem-preview>
    </el-dialog>
    <el-dialog
      :title="$t('m.ProblemList_Update_Title')"
      width="20%"
      :visible.sync="InlineEditDialogVisible"
      @close-on-click-modal="false"
    >
      <div>
        <p>{{ $t("m.Display_ID") }}: {{ currentRow.id }}</p>
        <p>{{ $t("m.ProblemList_Title") }}: {{ currentRow.title }}</p>
      </div>
      <span slot="footer">
        <cancel
          @click.native="
            InlineEditDialogVisible = false
            getProblemList(currentPage)
          "
        ></cancel>
        <save @click.native="updateProblem(currentRow)"></save>
      </span>
    </el-dialog>
    <el-dialog
      title="Add Contest Problem"
      v-if="contestId"
      width="80%"
      :visible.sync="addProblemDialogVisible"
      @close-on-click-modal="false"
    >
      <add-problem-component
        :contestID="contestId"
        @on-change="getProblemList"
      ></add-problem-component>
    </el-dialog>
    <el-dialog
      :title="$t('m.Button_Add_From_Contest')"
      v-if="contestId"
      width="80%"
      :visible.sync="importProblemDialogVisible"
      @close-on-click-modal="false"
    >
      <import-from-contest
        :contestID="contestId"
        @on-change="getProblemList"
      ></import-from-contest>
    </el-dialog>
  </div>
</template>

<script>
import api from "../../api.js"
import utils from "@/utils/utils"
import AddProblemComponent from "./AddPublicProblem.vue"
import ImportFromContest from "./ImportFromContest.vue"
import ProblemPreview from "./ProblemPreview.vue"

// A list of routers which need problems list
const PROBLEM_LIST_ROUTES = ["problem-list", "contest-problem-list"]

export default {
  name: "ProblemList",
  components: {
    AddProblemComponent,
    ImportFromContest,
    ProblemPreview,
  },
  data() {
    return {
      pageSize: 10,
      total: 0,
      problemList: [],
      keyword: "",
      sourceFilter: this.$route.query.source || "",
      visibleFilter: this.$route.query.visible || "",
      selectedProblems: [],
      loading: false,
      previewDialogVisible: false,
      previewProblemData: null,
      currentPage: 1,
      routeName: "",
      contestId: "",
      // for make public use
      currentProblemID: "",
      currentRow: {},
      InlineEditDialogVisible: false,
      makePublicDialogVisible: false,
      addProblemDialogVisible: false,
      importProblemDialogVisible: false,
    }
  },
  mounted() {
    this.routeName = this.$route.name
    this.contestId = this.$route.params.contestId
    this.getProblemList(this.currentPage)
  },
  methods: {
    handleDblclick(row) {
      row.isEditing = true
    },
    goEdit(problemId) {
      if (this.routeName === "problem-list") {
        this.$router.push({ name: "edit-problem", params: { problemId } })
      } else if (this.routeName === "contest-problem-list") {
        this.$router.push({
          name: "edit-contest-problem",
          params: { problemId: problemId, contestId: this.contestId },
        })
      }
    },
    goCreateProblem() {
      if (this.routeName === "problem-list") {
        this.$router.push({ name: "create-problem" })
      } else if (this.routeName === "contest-problem-list") {
        this.$router.push({
          name: "create-contest-problem",
          params: { contestId: this.contestId },
        })
      }
    },
    // 切换页码回调
    currentChange(page) {
      this.currentPage = page
      this.getProblemList(page)
    },
    getProblemList(page = 1) {
      this.loading = true
      let funcName =
        this.routeName === "problem-list"
          ? "getProblemList"
          : "getContestProblemList"
      console.log("this.routeName:", this.routeName)
      let params = {
        limit: this.pageSize,
        offset: (page - 1) * this.pageSize,
        keyword: this.keyword,
        contest_id: this.contestId,
        source: this.contestId ? "" : this.sourceFilter,
        visible: this.contestId ? "" : this.visibleFilter,
      }
      api[funcName](params).then(
        (res) => {
          this.loading = false
          this.total = res.data.data.total
          for (let problem of res.data.data.results) {
            problem.isEditing = false
          }
          this.problemList = res.data.data.results
        },
        (res) => {
          this.loading = false
        },
      )
    },
    deleteProblem(id) {
      this.$confirm(
        this.$t("m.ProblemList_Delete_Problem_Content"),
        this.$t("m.ProblemList_Delete_Problem_Title"),
        {
          type: "warning",
        },
      ).then(
        () => {
          let funcName =
            this.routeName === "problem-list"
              ? "deleteProblem"
              : "deleteContestProblem"
          api[funcName](id)
            .then(() => [this.getProblemList(this.currentPage - 1)])
            .catch(() => {})
        },
        () => {},
      )
    },
    makeContestProblemPublic(problemID) {
      this.$prompt(
        this.$t("m.ProblemList_Visible_Problem_Content"),
        this.$t("m.ProblemList_Visible_Problem_Title"),
      ).then(
        ({ value }) => {
          api
            .makeContestProblemPublic({ id: problemID, display_id: value })
            .catch()
        },
        () => {},
      )
    },
    updateProblem(row) {
      let data = Object.assign({}, row)
      let funcName
      if (this.contestId) {
        data.contest_id = this.contestId
        funcName = "editContestProblem"
      } else {
        funcName = "editProblem"
      }
      api[funcName](data)
        .then((res) => {
          this.InlineEditDialogVisible = false
          this.getProblemList(this.currentPage)
        })
        .catch(() => {
          this.InlineEditDialogVisible = false
        })
    },
    handleInlineEdit(row) {
      this.currentRow = row
      this.InlineEditDialogVisible = true
    },
    changeFilter(key, value) {
      this[key] = value === "all" ? "" : value
      const query = { ...this.$route.query }
      for (const [name, filter] of [
        ["source", this.sourceFilter],
        ["visible", this.visibleFilter],
      ]) {
        if (filter) {
          query[name] = filter
        } else {
          delete query[name]
        }
      }
      if (
        query.source === this.$route.query.source &&
        query.visible === this.$route.query.visible
      ) {
        this.currentChange(1)
        return
      }
      this.$router.replace({ query }).catch((error) => {
        if (error.name !== "NavigationDuplicated") {
          this.$error("필터를 적용하지 못했습니다")
        }
      })
    },
    hideBOJProblems() {
      api.getActiveBOJProblemCount().then((res) => {
        const count = res.data.data.count
        if (!count) {
          this.$warning("활성화된 백준 문제가 없습니다")
          return
        }
        this.$prompt(
          `활성화된 백준 문제 ${count}개를 모두 비활성화합니다. 사용자는 더 이상 이 문제들을 볼 수 없습니다. 계속하려면 아래에 "백준 비활성화"를 정확히 입력해 주세요.`,
          "백준 문제 전체 비활성화",
          {
            type: "warning",
            confirmButtonText: "비활성화",
            cancelButtonText: "취소",
            confirmButtonClass: "el-button--danger",
            inputPlaceholder: "백준 비활성화",
            inputValidator: (value) => value === "백준 비활성화",
            inputErrorMessage: '"백준 비활성화"를 정확히 입력해 주세요.',
          },
        ).then(
          () => {
            api.hideBOJProblems().then(() => {
              this.getProblemList(this.currentPage)
            })
          },
          () => {},
        )
      })
    },
    previewProblem(row) {
      this.previewProblemData = row
      this.previewDialogVisible = true
    },
    changeVisibility(visible) {
      const ids = this.selectedProblems.map((problem) => problem.id)
      api.changeProblemVisibility({ ids, visible }).then(() => {
        this.getProblemList(this.currentPage)
      })
    },
    downloadTestCase(problemID) {
      let url = "/admin/test_case?problem_id=" + problemID
      utils.downloadFile(url)
    },
    getPublicProblem() {
      api.getProblemList()
    },
  },
  watch: {
    $route(newVal, oldVal) {
      this.contestId = newVal.params.contestId
      this.routeName = newVal.name

      // Update only when the router requires a problem list
      if (PROBLEM_LIST_ROUTES.includes(this.routeName)) {
        const { source, visible } = newVal.query
        this.sourceFilter = source || ""
        this.visibleFilter = visible || ""
        if (
          source !== oldVal.query.source ||
          visible !== oldVal.query.visible
        ) {
          this.currentChange(1)
        } else {
          this.getProblemList(this.currentPage)
        }
      }
    },
    keyword() {
      this.currentChange(1)
    },
  },
}
</script>

<style scoped lang="less">
.filter-col {
  flex: 0 0 120px;
  margin-right: 15px;
}
</style>
