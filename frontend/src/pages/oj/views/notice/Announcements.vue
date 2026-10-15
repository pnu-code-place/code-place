<template>
  <div class="announcements">
    <div class="page-heading">
      <h1 class="title main-title">
        {{ pageTitle }}
      </h1>
      <div v-if="!isContest" class="content-tabs">
        <button
          type="button"
          :class="{ active: activeCategory === 'general' }"
          @click="setCategory('general')"
        >
          {{ $t("m.Announcements") }}
        </button>
        <button
          type="button"
          :class="{ active: activeCategory === 'release' }"
          @click="setCategory('release')"
        >
          {{ $t("m.Release_Notes") }}
        </button>
      </div>
    </div>
    <div class="announcement-container">
      <div
        class="no-announcement"
        v-if="!announcements.length"
        key="no-announcement"
      >
        <p>{{ $t("m.No_Announcements") }}</p>
      </div>
      <table v-else class="announcement-table" key="list">
        <thead>
          <tr>
            <th class="id">{{ $t("m.ID") }}</th>
            <th class="title">{{ $t("m.Title") }}</th>
            <th class="date">{{ $t("m.Date") }}</th>
            <th class="author">{{ $t("m.Author") }}</th>
          </tr>
        </thead>
        <tbody>
          <announcement-item
            v-for="announcement in announcements"
            :key="announcement.id"
            :announcement="announcement"
          >
          </announcement-item>
        </tbody>
      </table>
      <Pagination
        v-if="!isContest"
        :current="currentPage"
        :total="total"
        :page-size="limit"
        @on-change="getAnnouncementList"
      >
      </Pagination>
    </div>
  </div>
</template>

<script>
import api from "@oj/api"
import Pagination from "@oj/components/Pagination"
import AnnouncementItem from "./AnnouncementItem.vue"

export default {
  name: "NoticeAnnouncements",
  components: {
    AnnouncementItem,
    Pagination,
  },
  data() {
    return {
      limit: 10,
      total: 10,
      btnLoading: false,
      announcements: [],
      announcement: "",
      listVisible: true,
      activeCategory: "general",
      currentPage: 1,
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      this.activeCategory =
        this.$route.query.tab === "updates" ? "release" : "general"
      const savedPage = Number(sessionStorage.getItem(this.pageStorageKey)) || 1
      this.currentPage = savedPage

      if (this.isContest) {
        this.getContestAnnouncementList()
      } else {
        this.getAnnouncementList()
      }
    },
    getAnnouncementList(page = this.currentPage) {
      this.currentPage = page

      sessionStorage.setItem(this.pageStorageKey, page)

      this.btnLoading = true
      api
        .getAnnouncementList(
          (page - 1) * this.limit,
          this.limit,
          this.activeCategory,
        )
        .then(
          (res) => {
            this.btnLoading = false
            this.announcements = res.data.data.results
            this.total = res.data.data.total
          },
          () => {
            this.btnLoading = false
          },
        )
    },
    getContestAnnouncementList() {
      this.btnLoading = true
      api.getContestAnnouncementList(this.$route.params.contestID).then(
        (res) => {
          this.btnLoading = false
          this.announcements = res.data.data
        },
        () => {
          this.btnLoading = false
        },
      )
    },
    goAnnouncement(announcement) {
      this.announcement = announcement
      this.listVisible = false
    },
    setCategory(category) {
      if (this.activeCategory === category) return
      this.activeCategory = category
      this.currentPage = 1
      this.$router.replace({
        name: "notice",
        query: category === "release" ? { tab: "updates" } : {},
      })
      this.getAnnouncementList(1)
    },
  },
  computed: {
    pageTitle() {
      if (this.isContest) {
        return this.$i18n.t("m.Contest_Announcements")
      }
      return this.activeCategory === "release"
        ? this.$i18n.t("m.Release_Notes")
        : this.$i18n.t("m.Announcements")
    },
    title() {
      if (this.listVisible) {
        return this.isContest
          ? this.$i18n.t("m.Contest_Announcements")
          : this.$i18n.t("m.Announcements")
      } else {
        return this.announcement.title
      }
    },
    isContest() {
      return !!this.$route.params.contestID
    },
    pageStorageKey() {
      return `noticePage-${this.activeCategory}`
    },
  },
}
</script>

<style scoped lang="less">
.announcements {
  width: var(--global-width);

  .page-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 20px;
  }

  .title {
    margin-bottom: 0;
  }

  .content-tabs {
    display: flex;
    gap: 4px;
    padding: 4px;
    border-radius: 8px;
    background-color: #f1f1f5;

    button {
      padding: 7px 15px;
      border: 0;
      border-radius: 6px;
      color: #858594;
      background: transparent;
      font-size: 13px;
      cursor: pointer;

      &.active {
        color: #33334a;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        font-weight: 600;
      }
    }
  }

  .announcement-container {
    background-color: var(--box-background-color);
    border-radius: var(--container-border-radius);
    border: solid 1px var(--border-color);

    .announcement-table {
      width: 100%;
      border-collapse: collapse;

      th {
        background-color: var(--pale-point-color);
        color: var(--table-header-color);
        font-size: 16px;
        font-weight: 600;
        text-align: center;
        padding: 10px;
        border-bottom: solid 1px var(--border-color);
      }

      td {
        font-size: 14px;
        padding: 10px 0;
        border-bottom: solid 1px var(--border-color);
      }

      .id {
        width: 10%;
      }

      .title {
        text-align: left;
        width: 60%;
      }

      .date {
        width: 15%;
      }

      .author {
        width: 15%;
      }
    }
  }
}

.no-announcement {
  text-align: center;
  font-size: 18px;
  padding: 20px;
}
</style>
