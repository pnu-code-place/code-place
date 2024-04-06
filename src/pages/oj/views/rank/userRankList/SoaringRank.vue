<template>
  <div class="soaring-rank">
    <UserList :userList="surgeUsers" :is-loading="isLoading" :limit="limit"/>
    <Pagination :total="total" :page-size.sync="limit" :current.sync="page"
                @on-change="getSurgeUsers" show-sizer
                @on-page-size-change="getSurgeUsers(1)"></Pagination>
  </div>
</template>

<script>
import api from "../../../api";
import SkeletonBox from "../../../components/SkeletonBox.vue";
import {comma} from "../../../../../utils/utils";
import RankList from "./UserRankList.vue";
import Pagination from "../../../components/Pagination.vue";
import UserList from "./UserRankList.vue";

export default {
  name: 'SoaringRank',
  components: {UserList, Pagination, RankList, SkeletonBox},
  data() {
    return {
      AMOUNT_TO_DISPLAY: 7,
      surgeUsers: [],
      total: 0,
      isLoading: true,
      limit: 30,
      page: 1
    }
  },
  methods: {
    init() {
      this.getSurgeUsers()
    },
    getSurgeUsers() {
      this.isLoading = true
      api.getSurgeUsers(this.AMOUNT_TO_DISPLAY).then(res => {
        this.surgeUsers = res.data.data.results
        // item의 rank에 따라서 정렬
        this.surgeUsers.sort((a, b) => a.rank - b.rank)
        this.total = res.data.data.total
        this.isLoading = false
      })
    },
    comma
  },
  mounted() {
    this.init()
  },
}
</script>

<style scoped lang="less">
.soaring-rank {
  width: 100%;
}
</style>
