<template>
  <div class="sidebar-section">
    <div class="sidebar-card">
      <div class="sidebar-header">
        <span class="sidebar-title">실시간 랭킹</span>
        <span class="sidebar-more" @click="goRanking">더보기 →</span>
      </div>

      <div v-if="loading" class="skeleton-list">
        <div class="skeleton-item" v-for="i in 5" :key="i" />
      </div>

      <template v-else-if="rankingItems.length > 0">
        <div
          class="rank-item"
          v-for="(user, index) in rankingItems"
          :key="index"
          @click="goUser(user.username)"
        >
          <span class="rank-num" :class="rankClass(index)">{{ index + 1 }}</span>
          <img class="rank-avatar" :src="user.avatar" :alt="user.username" />
          <span class="rank-name">{{ user.username }}</span>
          <span class="rank-score">{{ user.total_score }}</span>
        </div>
      </template>

      <div v-else class="empty-text">랭킹 데이터가 없습니다.</div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"

export default {
  name: "HomeRankingSidebar",
  data() {
    return {
      rankingItems: [],
      loading: true,
    }
  },
  mounted() {
    api.getHomeRealTimeRanking().then(
      (res) => {
        this.rankingItems = (res.data.data || []).slice(0, 5)
        this.loading = false
      },
      () => {
        this.loading = false
      },
    )
  },
  methods: {
    goRanking() {
      this.$router.push({ name: "acm-rank" })
    },
    goUser(username) {
      this.$router.push({ name: "user-home", params: { username } })
    },
    rankClass(index) {
      if (index === 0) return "rank-num--gold"
      if (index === 1) return "rank-num--silver"
      if (index === 2) return "rank-num--bronze"
      return ""
    },
  },
}
</script>

<style scoped lang="less">
.sidebar-section {
  padding: 40px 0 0;
  flex-shrink: 0;
}

.sidebar-card {
  background-color: #ffffff;
  border: 1px solid #e5e5ed;
  border-radius: 20px;
  padding: 20px 20px;
  height: 100%;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 700;
  color: #14141f;
}

.sidebar-more {
  font-size: 12px;
  font-weight: 500;
  color: #5b64ed;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 6px;
  border-radius: 8px;
  margin: 0 -6px;
  cursor: pointer;
  transition: background-color 0.15s;

  & + & {
    border-top: 1px solid #f4f4f8;
  }

  &:hover {
    background-color: #f8f8fc;

    .rank-name {
      color: #5b64ed;
    }
  }
}

.rank-num {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #9999a6;
  background-color: #f4f4f8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &--gold {
    background-color: #fff8e6;
    color: #d97706;
  }

  &--silver {
    background-color: #f4f4f8;
    color: #6b7280;
  }

  &--bronze {
    background-color: #fdf3ee;
    color: #b45309;
  }
}

.rank-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  border: 1px solid #e5e5ed;
}

.rank-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: #14141f;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  transition: color 0.15s;
}

.rank-score {
  font-size: 12px;
  font-weight: 600;
  color: #5b64ed;
  flex-shrink: 0;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-item {
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(90deg, #f0f0f4 25%, #e8e8f0 50%, #f0f0f4 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

.empty-text {
  font-size: 13px;
  color: #9999a6;
  padding: 20px 0;
  text-align: center;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
