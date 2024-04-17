<template>
  <div class="contents">
    <ErrorSign v-if="this.error" :code="this.error.code || 404" :description="this.error.description || ''"
               :solution="this.error.solution || ''"/>
    <div class="soaring-rank" v-else>
      <UserList :userList="surgeUsers" :is-loading="isLoading" :limit="limit"/>
      <Pagination :total="total" :page-size.sync="limit" :current.sync="page"
                  @on-change="getSurgeUsers" show-sizer
                  @on-page-size-change="getSurgeUsers(1)"></Pagination>
    </div>
  </div>
</template>

<script>
import api from "../../api";
import SkeletonBox from "../../components/SkeletonBox.vue";
import {comma} from "../../../../utils/utils";
import RankList from "./UserRankList.vue";
import Pagination from "../../components/Pagination.vue";
import UserList from "./UserRankList.vue";
import ErrorSign from "../general/ErrorSign.vue";

export default {
  name: 'SurgeRank',
  components: {ErrorSign, UserList, Pagination, RankList, SkeletonBox},
  data() {
    return {
      isLoading: true,
      error: null,

      total: 0,
      limit: 30,
      query: {
        page: 1,
        limit: 10
      },
      surgeUsers: []
    }
  },
  methods: {
    init() {
      this.getSurgeUsers()
    },
    getSurgeUsers() {
      this.isLoading = true
      const offset = (this.query.page - 1) * this.limit
      api.getSurgeUsers(offset, this.limit)
        .then(res => {
          this.surgeUsers = res.data.data.results
          this.total = res.data.data.total
          if (this.dataRank.length === 0) {
            this.error = {code: 404, description: '충분한 데이터가 없습니다.', solution: '잠시 후 다시 시도해 주세요.'}
          }
          this.isLoading = false
        })
        .catch(error => {
          this.error = error.response.status
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
.contents {
  width: 100%;
}

.soaring-rank {
  background-color: var(--box-background-color);
  width: 100%;
}
</style>
