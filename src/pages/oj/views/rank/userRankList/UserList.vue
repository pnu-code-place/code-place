<script>
import UserItem from "./UserItem.vue";

export default {
  name: 'RankList',
  components: {UserItem},
  props: {
    userList: {
      type: Array,
      default: []
    }
  },
}
</script>

<template>
  <table>
    <thead>
    <tr>
      <th class="col-rank">{{ $t('m.Rank') }}</th>
      <th class="col-user">{{ $t('m.User') }}</th>
      <th class="col-mood">{{ $t('m.Mood') }}</th>
      <th class="col-major">{{ $t('m.Major') }}</th>
      <th class="col-grade">{{ $t('m.Grade') }}</th>
      <th class="col-score">{{ $t('m.Score') }}</th>
      <th class="col-solved">{{ $t('m.Solved_Problems') }}</th>
      <th class="col-rate">{{ $t('m.AC_Rate') }}</th>
    </tr>
    </thead>
    <tbody>
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

th {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  border-left: 1px solid #f0f0f0;
  font-size: 15px;
  color: #666;

  &:first-child {
    border-left: none;
  }

  &.col-rank {
    width: 3%;
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

  &.col-rate {
    width: 5%;
  }

}


</style>
