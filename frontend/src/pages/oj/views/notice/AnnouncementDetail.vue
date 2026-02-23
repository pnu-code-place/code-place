<script>
import api from "../../api"
import ErrorSign from "../general/ErrorSign.vue"
import notice from "./Notice.vue"

export default {
  name: "AnnouncementDetails",
  components: { ErrorSign },
  data() {
    return {
      announcement: {
        id: 1,
        created_by: {
          id: 1,
          username: "root",
          email: "root",
          real_name: null,
          student_id: null,
          school: "\uacf5\ub300",
          major: "\ud559\uacfc",
        },
        title: "[CSEP] 코딩역량강화플랫폼 채점 언어 및 컴파일러 안내",
        content:
          "<h2><strong>C\uc5b8\uc5b4 \ucef4\ud30c\uc77c\ub7ec</strong></h2><ul><li>gcc (Debian 13.2.0-25) 13.2.0</li></ul><h2><strong>C++ \ucef4\ud30c\uc77c\ub7ec</strong></h2><ul><li>g++ (Debian 13.2.0-25) 13.2.0</li></ul><h2><strong>\ud30c\uc774\uc36c \uc778\ud130\ud504\ub9ac\ud130</strong></h2><ul><li>Python 3.12.3</li></ul><h2><strong>\uc790\ubc14 JDK \ubc84\uc804</strong></h2><ul><li>openjdk 21.0.3 (LTS \ubc84\uc804)<ul><li>Temurin Java JDK</li></ul></li></ul><h2><strong>NodeJS(\uc790\ubc14\uc2a4\ud06c\ub9bd\ud2b8 \ub7f0\ud0c0\uc784) \ubc84\uc804</strong></h2><ul><li>v20.14.0</li></ul>",
        create_time: "2024-07-25T11:20:06.681229Z",
        last_update_time: "2024-07-21T16:33:17.914733Z",
        visible: true,
      },
      loading: false,
      error: 0,
      loadingNext: false,
      loadingBefore: false,
      nextAnnouncement: null,
      beforeAnnouncement: null,
      total: null,
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      this.getAnnouncement()
      // this.findNextAnnouncement(this.$route.params.noticeID)
      // this.findBeforeAnnouncement(this.$route.params.noticeID)
    },
    getAnnouncement() {
      this.loading = true
      api
        .getAnnouncement(this.$route.params.noticeID)
        .then((res) => {
          this.announcement = res.data.data.results[0]
          this.total = res.data.data.total
          this.loading = false
        })
        .catch((error) => {
          this.loading = false
          this.error = error.response.status
        })
    },
    findNextAnnouncement(noticeId) {
      this.loadingNext = true
      noticeId = parseInt(noticeId)
      if (noticeId >= this.total) {
        this.loadingNext = false
        this.nextAnnouncement = null
        return null
      }
      api
        .getAnnouncement(noticeId + 1)
        .then(async (res) => {
          if (res.data.data.results.length === 0) {
            // console.log(`발견된 공지사항이 없습니다. noticeId: ${noticeId} 다음 공지사항을 찾습니다. noticeId + 1: ${noticeId + 1}`)
            await this.findNextAnnouncement(noticeId + 1)
          } else {
            this.loadingNext = false
            this.nextAnnouncement = res.data.data.results[0]
            return res.data.data.results[0]
          }
        })
        .catch(async (error) => {
          this.loadingNext = false
        })
    },
    findBeforeAnnouncement(noticeId) {
      this.loadingBefore = true
      noticeId = parseInt(noticeId)
      if (noticeId <= 1) {
        this.loadingBefore = false
        this.beforeAnnouncement = null
        return null
      }
      api
        .getAnnouncement(noticeId - 1)
        .then(async (res) => {
          if (res.data.data.results.length === 0) {
            // console.log(`발견된 공지사항이 없습니다. noticeId: ${noticeId} 다음 공지사항을 찾습니다. noticeId - 1: ${noticeId - 1}`)
            await this.findBeforeAnnouncement(noticeId - 1)
          } else {
            this.loadingBefore = false
            this.beforeAnnouncement = res.data.data.results[0]
            return res.data.data.results[0]
          }
        })
        .catch(async (error) => {
          this.loadingBefore = false
        })
    },
    goBeforeAnnouncement() {
      this.$router.push({
        name: "notice-details",
        params: { noticeID: this.beforeAnnouncementId },
      })
    },
    goAfterAnnouncement() {
      this.$router.push({
        name: "notice-details",
        params: { noticeID: this.nextAnnouncementId },
      })
    },
    goList() {
      this.$router.push({
        name: "notice",
      })
    },
  },
  computed: {
    createDate() {
      if (this.announcement.create_time.split("T").length > 1) {
        return this.announcement.create_time.split("T")[0]
      } else {
        return this.announcement.create_time
      }
    },
    beforeAnnouncementId() {
      if (this.beforeAnnouncement === null) {
        return null
      }
      return this.beforeAnnouncement.id
    },
    nextAnnouncementId() {
      if (this.nextAnnouncement === null) {
        return null
      }
      return this.nextAnnouncement.id
    },
    nextAnnouncementTitle() {
      if (this.nextAnnouncement === null) {
        return this.$t("m.NoNextAnnouncement")
      }
      return this.nextAnnouncement.title
    },
    beforeAnnouncementTitle() {
      if (this.beforeAnnouncement === null) {
        return this.$t("m.NoBeforeAnnouncement")
      }
      return this.beforeAnnouncement.title
    },
    existBeforeAnnouncement() {
      return this.beforeAnnouncement !== null
    },
    existNextAnnouncement() {
      return this.nextAnnouncement !== null
    },
  },
  watch: {
    "$route.params.noticeID": function () {
      this.init()
    },
  },
}
</script>

