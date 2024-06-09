<script>
import {comma} from "../../../../../utils/utils";
import MajorRankPeople from "./MajorRankPerson.vue";
import MajorRankPerson from "./MajorRankPerson.vue";

export default {
  name: 'MajorRankItem',
  components: {MajorRankPerson},
  methods: {
    comma,
    printUsers() {
      console.log(this.major)
    }
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
    }
  },
}
</script>

<template>
  <div class="major-rank-item">
    <div class="major-info" @click="printUsers">
      <div class="rank vertical-center"><span>{{ major.rank }}{{$t("m.Th")}}</span></div>
      <div class="major">{{ major.major }}
        <div class="users">
          <major-rank-person v-for="(user, index) in this.major.people" :ranking="index+1" :user="user"/>
        </div>
      </div>
      <div class="score">{{ comma(major.score) }}{{$t("m.Point")}}</div>
      <div class="people">{{ comma(major.people.length) }}{{$t("m.People")}}</div>
    </div>
  </div>
</template>

<style scoped lang="less">

.vertical-center {
  display:flex;
  justify-content: center;
  align-content: center;
}

.major-info {
  border-top: 1px solid #dedede;
  padding: 15px 0;
  font-size: 15px;
  font-weight: 500;
  color: #666;
  display: flex;
  justify-content: space-around;

  & > .rank {
    width: 15%;
    text-align: center;
  }

  & > .major {
    width: 60%;
    display: flex;
    justify-content: space-between;
    padding: 0 10px;

    .users{
      display:flex;
      justify-content:end;
    }
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
</style>
