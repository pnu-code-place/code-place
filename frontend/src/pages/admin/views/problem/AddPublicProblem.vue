<template>
  <div>
    <el-input
      v-model="keyword"
      :placeholder="$t('m.Search_Keywords')"
      prefix-icon="el-icon-search">
    </el-input>
    <el-table :data="problems" v-loading="loading">
      <el-table-column
        :label="$t('m.AddProblem_Table_ID')"
        width="100"
        prop="id">
      </el-table-column>
      <el-table-column
        :label="$t('m.AddProblem_Table_DisplayId')"
        width="200"
        prop="_id">
      </el-table-column>
      <el-table-column
        :label="$t('m.AddProblem_Table_Title')"
        prop="title">
      </el-table-column>
      <el-table-column
        :label="$t('m.AddProblem_Table_Option')"
        align="center"
        width="100"
        fixed="right">
        <template slot-scope="{row}">
          <icon-btn icon="plus" :name="$t('m.Icon_Add')"
                    @click.native="handleAddProblem(row)"></icon-btn>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="page"
      layout="prev, pager, next"
      @current-change="getPublicProblem"
      :page-size="limit"
      :total="total">
    </el-pagination>
  </div>
</template>
<script>
  import api from '@admin/api'

  export default {
    name: 'add-problem-from-public',
    props: ['contestID'],
    data () {
      return {
        page: 1,
        limit: 10,
        total: 0,
        loading: false,
        problems: [],
        contest: {},
        keyword: ''
      }
    },
    mounted () {
      api.getContest(this.contestID).then(res => {
        this.contest = res.data.data
        this.getPublicProblem()
      }).catch(() => {
      })
    },
    methods: {
      getPublicProblem (page) {
        this.loading = true
        let params = {
          keyword: this.keyword,
          offset: (page - 1) * this.limit,
          limit: this.limit,
          rule_type: this.contest.rule_type
        }
        api.getProblemList(params).then(res => {
          this.loading = false
          this.total = res.data.data.total
          this.problems = res.data.data.results
        }).catch(() => {
        })
      },
      handleAddProblem (problemToAdd) {
        // console.log(this.problems)
        // console.log(problemID)
        // this.$prompt(this.$t('m.AddProblem_Modal_Content'), this.$t('m.AddProblem_Modal_Title')).then(({value}) => {
        //   let data = {
        //     problem_id: problemID,
        //     contest_id: this.contestID,
        //     display_id: value
        //   }
        //   api.addProblemFromPublic(data).then(() => {
        //     this.$emit('on-change')
        //   }, () => {
        //   })
        // }, () => {
        // })
        let data = {
          problem_id: problemToAdd.id,
          contest_id: this.contestID,
          display_id: problemToAdd._id
        }
        api.addProblemFromPublic(data).then(() => {
          this.$emit('on-change')
        }).catch((error) => {
          // this.$error(error)
        })
      }
    },
    watch: {
      'keyword' () {
        this.getPublicProblem(this.page)
      }
    }
  }
</script>
<style scoped>
  .page {
    margin-top: 20px;
    text-align: right
  }

</style>
