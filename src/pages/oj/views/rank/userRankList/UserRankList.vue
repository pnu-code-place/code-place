<script>
import UserItem from "./UserRankItem.vue";

export default {
  name: 'RankList',
  components: {UserItem},
  props: {
    userList: {
      type: Array,
      default: []
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    limit: {
      type: Number,
      default: 30
    }
  },
}
</script>

<template>
  <table>
    <thead>
    <tr>
      <th class="col-rank">{{ $t('m.Rank') }}</th>
      <th class="col-user">{{ $t('m.Users') }}</th>
      <th class="col-major">{{ $t('m.Major') }}</th>
      <th class="col-grade">{{ $t('m.Grade') }}</th>
      <th class="col-score">{{ $t('m.Score') }}/{{ $t('m.Today_Growth')}}</th>
      <th class="col-solved">{{ $t('m.Solved_Problems') }}</th>
    </tr>
    </thead>
    <tbody>
    <tr v-if="isLoading" v-for="index in 10" :key="index" class="skeleton-row">
      <td class="skeleton-wrapper" v-for="index in 6">
        <div class="skeleton"></div>
      </td>
    </tr>
    <UserItem v-for="user in userList" :key="user.username" :user="user"></UserItem>
    </tbody>
  </table>
</template>

<style scoped lang="less">
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.skeleton-row {
  height: 50px;
  margin: 0;

  .skeleton-wrapper {
    padding: 20px 0;
    height: 87px;

    .skeleton {
      width: 100%;
      height: 100%;
      animation: loading 1s infinite;
    }
  }

  .skeleton-wrapper:nth-child(1) {
    padding-left: 20px;

    .skeleton {
      border-radius: 20px 0 0 20px;
    }
  }

  .skeleton-wrapper:last-child {
    padding-right: 20px;

    .skeleton {
      border-radius: 0 20px 20px 0;
    }
  }
}

@keyframes loading {
  0% {
    background-color: #e3e3e3;
  }
  50% {
    background-color: #f5f5f5;
  }
  100% {
    background-color: #e3e3e3;
  }
}

th {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 15px;
  color: #666;

  &:first-child {
    border-left: none;
  }

  &.col-rank {
    width: 7%;
  }

  &.col-user {
    width: 15%;
  }

  &.col-mood {
    width: 30%;
  }

  &.col-major {
    width: 12%;
  }

  &.col-grade {
    width: 10%;
  }

  &.col-score {
    width: 7%;
  }

  &.col-solved {
    width: 10%;
  }

}


</style>
