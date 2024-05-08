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
  data() {
    return {
      rejudging: false
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
    buttonText() {
      return this.rejudging ? this.$i18n.t('m.Rejudging') : this.$i18n.t('m.Rejudge')
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
    handleRejudge(id) {
      if (this.rejudging) {
        return
      }
      this.rejudging = true
      api.submissionRejudge(id).then(res => {
        this.$success('Succeeded')
        this.getSubmissions()
      }, () => {
        this.$error('Failed')
      }).finally(() => {
        this.rejudging = false
      })
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
    <td><button class="status-badge">{{ JUDGE_STATUS[item.result].name }}</button></td>
    <td class="link" @click="this.goProblem">{{ item.problem }}</td>
    <td>{{ this.running_time }}</td>
    <td>{{ this.memory }}</td>
    <td>{{ item.language }}</td>
    <td class="link" @click="this.goUser">{{ item.username }}</td>
    <td>
      <button @click="handleRejudge(item.id)" :class="this.rejudging? 'rejudging rejudge' : 'rejudge'">{{ this.buttonText }}</button>
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
}

.link:hover {
  color: #32306b;
  text-decoration: underline;
}

button.rejudge {
  background-color: #32306b;
  border: none;
  color: white;
  padding: 5px 10px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 12px;
  cursor: pointer;
  border-radius: 5px;
}

button:hover.rejudge {
  background-color: #4a47a3;
}

.rejudging {
  background-color: #f0f0f0;
  animation: rejudging 1s infinite;
  //pointer-events: none;
  cursor: not-allowed;
}

@keyframes rejudging {
  0% {
    background-color: #5c59b8;
  }
  50% {
    background-color: #32306b;
  }
  100% {
    background-color: #5c59b8;
  }
}

.status-badge {
  background-color: #32306b;
  border: none;
  color: white;
  padding: 5px 10px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 12px;
  cursor: pointer;
  border-radius: 5px;
}
</style>
