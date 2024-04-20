<script>
import api from "../../../api";
import utils, {comma} from "../../../../../utils/utils";
import Pagination from "../../../components/Pagination.vue";
import {push} from "echarts/lib/component/dataZoom/history";
import MajorRankItem from "./MajorRankItem.vue";

export default {
  name: 'MajorRank',
  components: {MajorRankItem, Pagination},
  data() {
    return {
      isLoading: true,
      majorRankList: [],
      offset: 0,
      limits: 100,
      total: 0,
      query: {
        page: 1,
        limit: 10
      }
    }
  },
  methods: {
    push,
    init() {
      let query = this.$route.query
      this.query = Object.assign(this.query, query)
      this.offset = parseInt((this.query.page - 1) * this.query.limit) || 0
      this.limits = parseInt(this.query.limit) || 10
      this.getMajorRankList()
    },
    getMajorRankList() {
      this.isLoading = true
      api.getMajorRankList(this.offset, this.limits).then(res => {
        this.majorRankList = res.data.data.results
        // item의 rank에 따라서 정렬
        this.majorRankList.sort((a, b) => a.rank - b.rank).slice(0, 5)
        this.total = res.data.data.total
        this.isLoading = false
      })
    },
    comma,
    pushRouter() {
      console.log(this.query)
      this.$router.push({
        name: 'major-rank',
        query: utils.filterEmptyValue(this.query)
      })
    }
  },
  mounted() {
    this.init()
  }
}
</script>

<template>
  <div class="major-rank">
    <div class="table">
      <div class="table-header">
        <div class="rank">{{ $t('m.Rank') }}</div>
        <div class="major">{{ $t('m.Major') }}</div>
        <div class="score">{{ $t('m.Total_Score') }}</div>
        <div class="people">{{ $t('m.Num_People') }}</div>
      </div>
      <div class="table-body">
        <major-rank-item v-for="(major, index) in this.majorRankList" :major="major" :key="index"/>
      </div>
    </div>
    <Pagination
      :total="this.total"
      :limit="10"
      :page="1"
      @onChange="pushRouter"
      @on-page-size-change="pushRouter">
    </Pagination>
  </div>
</template>

<style scoped lang="less">
.major-rank {
  width: 100%;
  background-color: var(--box-background-color);
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;

  .table-header {
    display: flex;
    justify-content: space-around;
    padding: 5px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 16px;
    font-weight: 500;
    color: #666;

    & > .rank {
      width: 15%;
      text-align: center;
    }

    & > .major {
      width: 60%;
      text-align: left;
      padding: 0 10px;
    }

    & > .score {
      width: 5%;
      text-align: right;
    }

    & > .people {
      width: 15%;
      text-align: center;
    }
  }

  .table-body {

  }
}
</style>
