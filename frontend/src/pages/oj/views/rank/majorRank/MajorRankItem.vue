<script>
import {comma} from "../../../../../utils/utils";
import MajorRankPerson from "./MajorRankPerson.vue";

export default {
  name: 'MajorRankItem',
  components: {MajorRankPerson},
  methods: {
    comma,
    printUsers() {
      console.log(this.major)
      console.log(this.major.people.length)
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
  computed: {
    peopleNum() {
      return this.major.people.length
    }
  }
}
</script>

<template>
  <div class="major-rank-item">
    <div class="major-info" @click="printUsers">
      <div class="rank vertical-center horizontal-center">{{ major.rank }}{{$t("m.Th")}}</div>
      <div class="major vertical-center">{{ major.major }}
        <div class="users">
          <major-rank-person v-for="(user, index) in this.major.people" :ranking="index+1" :user="user" :key="index"  :user-num="peopleNum"/>
        </div>
      </div>
      <div class="score vertical-center">{{ comma(major.score) }}{{$t("m.Point")}}</div>
      <div class="people vertical-center">{{ comma(major.people.length) }}{{$t("m.People")}}</div>
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
  border-top: 1px solid #dedede;
  padding: 5px 0;
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
    justify-content: end;
  }

  & > .people {
    width: 15%;
    text-align: center;
    justify-content: center;
  }
}
</style>
