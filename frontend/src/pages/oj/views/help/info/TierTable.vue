<script>
import {TierImageSrc} from "../../../../../utils/constants";

export default {
  name: "TierTable",
  data() {
    return {
      tierInfo: [
        {
          name: "Sprout",
          minScore: 0,
          maxScore: 1000,
          imageSrc: TierImageSrc.sprout
        },
        {
          name: "Bronze1",
          minScore: 1000,
          maxScore: 2000,
          imageSrc: TierImageSrc.bronze1
        },
        {
          name: "Silver1",
          minScore: 2000,
          maxScore: 3000,
          imageSrc: TierImageSrc.silver1
        },
        {
          name: "Gold1",
          minScore: 3000,
          maxScore: 4000,
          imageSrc: TierImageSrc.gold1
        },
        {
          name: "Platinum1",
          minScore: 4000,
          maxScore: 5000,
          imageSrc: TierImageSrc.platinum1
        },
        {
          name: "Diamond1",
          minScore: 5000,
          maxScore: 6000,
          imageSrc: TierImageSrc.diamond1
        }
      ],
    }
  },
  methods: {
    getTierRange(tier) {
      return `${tier.minScore} ~ ${tier.maxScore}`;
    }
  }
}
</script>

<template>
  <table class="tier-table">
    <thead>
    <tr>
      <th class="header-tier">티어</th>
      <th class="header-description">점수</th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="tier in tierInfo">
      <td>
        <img :src="tier.imageSrc" alt="tier mark">
        {{ tier.name }}
      </td>
      <td class="tier-range">{{ getTierRange(tier) }}</td>
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

        &.tier-range{
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
