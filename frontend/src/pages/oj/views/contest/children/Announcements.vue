<template>
  <div class="announcementBox">
    <div class="announcementTitle">
      <p>{{ $t("m.Announcement") }}</p>
      <Button
        v-if="listVisible"
        type="info"
        @click="init"
        :loading="btnLoading"
        >{{ $t("m.Refresh") }}</Button
      >
      <Button v-else type="ghost" icon="ios-undo" @click="goBack">{{
        $t("m.Back")
      }}</Button>
    </div>
    <div v-if="listVisible">
      <div
        v-if="!announcements.length"
        style="text-align: center; font-size: 16px"
      >
        {{ $t("m.No_Announcements") }}
      </div>
      <table v-else class="announcementTable">
        <thead>
          <th>{{ $t("m.ID") }}</th>
          <th class="TableTitle">{{ $t("m.Title") }}</th>
          <th>{{ $t("m.Date") }}</th>
          <th>{{ $t("m.Author") }}</th>
        </thead>
        <tbody>
          <tr
            v-for="(announcement, idx) in announcements"
            @click="goAnnouncement(announcement)"
          >
            <td>{{ announcement.id }}</td>
            <td class="TableTitle">{{ announcement.title }}</td>
            <td>{{ announcement.create_time | localtime("YYYY-M-D") }}</td>
            <td>{{ announcement.created_by.username }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div
      v-else
      v-html="announcement.content"
      key="content"
      class="markdown-body"
      style="padding: 10px 20px"
    ></div>
  </div>
</template>

<script>
import api from "@oj/api"

export default {
  name: "Announcement",
  data() {
    return {
      limit: 10,
      total: 10,
      btnLoading: false,
      announcements: [],
      announcement: "",
      listVisible: true,
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      this.getContestAnnouncementList()
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
    goBack() {
      this.listVisible = true
      this.announcement = ""
    },
  },
}
</script>

<style scoped lang="less">
.announcementBox {
  border: 1px solid #e9ece9;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--box-background-color);
  padding: 15px 20px;
  border-radius: 7px;
}
.announcementTitle {
  display: flex;
  justify-content: space-between;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
}
.announcementTable {
  text-align: center;
  th {
    width: 80px;
    color: #7e7e7e;
    font-size: 1.3em;
    padding-bottom: 10px;
  }
  td {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    padding: 10px 0px;
    cursor: pointer;
  }
  tr {
    font-size: 1.05em;
    &:hover {
      color: #2d8cf0;
    }
  }
  .TableTitle {
    font-size: 1.3em;
    width: auto;
    text-align: left;
  }
}
</style>
