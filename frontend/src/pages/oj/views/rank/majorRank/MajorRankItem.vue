<script>
import {comma} from "../../../../../utils/utils";
import MajorRankPerson from "./MajorRankPerson.vue";

export default {
  name: 'MajorRankItem',
  components: {MajorRankPerson},
  methods: {
    comma,
  },
  data() {
    return {
      PEOPLE_TO_SHOW: 5
    }
  },
  props: {
    major: {
      type: Object,
      default: () => {
      }
    },
    ranking: {
      type: Number,
      default: 0
    }
  },
  computed: {
    peopleNum() {
      return this.major.people.length
    },
    rankingClass() {
      if (this.ranking === 1) {
        return 'first'
      } else if (this.ranking === 2) {
        return 'second'
      } else if (this.ranking === 3) {
        return 'third'
      }
    },
    majorRankClass() {
      return `major-info ${this.rankingClass}`
    }
  }
}
</script>

<template>
  <div class="major-rank-item">
    <div :class="this.majorRankClass">
      <div class="rank vertical-center horizontal-center">{{ major.rank }}{{$t("m.Th")}}</div>
      <div class="major vertical-center">{{ major.major }}
        <div class="users">
          <major-rank-person v-for="(user, index) in this.major.people" :ranking="index+1" :user="user" :key="index"  :user-num="peopleNum"/>
        </div>
      </div>
      <div class="score vertical-center">{{ comma(major.score) }}{{$t("m.Point")}}</div>
      <div class="people vertical-center">{{ comma(major.population) }}{{$t("m.People")}}</div>
    </div>
  </div>
</template>

<style scoped lang="less">

.vertical-center {
  display: flex;
  align-items: center;
}

.horizontal-center {
  display: flex;
  justify-content: center;
}
.major-info {
  --major-info-height: 40px;
  border-radius: calc(var(--major-info-height) / 2);
  border: 1px solid #dedede;
  box-shadow: 0 0 10px 0 rgba(0, 0, 0, 0.1);
  padding: 5px 0;
  font-size: 15px;
  font-weight: 500;
  color: #666;
  display: flex;
  justify-content: space-around;
  opacity: 0.8;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  & > .rank {
    width: 15%;
    text-align: center;
  }

  & > .major {
    width: 60%;
    display: flex;
    justify-content: space-between;
    padding: 0 10px;
    font-weight: 600;

    .users{
      display:flex;
      justify-content:end;
    }
  }

  & > .score {
    width: 5%;
    text-align: right;
    justify-content: end;
  }

  & > .people {
    width: 15%;
    text-align: center;
    justify-content: center;
  }

  &:hover {
    opacity: 1;
    transform: scale(1.02);
  }

  &.first {
    background: linear-gradient(90deg, #FAF882, #FFFFFF);
  }

  &.second {
    background: linear-gradient(90deg, #F4F4F4, #FFFFFF);
  }

  &.third {
    background: linear-gradient(90deg, #D6C68B, #FFFFFF);
  }
}
</style>
