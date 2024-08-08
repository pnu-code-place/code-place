<template>
  <div class="announcements">
    <h1 class="title main-title">
      {{ $t('m.Announcements') }}
    </h1>
    <div class="announcement-container">
      <div class="no-announcement" v-if="!announcements.length" key="no-announcement">
        <p>{{ $t('m.No_Announcements') }}</p>
      </div>
      <table v-else class="announcement-table" key="list">
        <thead>
        <tr>
          <th class="id">{{ $t('m.ID') }}</th>
          <th class="title">{{ $t('m.Title') }}</th>
          <th class="date">{{ $t('m.Date') }}</th>
          <th class="author">{{ $t('m.Author') }}</th>
        </tr>
        </thead>
        <tbody>
        <announcement-item v-for="announcement in announcements" :key="announcement.title" :announcement="announcement">
        </announcement-item>
        </tbody>
      </table>
      <Pagination v-if="!isContest"
                  key="page"
                  :total="total"
                  :page-size="limit"
                  @on-change="getAnnouncementList">
      </Pagination>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'
import Pagination from '@oj/components/Pagination'
import AnnouncementItem from "./AnnouncementItem.vue";

export default {
  name: 'Announcement',
  components: {
    AnnouncementItem,
    Pagination
  },
  data() {
    return {
      limit: 10,
      total: 10,
      btnLoading: false,
      announcements: [],
      announcement: '',
      listVisible: true
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      if (this.isContest) {
        this.getContestAnnouncementList()
      } else {
        this.getAnnouncementList()
      }
    },
    getAnnouncementList(page = 1) {
      this.btnLoading = true
      api.getAnnouncementList((page - 1) * this.limit, this.limit).then(res => {
        this.btnLoading = false
        this.announcements = res.data.data.results
        this.total = res.data.data.total
      }, () => {
        this.btnLoading = false
      })
    },
    getContestAnnouncementList() {
      this.btnLoading = true
      api.getContestAnnouncementList(this.$route.params.contestID).then(res => {
        this.btnLoading = false
        this.announcements = res.data.data
      }, () => {
        this.btnLoading = false
      })
    },
    goAnnouncement(announcement) {
      this.announcement = announcement
      this.listVisible = false
    },
  },
  computed: {
    title() {
      if (this.listVisible) {
        return this.isContest ? this.$i18n.t('m.Contest_Announcements') : this.$i18n.t('m.Announcements')
      } else {
        return this.announcement.title
      }
    },
    isContest() {
      return !!this.$route.params.contestID
    }
  }
}
</script>

<style scoped lang="less">
.announcements {
  width: var(--global-width);

  .title {
    margin-bottom: 20px;
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
