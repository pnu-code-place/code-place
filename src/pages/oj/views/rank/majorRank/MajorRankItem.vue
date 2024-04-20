<script>
import {comma} from "../../../../../utils/utils";
import MajorRankPeople from "./MajorRankPeople.vue";

export default {
  name: 'MajorRankItem',
  components: {MajorRankPeople},
  methods: {
    comma,
    toggleExtended() {
      this.isExtended = !this.isExtended
    },
  },
  data() {
    return {
      isExtended: false,
      PEOPLE_TO_SHOW: 5
    }
  },
  props: {
    major: {
      type: Object,
      default: () => {
      }
    }
  },
}
</script>

<template>
  <div class="major-rank-item">
    <div class="major-info" @click="toggleExtended">
      <div class="rank">{{ major.rank }}</div>
      <div class="major">{{ major.major }}</div>
      <div class="score">{{ comma(major.score) }}</div>
      <div class="people">{{ comma(major.people_num) }}</div>
    </div>
    <transition>
      <div class="major-people" v-if="isExtended">
        <MajorRankPeople v-for="(person, index) in major.people" :user="person" :key="person.username" :ranking="index+1"/>
      </div>
    </transition>
  </div>
</template>

<style scoped lang="less">
.major-info {
  border-top: 1px solid #dedede;
  padding: 15px 0;
  font-size: 15px;
  font-weight: 500;
  color: #666;
  display: flex;
  justify-content: space-around;
  cursor: pointer;

  &:hover {
    background-color: #f5f5f5;
  }

  & > .rank {
    width: 15%;
    text-align: center;
  }

  & > .major {
    width: 60%;
    padding: 0 10px;
  }

  & > .score {
    width: 5%;
    text-align: right;
  }

  & > .people {
    width: 15%;
    text-align: center;
  }
}

.v-enter-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.v-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.v-enter, .v-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

</style>
