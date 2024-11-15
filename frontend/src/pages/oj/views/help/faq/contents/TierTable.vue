<script>
import {TIER_SCORE} from "../../../../../../utils/constants";

export default {
  name: "TierTable",
  methods: {
    TIER_SCORE() {
      return TIER_SCORE
    }
  },
  data() {
    return {}
  },
}
</script>

<template>
  <table class="tier-table">
    <thead>
    <tr>
      <th class="header-tier">티어</th>
      <th class="header-description">티어 3 점수</th>
      <th class="header-description">티어 2 점수</th>
      <th class="header-description">티어 1 점수</th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="tier in TIER_SCORE()">
      <td rowspan="3">
        <img :src="tier.imageSrc" alt="tier mark">
        {{ tier.name }}
      </td>
      <td class="tier-range">{{ tier.score[3] }}</td>
      <td class="tier-range">{{ tier.score[2] }}</td>
      <td class="tier-range">{{ tier.score[1] }}</td>
    </tr>
    </tbody>
  </table>
</template>

<style scoped lang="less">
table {
  border: 1px solid #dedede;
  border-radius: 7px;
  border-collapse: collapse;

  thead {
    background-color: var(--pale-point-color);
    font-weight: bold;
    font-size: 16px;
    text-align: center;
    border-bottom: 1px solid #dedede;

    tr {
      th {
        padding: 10px;
      }
    }

    .header-tier {
      width: 100px;
    }
  }

  tbody {
    tr {
      border-bottom: 1px solid #dedede;

      td {
        &:first-child {
          display: flex;
          flex-direction: column;
          text-align: center;
          align-items: center;
          font-size: 16px;
          font-weight: bold;
          padding: 10px 12px;

          img {
            width: 60px;
          }
        }

        &.tier-range {
          padding: 10px;
          font-size: 16px;
          font-weight: bold;
          text-align: center;
        }
      }
    }

    tr:last-child {
      border-bottom: none;
    }
  }
}


</style>
