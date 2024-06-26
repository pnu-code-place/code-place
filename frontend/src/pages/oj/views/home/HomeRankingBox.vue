<template>
  <div class="rankingBox">
    <div class="rankingBoxHeader">
      <span>{{ $t('m.Title_Home_Ranking') }} <span class="gradientSpan">{{ $t('m.Top_Three_Home_Ranking') }}</span></span>
      <div class="plusDiv" @click="handleRoute('acm-rank')" v-if="this.rankingItems.length >= 3">
        <Icon type="android-add" size="13" color="#7a7a7a"></Icon>
        <span>{{ $t('m.More_Home_Ranking') }}</span>
      </div>
    </div>
      <div class="rankingBoxBody">
      <template v-if="this.rankingItems.length <= 1">
        <div class="noData">
          {{ $t('m.No_Sufficient_Data_Home_Ranking') }}
        </div>
      </template>
      <template v-else>
        <table>
          <tr>
            <th class="idx">{{ $t('m.Rank_Home_Ranking') }}</th>
            <th class="name">{{ $t('m.User_Home_Ranking') }}</th>
            <th class="tier">{{ $t('m.Tier_Home_Ranking') }}</th>
            <th class="score">{{ $t('m.Total_Score_Home_Ranking') }}</th>
          </tr>
          <tbody>
          <tr v-for="(user, index) in this.rankingItems" :key="index" v-if="index <= 2">
            <td class="idx">
              {{index + 1 + '위'}}
            </td>
            <td class="name">
                <div class="user-wrapper" @click="goUserInfo(user.username)">
                  <img class="avatar" :src="user.avatar"/>
                  <span>
                {{ user.username }}
              </span>
                </div>
              </td>
            <template v-if="(index + 1) <= 3">
              <td class="tier">
                <ShineWrapper>
                  <img alt="" :src="TierImageSrc[user.tier]" width="25px"/>
                </ShineWrapper>
              </td>
            </template>
            <td class="score">
              <div class="user-score">
                <span class="user-score__score">{{ user.total_score }}</span>
                <span class="user-score__growth">{{user.fluctuation===0? "-":("▲" + user.fluctuation) }}
              </span>
              </div>
              </td>
          </tr>
          </tbody>
        </table>
      </template>
    </div>
  </div>
</template>

<script>
import api from "../../api";
import {TierImageSrc} from "../../../../utils/constants";
import ShineWrapper from "../../components/ShineWrapper.vue";

export default {
  name: 'HomeRankingBox',
  components: {ShineWrapper},
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
    handleRoute(route) {
      this.$router.push({name: route});
    },
    goUserInfo(username) {
      this.$router.push({name: 'user-home', params: {username: username}})
    },
    init() {
      api.getHomeRealTimeRanking()
        .then((res)=>{
          this.rankingItems = res.data.data
        })
    }
  },
  computed:{
    TierImageSrc() {
      return TierImageSrc
    },
  }
}
</script>

<style scoped lang="less">

.rankingBox {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 270px;

  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .rankingBoxHeader {
    padding: 15px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;

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

  .rankingBoxBody{
    padding: 10px;
    .noData{
      text-align: center;
      height: 80%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}
.rankingBox:hover{
  border: 1px solid #cccccc;
}

table {
  width: 100%;
  border-collapse: collapse;
  th {
    padding: 1px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 14px;
    color: #666;

    &.idx{
      width: 15%;
    }

    &.tier {
      width: 10%;
    }

    &.name {
      width: 28%;
      text-align: left;
      padding: 0 10px;
    }

    &.score {
      width: 20%;

    }
  }

  tbody {
    tr {
      border-top: 1px solid #efefef;

      td {
        padding: 10px 0;
        font-size: 13px;
        color: #666;
        text-align: center;

        &.idx{
          font-weight: 560;
          font-size: 13px;
        }

        &.name {
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          text-align: left;
          vertical-align: middle;
          padding: 0 10px;
          font-weight: 560;
          font-size: 14px;

          .user-wrapper{
            display: flex;
            align-items: center;
            cursor: pointer;

            span{
              padding-left: 10px;
            }
          }
        }

        &.score {
          .user-score {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: 700;
            color: #666;
            .user-score__score {
              font-size: 13px;
              color: #333;
            }
            .user-score__growth {
              font-size: 10px;
              color: #00aaaa;
            }
          }
        }
      }
    }
  }
}

.gradientSpan {
  font-weight: bold;
  background: linear-gradient(
    to right,
    #6266dc 20%,
    #39408e 30%,
    #3d3580 70%,
    #20345c 80%
  );
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-fill-color: transparent;
  background-size: 500% auto;
  animation: textShine 3s ease-in-out infinite alternate;
}
@keyframes textShine {
  0% {
    background-position: 0% 50%;
  }
  100% {
    background-position: 100% 50%;
  }
}
@keyframes animate {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

@avatar-radius: 50%;

.avatar {
  width: 30px;
  border-radius: @avatar-radius;
  box-shadow: 0px 0px 1px 0px;
}
</style>