<template>
  <div>
    <div class="announcement-detail">
      <div v-if="this.loading" class="loading-wrapper">
        <div class="loading-header skeleton"></div>
        <hr />
        <div class="loading-contents">
          <div class="loading-skeleton skeleton"></div>
          <div class="loading-skeleton skeleton"></div>
          <div class="loading-skeleton skeleton"></div>
          <div class="loading-skeleton skeleton"></div>
        </div>
      </div>
      <div v-else-if="this.error !== 0">
        <ErrorSign :code="this.error"> </ErrorSign>
      </div>
      <div v-else>
        <header class="announcement-header">
          <h1 class="title">{{ this.announcement.title }}</h1>
          <div class="announcement-info">
            <div class="announcement-info__content">
              <span class="label">{{ $t("m.Date") }}</span>
              <span class="data">{{ this.createDate }}</span>
            </div>
            <div class="announcement-info__content">
              <span class="label">{{ $t("m.Author") }}</span>
              <span class="data">{{
                this.announcement.created_by.username
              }}</span>
            </div>
          </div>
        </header>
        <hr />
        <div
          v-katex
          v-html="this.announcement.content"
          key="content"
          class="contents content-container markdown-body"
        ></div>
      </div>
    </div>
    <button class="notice-list-btn" @click="goList">
      {{ $t("m.Notice_List") }}
    </button>
    <!--    <div class="other-announcements">-->
    <!--      <div class="other-announcement-wrapper">-->
    <!--        <div class="announcement-skeleton" v-if="this.loadingNext">-->
    <!--          <div class="skeleton"></div>-->
    <!--        </div>-->
    <!--        <div v-else-if="this.existNextAnnouncement" class="other-announcement__title" @click="this.goAfterAnnouncement">-->
    <!--          {{ this.nextAnnouncementTitle }}-->
    <!--        </div>-->
    <!--        <div v-else>-->
    <!--          <div class="no-announcement">{{ $t('m.NoNextAnnouncement') }}</div>-->
    <!--        </div>-->
    <!--      </div>-->
    <!--      <div class="other-announcement-wrapper">-->
    <!--        <div class="announcement-skeleton" v-if="this.loadingBefore">-->
    <!--          <div class="skeleton"></div>-->
    <!--        </div>-->
    <!--        <div v-else-if="this.existBeforeAnnouncement" class="other-announcement__title"-->
    <!--             @click="this.goBeforeAnnouncement">{{ this.beforeAnnouncementTitle }}-->
    <!--        </div>-->
    <!--        <div v-else>-->
    <!--          <div class="no-announcement">{{ $t('m.NoBeforeAnnouncement') }}</div>-->
    <!--        </div>-->
    <!--      </div>-->
    <!--    </div>-->
  </div>
</template>

<style scoped lang="less">
.other-announcements {
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-top: 20px;
  background-color: var(--box-background-color);
  border-radius: var(--container-border-radius);
  border: 1px solid var(--container-border-color);

  .other-announcement-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    width: 100%;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    &:hover {
      background-color: var(--pale-point-color);
    }

    &:nth-child(1) {
      border-bottom: 1px solid var(--container-border-color);
    }

    .announcement-skeleton {
      width: 100%;
      height: 50px;
      background-color: var(--skeleton-color);
      border-radius: 5px;
    }

    .other-announcement__title {
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
      width: 100%;
      text-align: center;
    }
  }
}

.announcement-detail {
  --skeleton-color: #dedede;
  width: var(--global-width);
  background-color: var(--box-background-color);
  border-radius: var(--container-border-radius);
  padding: 0 30px 15px;
  border: 1px solid var(--container-border-color);
  min-height: 600px;

  .announcement-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .announcement-info {
      width: 160px;
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 2px;

      .announcement-info__content {
        width: 100%;
        font-size: 18px;
        color: var(--text-color);
        font-weight: 600;
        display: flex;
        gap: 10px;
        justify-content: space-between;
      }
    }
  }

  hr {
    border: 1px solid var(--container-border-color);
  }

  .title {
    font-size: 24px;
    font-weight: 700;
    padding: 20px 0;
  }

  .contents {
    padding-top: 15px;
  }
}

.loading-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  align-items: center;

  .loading-header {
    width: 100%;
    height: 50px;
    background-color: var(--skeleton-color);
    border-radius: 5px;
  }

  hr {
    width: 100%;
    border: 1px solid var(--container-border-color);
  }

  .loading-contents {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 20px;

    .loading-skeleton {
      width: 100%;
      height: 35px;
      background-color: var(--skeleton-color);
      border-radius: 5px;
    }
  }
}

.skeleton {
  animation: skeleton-loading 1s infinite;
  width: 100%;
}

@keyframes skeleton-loading {
  0% {
    opacity: 0.5;
  }

  50% {
    opacity: 0.8;
  }

  100% {
    opacity: 0.5;
  }
}

.notice-list-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.notice-list-btn {
  background: rgb(241, 243, 244);
  color: black;
}

.notice-list-btn:hover {
  background: lightgrey;
  color: rgb(50, 50, 50);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.2);
}
</style>
