<script>
import api from "../../../api";
import {comma} from "../../../../../utils/utils";

export default {
  data() {
    return {
      isLoading: true,
      majorRankList: [],
      AMOUNT_TO_DISPLAY: 7

    }
  },
  methods: {
    init() {
      this.getMajorRankList()
    },
    getMajorRankList() {
      this.isLoading = true
      api.getMajorRankList(this.AMOUNT_TO_DISPLAY).then(res => {
        this.majorRankList = res.data.data.results
        // item의 rank에 따라서 정렬
        this.majorRankList.sort((a, b) => a.rank - b.rank)
        this.isLoading = false
      })
    },
    comma
  },
  mounted() {
    this.init()
  }
}
</script>

<template>
  <table>
    <tr>
      <th class="rank">{{ $t('m.Rank') }}</th>
      <th class="major">{{ $t('m.Major') }}</th>
      <th class="score">{{ $t('m.Total_Score') }}</th>
    </tr>
    <tbody>
    <tr v-for="(major, index) in this.majorRankList" :key="index">
      <td class="rank">{{ major.rank }}</td>
      <td class="major">{{ major.major }}</td>
      <td class="score">{{ comma(major.score) }}</td>
    </tr>
    </tbody>
  </table>
</template>

<style scoped lang="less">
table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;

  th {
    padding: 5px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 14px;
    color: #666;

    &.rank {
      width: 15%;
    }

    &.major {
      width: 60%;
      text-align: left;
      padding: 0 10px;
    }

    &.score {
      width: 25%;
      text-align: left;
    }
  }

  tbody {
    tr {
      border-top: 1px solid #dedede;

      td {
        padding: 10px 0;
        font-size: 13px;
        color: #666;

        &.rank {
          text-align: center;
        }

        &.major {
          padding: 0 10px;
        }

        &.score {

        }
      }
    }
  }
}
</style>
