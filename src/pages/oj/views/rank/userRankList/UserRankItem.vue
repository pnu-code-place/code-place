<script>
export default {
  name: 'UserItem',
  props: {
    user: {
      type: Object,
      default: () => {
        return {
          rank: 0,
          avatar: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
          username: "username",
          major: "undefined",
          tier: "unranked",
          score: 0,
          solved: 0,
          accuracy: 0.0,
        }
      }
    }
  },
  computed: {
    accuracy() {
      return (this.user.accuracy * 100).toFixed(1) + '%'
    },
    commaScore() {
      return this.user.score.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    }
  }
}
</script>

<template>
  <tr>
    <td>{{ user.rank }}</td>
    <td class="user-info">
      <router-link :to="{name: 'user-home', params: {username :user.username}}">
        <img class='avatar' :src="user.avatar" alt="avatar">
        <span>{{ user.username }}</span>
      </router-link>
    </td>
<!--    <td><p class="mood">{{ user.mood }}</p></td>-->
    <td>{{ user.major }}</td>
    <td>{{ user.tier }}</td>
    <td>{{ this.commaScore }}</td>
    <td class="user-problem">
      <router-link :to="{name: 'user-problems', params: {username : user.username}}" class="justify-center">{{ user.solved }}</router-link>
    </td>
    <td>{{ this.accuracy }}</td>
  </tr>
</template>

<style scoped lang="less">
tr {
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  cursor: default;
  font-size: 13px;

  .user-info {
    display: flex;
    align-items: center;
  }

  &:hover {
    background-color: #f5f5f5;
  }

  td {
    padding: 10px 0;
    text-align: center;

    p {
      padding: 0 10px;
    }

    .mood {
      // 2줄 이상일 때 생략
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
  }
}

.avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  margin-right: 10px;
  background: linear-gradient(90deg, #f0f0f0 25%, #f5f5f5 50%, #f0f0f0 75%);
}

.justify-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

a {
  width: 100%;
  display: flex;
  align-items: center;
  //color: #666;
  text-decoration: none;
}
</style>
