<template>
  <table>
    <tr>
      <th class="rank">{{ $t('m.Rank') }}</th>
      <th class="user">{{ $t('m.Users') }}</th>
      <th class="score">{{ $t('m.Score') }}</th>
    </tr>
    <tbody>
    <tr v-for="(user, index) in surgeUsers" class="user-data">
      <td class="rank">{{ index + 1 }}</td>
      <td class="user">
        <router-link :to="{name : 'user-dashboard', params:{username:user.username}}">{{ user.username }}</router-link>
      </td>
      <td class="score">
        <span>{{ comma(user.score) }}</span>
        <span class="increased-score">{{ comma(user.increasedScore) }}▲</span>
      </td>
    </tr>
    </tbody>
    <div style="width:100%; height: 10px">
      <SkeletonBox v-if="isLoading" :count="5"></SkeletonBox>
    </div>
  </table>
</template>

<script>
import api from "../../../api";
import SkeletonBox from "../../../components/SkeletonBox.vue";
import {comma} from "../../../../../utils/utils";

export default {
  name: 'SoaringRank',
  components: {SkeletonBox},
  data() {
    return {
      AMOUNT_TO_DISPLAY: 7,
      surgeUsers: [],
      total: 0,
      isLoading: true
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
table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;

  th {
    padding: 10px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 15px;
    color: #666;

    &.rank {
      width: 15%;
    }

    &.user {
      text-align: left;
      padding: 0 10px;
      width: 60%;
    }

    &.score {
      width: 25%;
      text-align: left;
    }
  }

  tbody {
    tr {
      border-top: 1px solid #dedede;

      &:hover {
        background-color: #f5f5f5;
      }

      td {
        padding: 10px 0;
        font-size: 13px;
        color: #666;

        &.rank {
          text-align: center;
        }

        &.user {
          padding: 0 10px;
        }

        &.score {

          .increased-score {
            color: #ff4d4f;
            margin-left: 5px;
            font-weight: 700;
          }
        }
      }
    }
  }
}
</style>
