<template>
  <div class="notice-section">
    <div class="notice-card">
      <!-- 헤더 -->
      <div class="notice-header">
        <span class="header-title">공지사항</span>
        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            class="tab-btn"
            :class="{ active: activeTab === tab.value }"
            @click="activeTab = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>
        <span class="more-link" @click="goNotice">더보기 →</span>
      </div>

      <!-- 바디 -->
      <div class="notice-body">
        <!-- Code Place 공지 -->
        <div class="notice-col" v-show="activeTab === 'all' || activeTab === 'codeplace'">
          <div class="col-label" style="color: #5b64ed">Code Place 공지</div>
          <div v-if="loading" class="skeleton-list">
            <div class="skeleton-item" v-for="i in 3" :key="i" />
          </div>
          <template v-else>
            <div
              v-for="(item, idx) in cpAnnouncements"
              :key="idx"
              class="notice-item"
              @click="goNotice"
            >
              <span class="badge-new" v-if="isNew(item.create_time)">NEW</span>
              <span class="badge-num" v-else>{{ idx + 1 }}</span>
              <span class="item-title">{{ item.title }}</span>
            </div>
            <div v-if="cpAnnouncements.length === 0" class="empty-text">공지사항이 없습니다.</div>
          </template>
        </div>

        <div class="col-divider" v-show="activeTab === 'all'" />

        <!-- AI 공지 -->
        <div class="notice-col" v-show="activeTab === 'all' || activeTab === 'ai'">
          <div class="col-label" style="color: #5b64ed">
            AI융합교육원 공지 <span class="col-label-sub">(외부 링크)</span>
          </div>
          <div v-if="aiLoading" class="skeleton-list">
            <div class="skeleton-item" v-for="i in 3" :key="i" />
          </div>
          <template v-else>
            <div
              v-for="(item, idx) in aiAnnouncements"
              :key="idx"
              class="notice-item"
              @click="goNotice"
            >
              <Icon type="ios-share-outline" size="15" color="#5b64ed" class="ext-icon" />
              <span class="item-title">{{ item.title }}</span>
              <span class="item-date">{{ formatDate(item.create_time) }}</span>
            </div>
            <div v-if="aiAnnouncements.length === 0" class="empty-text">공지사항이 없습니다.</div>
          </template>
        </div>
      </div>

      <!-- 푸터 -->
      <div class="notice-footer" @click="goNotice">
        🔔&nbsp; 더 많은 공지사항 확인하기 →
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
      activeTab: "all",
      tabs: [
        { label: "전체", value: "all" },
        { label: "Code Place 공지", value: "codeplace" },
        { label: "AI융합교육원 공지", value: "ai" },
      ],
      loading: false,
      aiLoading: false,
      cpAnnouncements: [],
      aiAnnouncements: [],
    }
  },
  mounted() {
    this.loadAnnouncements()
  },
  methods: {
    loadAnnouncements() {
      this.loading = true
      this.aiLoading = true
      api.getAnnouncementList(0, 10).then(
        (res) => {
          const all = res.data.data.results || []
          this.cpAnnouncements = all.slice(0, 5)
          this.aiAnnouncements = all.slice(5, 10)
          this.loading = false
          this.aiLoading = false
        },
        () => {
          this.loading = false
          this.aiLoading = false
        },
      )
    },
    isNew(dateStr) {
      if (!dateStr) return false
      const diff = Date.now() - new Date(dateStr).getTime()
      return diff < 7 * 24 * 60 * 60 * 1000
    },
    formatDate(dateStr) {
      if (!dateStr) return ""
      const d = new Date(dateStr)
      return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`
    },
    goNotice() {
      this.$router.push({ name: "notice" })
    },
  },
}
</script>

<style scoped lang="less">
.notice-section {
  width: 100%;
  padding: 20px 0 0;
}

.notice-card {
  background-color: #ffffff;
  border: 1px solid #e5e5ed;
  border-radius: 20px;
  overflow: hidden;
}

.notice-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 28px 16px;
  border-bottom: 1px solid #f0f0f6;
}

.header-title {
  font-size: 16px;
  font-weight: 700;
  color: #14141f;
  flex-shrink: 0;
}

.tabs {
  display: flex;
  gap: 6px;
}

.tab-btn {
  height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid #e5e5ed;
  background-color: #ffffff;
  color: #59596b;
  transition: all 0.15s;

  &.active {
    background-color: #5b64ed;
    border-color: #5b64ed;
    color: #ffffff;
  }

  &:hover:not(.active) {
    border-color: #b8baed;
    color: #5b64ed;
  }
}

.more-link {
  margin-left: auto;
  font-size: 13px;
  font-weight: 500;
  color: #5b64ed;
  cursor: pointer;
  flex-shrink: 0;

  &:hover {
    text-decoration: underline;
  }
}

.notice-body {
  display: flex;
  padding: 20px 28px;
  gap: 0;
  min-height: 160px;
}

.notice-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
}

.col-divider {
  width: 1px;
  background-color: #f0f0f6;
  margin: 0 28px;
  flex-shrink: 0;
}

.col-label {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 14px;
}

.col-label-sub {
  font-size: 11px;
  font-weight: 400;
  color: #9999a6;
  margin-left: 4px;
}

.notice-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 0;
  cursor: pointer;
  border-top: 1px solid #f4f4f8;

  &:hover .item-title {
    color: #5b64ed;
  }
}

.badge-new {
  font-size: 10px;
  font-weight: 700;
  color: #5b64ed;
  background-color: #eeeaff;
  border-radius: 6px;
  padding: 2px 7px;
  flex-shrink: 0;
}

.badge-num {
  width: 22px;
  height: 22px;
  border: 1px solid #d0d0e0;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #6b6b8a;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ext-icon {
  flex-shrink: 0;
}

.item-title {
  font-size: 13px;
  color: #333345;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  transition: color 0.15s;
}

.item-date {
  font-size: 11px;
  color: #9999a6;
  flex-shrink: 0;
}

.notice-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 52px;
  background-color: #f5f4ff;
  font-size: 13px;
  font-weight: 600;
  color: #5b5b7a;
  cursor: pointer;
  transition: background-color 0.15s;

  &:hover {
    background-color: #ebe9ff;
  }
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-item {
  height: 20px;
  border-radius: 6px;
  background: linear-gradient(90deg, #f0f0f4 25%, #e8e8f0 50%, #f0f0f4 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

.empty-text {
  font-size: 13px;
  color: #9999a6;
  padding: 20px 0;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
