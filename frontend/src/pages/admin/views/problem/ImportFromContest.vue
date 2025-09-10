<template>
  <div>
    <el-input
      v-model="keyword"
      :placeholder="$t('m.Search_Keywords')"
      prefix-icon="el-icon-search"
    >
    </el-input>
    <el-table :data="contests" v-loading="loading">
      <el-table-column
        :label="$t('m.Contest_ID')"
        width="100"
        prop="id"
      >
      </el-table-column>
      <el-table-column
        :label="$t('m.Contest_Name')"
        prop="title"
      >
      </el-table-column>
      <el-table-column
        :label="$t('m.Contest_Creator')"
        prop="created_by.username"
      >
      </el-table-column>
      <el-table-column
        :label="$t('m.Contest_Visible')"
        width="100"
        prop="visible"
      >
        <template slot-scope="scope">
          <el-tag :type="scope.row.visible ? 'success' : 'danger'">
            {{ scope.row.visible ? $t('m.Yes') : $t('m.No') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        :label="$t('m.AddProblem_Table_Option')"
        align="center"
        width="100"
        fixed="right"
      >
        <template slot-scope="{ row }">
          <icon-btn
            icon="plus"
            :name="$t('m.Import')"
            @click.native="handleImport(row.id)"
          ></icon-btn>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="page"
      layout="prev, pager, next"
      @current-change="getContestList"
      :page-size="limit"
      :total="total"
    >
    </el-pagination>
  </div>
</template>
<script>
import api from "@admin/api"

export default {
  name: "import-from-contest",
  props: ["contestID"],
  data() {
    return {
      page: 1,
      limit: 10,
      total: 0,
      loading: false,
      contests: [],
      keyword: "",
    }
  },
  mounted() {
    this.getContestList()
  },
  methods: {
    getContestList(page) {
      this.loading = true
      let params = {
        keyword: this.keyword,
        offset: (page - 1) * this.limit,
        limit: this.limit,
      }
      api
        .getContestListForProblem(params)
        .then((res) => {
          this.loading = false
          this.total = res.data.data.total
          this.contests = res.data.data.results
        })
        .catch(() => {
          this.loading = false
        })
    },
    handleImport(contestId) {
      this.$confirm(this.$t('m.Import_Contest_Problems_Confirm'), this.$t('m.Warning')).then(() => {
        api.importContestProblems(this.contestID, { from_contest_id: contestId }).then(() => {
          this.$emit("on-change")
          this.$success(this.$t('m.Import_Successfully'))
        })
      }).catch(() => {
      })
    },
  },
  watch: {
    keyword() {
      this.getContestList(this.page)
    },
  },
}
</script>
<style scoped>
.page {
  margin-top: 20px;
  text-align: right;
}
</style>
