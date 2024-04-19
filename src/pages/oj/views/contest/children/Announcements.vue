<template>
  <div class="announcementBox">
    <div class="announcementTitle">
      <p>{{$t('m.Announcement')}}</p>
      <Button v-if="listVisible" type="info" @click="init" :loading="btnLoading">{{$t('m.Refresh')}}</Button>
      <Button v-else type="ghost" icon="ios-undo" @click="goBack">{{$t('m.Back')}}</Button>
    </div>
    <div v-if="listVisible" class="announcementContent">
      <div v-if="!announcements.length" key="noAnnouncement">{{$t('m.No_Announcements')}}</div>
      <a v-for="announcement in announcements" :key="announcement.id" class="announcementItem" @click="goAnnouncement(announcement)">
        <div class="title">{{announcement.title}}</div>
        <div class="date">{{announcement.create_time | localtime('YYYY-M-D')}}</div>
        <div class="creator">{{announcement.created_by.username}}</div>
      </a>
    </div>
    <div v-else v-html="announcement.content" key="content" class="markdown-body" style="padding: 10px 20px;"></div>
  </div>
</template>

<script>
  import api from '@oj/api'

  export default {
    name: 'Announcement',
    data () {
      return {
        limit: 10,
        total: 10,
        btnLoading: false,
        announcements: [],
        announcement: '',
        listVisible: true
      }
    },
    mounted () {
      this.init()
    },
    methods: {
      init () {
        this.getContestAnnouncementList()
      },
      getContestAnnouncementList () {
        this.btnLoading = true
        api.getContestAnnouncementList(this.$route.params.contestID).then(res => {
          this.btnLoading = false
          this.announcements = res.data.data
        }, () => {
          this.btnLoading = false
        })
      },
      goAnnouncement (announcement) {
        this.announcement = announcement
        this.listVisible = false
      },
      goBack () {
        this.listVisible = true
        this.announcement = ''
      }
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
.announcementContent {
  display: flex;
  flex-direction: column;
  font-size: 16px;
  text-align: center;
}
.announcementItem {
  display: flex;
  margin: 0px 20px;
  color: #495060;
  padding: 15px;
  border-bottom: 1px solid rgba(187, 187, 187, 0.5);
  &:hover {
    :first-child {color: #2d8cf0;}
  }
  &:last-child { border-bottom: none; }
  .title {
    flex: 1 auto;
    text-align: left;
  }
  .date {
    flex-shrink: 0;
    width: 150px;
  }
  .creator {
    flex-shrink: 0;
    width: 150px;
  }
}
</style>
