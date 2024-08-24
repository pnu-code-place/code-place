<script>

import TopRanker from "./TopRanker.vue";
import UserList from "./UserRankList.vue";
import Pagination from "../../components/Pagination.vue";
import SurgeRankList from "./SurgeRank.vue";
import MajorRankList from "./majorRank/MajorRank.vue";
import {RULE_TYPE} from "../../../../utils/constants";
import api from "../../api";
import utils from "../../../../utils/utils";
import ErrorSign from "../general/ErrorSign.vue";

export default {
  name: 'UserRank',
  components: {
    ErrorSign,
    Pagination, UserList, SurgeRankList, MajorRankList, TopRanker
  },
  data() {
    return {
      isLoading: false,
      error: null,

      total: 0,
      limit: 10,
      query: {
        page: 1,
        limit: 10
      },
      dataRank: [],
      topUsers: {
        '1': {
          username: 'username',
          avatar: 'https://cdn-icons-png.flaticon.com/512/473/473406.png',
          score: 0,
          solved: 0,
          accuracy: 0.0
        },
        '2': {
          username: 'username',
          avatar: 'https://cdn-icons-png.flaticon.com/512/473/473406.png',
          score: 0,
          solved: 0,
          accuracy: 0.0
        },
        '3': {
          username: 'username',
          avatar: 'https://cdn-icons-png.flaticon.com/512/473/473406.png',
          score: 0,
          solved: 0,
          accuracy: 0.0
        }
      }
    }
  },
  mounted() {
    this.init()
    this.getTopUsers()
  },
  computed: {
    offset() {
      if (this.$route.query.offset === undefined) {
        return 3
      }
      return this.$route.query.offset
    },
    limit() {
      if (this.$route.query.limit === undefined) {
        return 10
      }
      return this.$route.query.limit
    }
  },
  methods: {
    getRankData() {
      let offset = (this.query.page - 1) * this.query.limit + 3
      this.isLoading = true
      api.getUserRank(offset, this.limit, RULE_TYPE.ACM)
        .then(res => {
          this.total = res.data.data.total-3
          this.dataRank = res.data.data.results
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
    pushRouter() {
      this.$router.push({
        name: 'user-rank',
        query: utils.filterEmptyValue(this.query)
      })
    },
    init() {
      let query = this.$route.query
      this.query.page = parseInt(query.page) || 1
      if (this.query.page < 1) {
        this.query.page = 1
      }
      this.query.limit = parseInt(query.limit) || 10
      this.getRankData()
    },
    getTopUsers() {
      api.getUserRank(0, 3).then(res => {
        this.topUsers = res.data.data.results
      })
    },
  },
  watch: {
    '$route.query': {
      handler: 'init',
      immediate: true
    }
  }
}
</script>

<template>
  <div class="contents-wrapper">
    <ErrorSign v-if="this.error" :code="this.error.code || 404" :description="this.error.description || ''"
               :solution="this.error.solution || ''"/>
    <div class="contents" v-else>
      <div class="top-users">
        <div class="top-user sub-top">
          <h2>{{ $t('m.TOP_2') }}</h2>
          <TopRanker :user="this.topUsers[1]" :loading="isLoading" :rank="2"></TopRanker>
        </div>
        <div class="top-user">
          <h2>{{ $t('m.TOP_1') }}</h2>
          <TopRanker :user="this.topUsers[0]" :loading="isLoading" :rank="1"></TopRanker>
        </div>
        <div class="top-user sub-top">
          <h2>{{ $t('m.TOP_3') }}</h2>
          <TopRanker :user=this.topUsers[2] :loading="isLoading" :rank="3"></TopRanker>
        </div>
      </div>
      <UserList :userList="dataRank" :is-loading="isLoading" :limit="limit"/>
      <Pagination
        :total="total" :page-size.sync="query.limit" :current.sync="query.page"
        @on-change="pushRouter" @on-page-size-change="pushRouter"
        :show-sizer="true">
      </Pagination>
    </div>
  </div>
</template>

<style scoped lang="less">

.contents-wrapper {
  width: 100%;
}

.contents {
  width: 100%;
  background-color: var(--box-background-color);

  .top-users {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
    gap: 30px;

    .sub-top {
      margin-top: 60px;
    }

    .top-user {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
  }
}
</style>
