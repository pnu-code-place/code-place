<script>
import api from "../../api";
import {JUDGE_STATUS} from "../../../../utils/constants";

export default {
  name: 'SubmissionListItem',
  props: {
    item: {
      type: Object,
      default: () => {
      }
    }
  },
  computed: {
    JUDGE_STATUS() {
      return JUDGE_STATUS
    },
    submit_time() {
      // 2024-04-30T10:51:36.831239Z-> 2024-04-30 10:51:36
      return this.item.create_time.replace('T', ' ').split('.')[0]
    },
    id() {
      return this.item.id.slice(0, 12)
    },
    memory() {
      if (this.item.statistic_info.memory_cost === null || this.item.statistic_info.memory_cost === undefined) {
        return '--'
      } else {
        return this.getMemory(this.item.statistic_info.memory_cost)
      }
    },
    running_time() {
      if (this.item.statistic_info.time_cost === null || this.item.statistic_info.time_cost === undefined) {
        return '--'
      } else {
        return this.item.statistic_info.time_cost + 'ms'
      }
    },
    statusStyle() {
      return {
        backgroundColor: JUDGE_STATUS[this.item.result].color,
        color: JUDGE_STATUS[this.item.result].textColor,
        fontWeight: 'bold'
      }
    }
  },
  methods: {
    goStatus() {
      this.$router.push('/status/' + this.item.id)
    },
    goProblem() {
      this.$router.push({name: 'problem-details', params: {problemID: this.item.problem}})
    },
    goUser() {
      this.$router.push({name: 'user-home', params: {username: this.item.username}})
    },
    getMemory(memory_cost) {
      if (memory_cost > 1024 * 1024 * 1024) {
        return (memory_cost / 1024 / 1024 / 1024).toFixed(1) + 'GB'
      } else if (memory_cost > 1024 * 1024) {
        return (memory_cost / 1024 / 1024).toFixed(1) + 'MB'
      } else if (memory_cost > 1024) {
        return (memory_cost / 1024).toFixed(1) + 'KB'
      } else {
        return memory_cost + 'B'
      }
    },
  },
}

</script>

<template>
  <tr>
    <td>{{ this.submit_time }}</td>
    <td class="link" @click="this.goStatus">{{ item.id.slice(0, 12) }}</td>
    <td><button class="status-badge" :style="this.statusStyle">{{ JUDGE_STATUS[item.result].name }}</button></td>
    <td class="link" @click="this.goProblem">{{ item.problem + '번' }}</td>
    <td>{{ this.running_time }}</td>
    <td>{{ this.memory }}</td>
    <td>{{ item.language }}</td>
    <td class="link" @click="this.goUser">
      <div class="user-wrapper">
        <img class="avatar" :src="item.user_avatar"/>
        <div class="name-wrapper">
          {{ item.username }}
        </div>
      </div>
      </td>
    <!--        <td>{{ item.id }}</td>-->
    <!--        <td>{{ item.status }}</td>-->
    <!--        <td>{{ item.memory }}</td>-->
    <!--        <td>{{ item.time }}</td>-->
  </tr>
</template>

<style scoped lang="less">
tr {
  border-bottom: 1px solid #e0e0e0;
}

td {
  text-align: center;
  padding: 10px 0;
}

.link {
  color: #32306b;
  cursor: pointer;
  .user-wrapper{
    display: flex;
    justify-content: center;
    align-items: center;
    .name-wrapper{
      margin-left: 7px;
    }
  }
}

.link:hover {
  color: #32306b;
  text-decoration: underline;
}

.status-badge {
  border: none;
  color: white;
  padding: 5px 10px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 10.5px;
  cursor: pointer;
  border-radius: 5px;
}

@avatar-radius: 50%;

.avatar {
  width: 30px;
  border-radius: @avatar-radius;
  box-shadow: 0px 0px 1px 0px;
}
</style>
