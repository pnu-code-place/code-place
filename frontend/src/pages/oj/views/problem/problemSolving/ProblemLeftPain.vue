<template>
  <div class="left-pane-container">
    <div class="tab-headers">
      <div
        class="tab-header"
        :class="{ active: activeTab === 'problem' }"
        @click="setActiveTab('problem')"
      >
        문제 설명
      </div>
      <div
        class="tab-header"
        :class="{ active: activeTab === 'submissions' }"
        @click="setActiveTab('submissions')"
      >
        제출 현황
      </div>
    </div>

    <div class="tab-content">
      <ProblemDetailFlexibleContainer
        v-if="activeTab === 'problem'"
        :problem="problem"
        :contestID="contestID"
      />
      <SubmissionList
        v-if="activeTab === 'submissions'"
        :problemID="problemID"
        :contestID="contestID"
      />
    </div>
  </div>
</template>

<script>
import ProblemDetailFlexibleContainer from './problemSolvingComponent/ProblemDetailFlexibleContainer.vue';
import SubmissionList from './problemSolvingComponent/SubmissionList.vue';

export default {
  name: "ProblemLeftPain",
  props: {
    problemID: String,
    contestID: String,
    problem: Object,
  },
  data() {
    return {
      problem: {
        title: '',
        description: '',
        hint: '',
        my_status: '',
        template: {},
        languages: [],
        created_by: {
          username: ''
        },
        difficulty: '',
        tags: [],
        io_mode: {'io_mode': 'Standard IO'}
      },
      activeTab: 'problem',
    }
  },
  methods: {
    init() {
      this.activeTab = 'problem';
      this.problem =
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    }
  }
}
</script>

<style lang="less">
.tab-headers {
  display: flex;
  // border-bottom: 1px solid #e0e0e0;
  // margin-bottom: 15px;
}

.tab-header {
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-header.active {
  border-bottom-color: #007bff;
  color: #007bff;
  font-weight: 600;
}

.tab-header:hover {
  background-color: #f8f9fa;
}

.tab-content {
  height: calc(100% - 50px);
  overflow-y: auto;
}
</style>
