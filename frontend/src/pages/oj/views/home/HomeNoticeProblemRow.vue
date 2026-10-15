<template>
  <div class="notice-section">
    <div class="notice-card">
      <!-- 헤더 (아이콘 + 제목 + 탭 + 더보기) -->
      <div class="card-header">
        <div class="header-left">
          <span class="header-title">{{ $t("m.Announcements") }}</span>
          <div class="tab-pills">
            <button
              class="tab-pill"
              :class="{ active: activeTab === 'cp' }"
              @click="activeTab = 'cp'"
            >
              {{ $t("m.CSEP") }}
            </button>
            <button
              class="tab-pill"
              :class="{ active: activeTab === 'ai' }"
              @click="activeTab = 'ai'"
            >
              {{ $t("m.SWCenter") }}
            </button>
          </div>
        </div>
        <span class="header-more" @click="goMore"> {{ $t("m.More") }} → </span>
      </div>

      <!-- 코드플레이스 공지 목록 -->
      <div class="notice-list" v-show="activeTab === 'cp'">
        <div v-if="loading" class="skeleton-list">
          <div class="skeleton-item" v-for="i in 5" :key="i" />
        </div>
        <template v-else>
          <div
            v-for="(item, idx) in cpAnnouncements"
            :key="idx"
            class="notice-item"
            :class="{ 'notice-item--pinned': item.is_pinned }"
            @click="goNoticeDetail(item)"
          >
            <span
              class="bullet"
              :class="item.is_pinned ? 'bullet--pin' : 'bullet--dot'"
            >
              <span v-if="item.is_pinned">📌</span>
              <span v-else class="dot" />
            </span>
            <span class="item-main">
              <span class="item-title" :class="{ pinned: item.is_pinned }">
                {{ item.title }}
              </span>
              <span v-if="isNew(item.create_time)" class="badge-new">
                NEW
              </span>
            </span>
            <span class="item-date">{{ formatDate(item.create_time) }}</span>
          </div>
          <div v-if="cpAnnouncements.length === 0" class="empty-text">
            {{ $t("m.No_Announcements") }}
          </div>
        </template>
      </div>

      <!-- AI융합교육원 공지 목록 -->
      <div class="notice-list" v-show="activeTab === 'ai'">
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
            <!-- 탭 간 UI 정렬 통일을 위한 불릿 점 추가-->
            <span class="bullet bullet--dot">
              <span class="dot" />
            </span>
            <span class="item-main">
              <span class="item-title">{{ item.title }}</span>
              <span v-if="isNew(item.pubDate)" class="badge-new">NEW</span>
            </span>
            <span class="item-date">{{ formatDate(item.pubDate) }}</span>
          </div>
          <div v-if="aiAnnouncements.length === 0" class="empty-text">
            {{ $t("m.No_Announcements") }}
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
      activeTab: "cp",
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
      Promise.all([
        api.getAnnouncementList(0, 5, "general"),
        api.getAnnouncementList(0, 1, "release"),
      ]).then(
        ([announcements, releases]) => {
          const generalItems = announcements.data.data.results || []
          const latestRelease = releases.data.data.results[0]

          const generalPinned = generalItems.filter((item) => item.is_pinned)
          const releasePinned =
            latestRelease && latestRelease.is_pinned ? [latestRelease] : []
          const pinnedItems = [...generalPinned, ...releasePinned].sort(
            (a, b) => new Date(b.create_time) - new Date(a.create_time),
          )

          const generalRecent = generalItems.filter((item) => !item.is_pinned)
          const releaseRecent =
            latestRelease && !latestRelease.is_pinned ? [latestRelease] : []
          const recentItems = [...generalRecent, ...releaseRecent].sort(
            (a, b) => new Date(b.create_time) - new Date(a.create_time),
          )

          this.cpAnnouncements = [...pinnedItems, ...recentItems].slice(0, 5)
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
      const t = new Date(dateStr).getTime()
      if (Number.isNaN(t)) return false
      const FIVE_DAYS = 5 * 24 * 60 * 60 * 1000
      return Date.now() - t <= FIVE_DAYS
    },
    formatDate(dateStr) {
      if (!dateStr) return ""
      const d = new Date(dateStr)
      return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`
    },
    goMore() {
      if (this.activeTab === "cp") {
        this.$router.push({ name: "notice" })
      } else {
        window.open("https://swedu.pusan.ac.kr/swedu/16156/subview.do")
      }
    },
    goNoticeDetail(item) {
      this.$router.push({
        name: "notice-details",
        params: { noticeID: item.id },
      })
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
  display: flex;
  flex-direction: column;
}

/* 헤더 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px 16px;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  min-width: 0;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
  color: #14141f;
  white-space: nowrap;
}

/* 탭 pill 버튼 */
.tab-pills {
  display: flex;
  gap: 6px;
  margin-left: 6px;
}

.tab-pill {
  font-size: 13px;
  font-weight: 500;
  color: #9999a6;
  background: #f4f4f8;
  border: 1.5px solid transparent;
  border-radius: 99px;
  padding: 5px 14px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;

  &:hover:not(.active) {
    background: #ebebf4;
    color: #555;
  }

  &.active {
    color: #5b64ed;
    background: #eeeffe;
    border-color: #c5c8f8;
    font-weight: 600;
  }
}

.header-more {
  font-size: 13px;
  font-weight: 500;
  color: #5b64ed;
  cursor: pointer;
  flex-shrink: 0;
  white-space: nowrap;

  &:hover {
    text-decoration: underline;
  }
}

/* 목록 */
.notice-list {
  flex: 1;
  padding: 2px 20px 10px;
}

.notice-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px 8px;
  cursor: pointer;
  border-radius: 10px;
  margin: 0 -8px;
  transition: background-color 0.15s;

  & + & {
    border-top: 1px solid #f4f4f8;
  }

  &:hover {
    background-color: #f4f3ff;

    .item-title {
      color: #5b64ed;
    }
  }

  &--pinned {
    background-color: #f5f4ff;

    &:hover {
      background-color: #eceaff;
    }
  }

  &--pinned + &--pinned {
    border-top: 1px solid #e8e6f8;
  }
}

/* 불릿 */
.bullet {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
}

.dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #c5c5d8;
}

.notice-item--pinned .dot {
  background-color: #5b64ed;
}

/* NEW 뱃지 */
.badge-new {
  font-size: 10px;
  font-weight: 700;
  color: #16a34a;
  background-color: #dcfce7;
  border-radius: 6px;
  padding: 2px 7px;
  flex-shrink: 0;
  letter-spacing: 0.3px;
  white-space: nowrap;
}

.item-title {
  font-size: 14px;
  color: #1a1a2e;
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  transition: color 0.15s;

  &.pinned {
    font-weight: 700;
    color: #3b3a8e;
  }
}

.item-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.item-date {
  font-size: 12px;
  color: #b0b0c0;
  flex-shrink: 0;
  white-space: nowrap;
}

/* 스켈레톤 */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 12px 0;
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
  padding: 24px 0;
  text-align: center;
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
