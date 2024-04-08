<template>
  <div class="rankingBox">
    <div class="rankingBoxHeader">
      <span>실시간 랭킹</span>
      <div class="plusDiv" @click="handleRoute('acm-rank')" v-if="this.rankingItems.length >= 10">
        <Icon type="android-add" size="13" color="#7a7a7a"></Icon>
        <span>더보기</span>
      </div>
    </div>
    <div style="padding: 10px; height: 100%">
      <template v-if="this.rankingItems.length == 1">
        <div style="text-align: center; height: 80%; display: flex; align-items: center; justify-content: center">
          표시할 데이터가 충분하지 않습니다.
        </div>
      </template>
      <template v-else>
        <table>
          <tr>
            <th class="rank">순위</th>
            <th class="name">이름</th>
            <th class="score">{{ $t('m.Total_Score') }}</th>
          </tr>
          <tbody>
          <tr v-for="(user, index) in this.rankingItems" :key="index">
            <template v-if="(index + 1) <= 3">
              <td class="rank">
                <img alt="" :src="getAwardImageSrc(index+1)" width="12px"/>
              </td>
            </template>
            <template v-else>
              <td class="rank">{{ index + 1 }}</td>
            </template>
            <td class="name">{{ user.username }}</td>
            <td class="score">{{ user.total_score }}</td>
          </tr>
          </tbody>
        </table>
      </template>
    </div>
  </div>
</template>

<script>
import testRealTimeRankingDTO from "../general/testRealTimeRankingDTO";
import api from "../../api";
import {getAwardImageSrc, getTierImageSrc} from "../../../../utils/constants";

export default {
  name: 'HomeRankingBox',
  data () {
    return {
      rankingItems: [],
      isLoading: true,
    }
  },
  mounted() {
    this.init()
  },
  methods:{
    getTierImageSrc,
    getAwardImageSrc,
    handleRoute(route) {
      this.$router.push({name: route});
    },
    init() {
      api.getHomeRealTimeRanking()
        .then((res)=>{
          console.log(res)
          this.rankingItems = res.data.data
        })
    }
  }
}
</script>

<style scoped lang="less">

.rankingBox {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 510px;

  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .rankingBoxHeader {
    padding: 15px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    //border-bottom: 1px solid #dedede;

    span:first-child {
      font-weight: 650;
      font-size: 15px;
    }

    span:nth-child(2) {
      color: #7a7a7a;
      font-size: 12px;
    }

    .plusDiv{
      cursor: pointer;
    }
  }
}
.rankingBox:hover{
  border: 1px solid #cccccc;
}

table {
  width: 100%;
  border-collapse: collapse;
  //margin: 20px 0;
  th {
    padding: 3px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 14px;
    color: #666;

    &.rank {
      width: 20%;
    }

    &.name {
      width: 50%;
      text-align: left;
      padding: 0 10px;
    }

    &.score {
      width: 30%;
      text-align: center;
    }
  }

  tbody {
    tr {
      border-top: 1px solid #efefef;

      td {
        padding: 10px 0;
        font-size: 13px;
        color: #666;

        &.rank {
          text-align: center;
        }

        &.name {
          text-align: left;
          padding: 0 10px;
          font-weight: 560;
        }

        &.score {
          text-align: center;
        }
      }
    }
  }
}
</style>
