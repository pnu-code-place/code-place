<template>
  <div class="notice-section">
    <div class="notice-card">
      <!-- 코드플레이스 공지 -->
      <div class="notice-block">
        <div class="block-header">
          <div class="block-icon cp">
            <Icon type="ios-information" size="28" color="#ffffff" />
          </div>
          <div class="block-header-text">
            <span class="block-title">공지사항</span>
          </div>
          <span class="block-more" @click="goNotice">더보기 →</span>
        </div>
        <div v-if="loading" class="skeleton-list">
          <div class="skeleton-item" v-for="i in 3" :key="i" />
        </div>
        <template v-else>
          <div
            v-for="(item, idx) in cpAnnouncements"
            :key="idx"
            class="notice-item"
            :class="{ 'notice-item--pinned': item.is_pinned }"
            @click="goNoticeDetail(item)"
          >
            <span class="bullet cp-bullet" />
            <span class="pin-icon" v-if="item.is_pinned">📌</span>
            <span class="badge-new" v-if="isNew(item.create_time)">NEW</span>
            <span class="item-title">{{ item.title }}</span>
            <span class="item-date">{{ formatDate(item.create_time) }}</span>
            <Icon
              type="ios-arrow-forward"
              size="16"
              color="#c0c0d0"
              class="item-arrow"
            />
          </div>
          <div v-if="cpAnnouncements.length === 0" class="empty-text">
            공지사항이 없습니다.
          </div>
        </template>
      </div>

      <div class="row-divider" />

      <!-- AI융합교육원 공지 -->
      <div class="notice-block">
        <div class="block-header">
          <div class="block-icon ai">
            <Icon type="ios-pulse" size="28" color="#ffffff" />
          </div>
          <div class="block-header-text">
            <span class="block-title">AI융합교육원 공지사항</span>
          </div>
          <span class="block-more" @click="goSW">더보기 →</span>
        </div>
        <div v-if="aiLoading" class="skeleton-list">
          <div class="skeleton-item" v-for="i in 5" :key="i" />
        </div>
        <template v-else>
          <div
            v-for="(item, idx) in aiAnnouncements"
            :key="idx"
            class="notice-item"
            @click="goSWItem(item)"
          >
            <span class="bullet ai-bullet" />
            <span class="badge-new ai" v-if="isNew(item.pubDate)">NEW</span>
            <span class="item-title">{{ item.title }}</span>
            <span class="item-date">{{ formatDate(item.pubDate) }}</span>
            <Icon
              type="ios-arrow-forward"
              size="16"
              color="#c0c0d0"
              class="item-arrow"
            />
          </div>
          <div v-if="aiAnnouncements.length === 0" class="empty-text">
            공지사항이 없습니다.
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"

export default {
  name: "HomeNoticeProblemRow",
  data() {
    return {
      loading: false,
      aiLoading: false,
      cpAnnouncements: [],
      aiAnnouncements: [],
    }
  },
  mounted() {
    this.loadCPAnnouncements()
    this.loadAIAnnouncements()
  },
  methods: {
    loadCPAnnouncements() {
      this.loading = true
      api.getAnnouncementList(0, 3).then(
        (res) => {
          this.cpAnnouncements = res.data.data.results || []
          this.loading = false
        },
        () => {
          this.loading = false
        },
      )
    },
    loadAIAnnouncements() {
      this.aiLoading = true
      api.getSWCenterList().then(
        (res) => {
          this.aiAnnouncements = (res.data.data || []).slice(0, 5)
          this.aiLoading = false
        },
        () => {
          this.aiLoading = false
        },
      )
    },
    isNew(dateStr) {
      if (!dateStr) return false
      const diff = Date.now() - new Date(dateStr).getTime()
      return diff < 14 * 24 * 60 * 60 * 1000
    },
    formatDate(dateStr) {
      if (!dateStr) return ""
      const d = new Date(dateStr)
      return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`
    },
    goNotice() {
      this.$router.push({ name: "notice" })
    },
    goNoticeDetail(item) {
      this.$router.push({
        name: "notice-details",
        params: { noticeID: item.id },
      })
    },
    goSW() {
      window.open("https://swedu.pusan.ac.kr/swedu/16156/subview.do")
    },
    goSWItem(item) {
      window.open(
        item.link || "https://swedu.pusan.ac.kr/swedu/16156/subview.do",
      )
    },
  },
}
</script>

<style scoped lang="less">
.notice-section {
  width: 100%;
  padding: 40px 0 0;
  height: 100%;
  box-sizing: border-box;
}

.notice-card {
  background-color: #ffffff;
  border: 1px solid #e5e5ed;
  border-radius: 20px;
  overflow: hidden;
  height: 100%;
}

.notice-block {
  padding: 16px 28px;
}

.block-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 8px;
}

.block-icon {
  width: 54px;
  height: 54px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.cp {
    background-color: #5b64ed;
  }

  &.ai {
    background-color: #34c175;
  }
}

.block-header-text {
  flex: 1;
}

.block-title {
  font-size: 18px;
  font-weight: 700;
  color: #14141f;
}

.block-more {
  font-size: 13px;
  font-weight: 500;
  color: #5b64ed;
  cursor: pointer;
  flex-shrink: 0;

  &:hover {
    text-decoration: underline;
  }
}

.row-divider {
  height: 1px;
  background-color: #f0f0f6;
  margin: 0 28px;
}

.notice-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 8px;
  cursor: pointer;
  border-radius: 8px;
  margin: 0 -8px;
  transition: background-color 0.15s;

  &:hover {
    background-color: #f0eeff;

    .item-title {
      color: #5b64ed;
    }

    .item-arrow {
      color: #5b64ed;
    }
  }

  & + & {
    border-top: 1px solid #f4f4f8;
  }

  &--pinned {
    background-color: #f4f3ff;

    &:hover {
      background-color: #eceaff;
    }

    .bullet.cp-bullet {
      background-color: #5b64ed;
    }
  }
}

.bullet {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;

  &.cp-bullet {
    background-color: #5b64ed;
  }

  &.ai-bullet {
    background-color: #16a34a;
  }
}

.pin-icon {
  font-size: 12px;
  flex-shrink: 0;
  line-height: 1;
}

.badge-new {
  font-size: 10px;
  font-weight: 700;
  color: #ffffff;
  background-color: #5b64ed;
  border-radius: 99px;
  padding: 2px 7px;
  flex-shrink: 0;
  letter-spacing: 0.3px;

  &.ai {
    background-color: #16a34a;
  }
}

.item-title {
  font-size: 14px;
  color: #333345;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  transition: color 0.15s;
}

.item-date {
  font-size: 12px;
  color: #b0b0c0;
  flex-shrink: 0;
}

.item-arrow {
  flex-shrink: 0;
  transition: color 0.15s;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-item {
  height: 18px;
  border-radius: 6px;
  background: linear-gradient(90deg, #f0f0f4 25%, #e8e8f0 50%, #f0f0f4 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

.empty-text {
  font-size: 13px;
  color: #9999a6;
  padding: 16px 0;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
