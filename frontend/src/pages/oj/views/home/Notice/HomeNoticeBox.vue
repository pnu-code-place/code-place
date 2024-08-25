<template>
  <div class="noticeBox">
    <div class="noticeBoxHeader">
      <span @click="handleRoute('notice')">공지사항</span>
    </div>
    <div>
      <div class="announcement-header csep" @click="goAnnouncement('')">
        <img :src="this.logos.csep" alt="">
        <span class="facility-name">{{ $t("m.CSEP") }}</span>
        <span class="facility-description">
          <span class="plusDiv">
            <Icon type="android-add" size="13" color="#fff"></Icon>
            <span>더보기</span>
          </span>
        </span>
      </div>
      <div class="loading-container" v-if="this.loadingCSEP">
        <div class="loading-skeleton" v-for="i in Array(2)" :key="i"></div>
      </div>
      <div class="notice-sign" v-else-if="this.errorCSPE">
        <span>{{ $t("m.Server_Error") }}</span>
      </div>
      <div class="notice-sign" v-else-if="this.csepAnnouncements.length === 0">
        <span>{{ $t("m.No_Announcements") }}</span>
      </div>
      <ul class="announcements-container" key="list" v-else>
        <HomeNoticeItem
          v-for="(announcement, idx) in csepAnnouncements"
          v-if="idx < 2"
          :key="announcement.title"
          :announcement="announcement"
          :isCSEP="true"
          :isSW="false"
        >
        </HomeNoticeItem>
      </ul>
    </div>
    <div>
      <div class="announcement-header sw" @click="goSW">
        <img :src="this.logos.sw" alt="">
        <span class="facility-name">{{ $t("m.SWCenter") }}</span>
        <span class="facility-description">
          <span class="plusDiv">
            <Icon type="android-add" size="13" color="#fff"></Icon>
            <span>더보기</span>
          </span>
        </span>
      </div>
      <div class="loading-container" v-if="this.loadingSW">
        <div class="loading-skeleton" v-for="i in Array(2)" :key="i"></div>
      </div>
      <div class="notice-sign" v-else-if="this.errorSW">
        <span>{{ $t("m.Server_Error") }}</span>
      </div>
      <div class="notice-sign" v-else-if="this.swAnnouncements.length === 0">
        <span>{{ $t("m.No_Announcements") }}</span>
      </div>
      <ul class="announcements-container" key="list" v-else>
        <HomeNoticeItem
          v-for="(announcement, idx) in swAnnouncements"
          v-if="idx < 5"
          :key="announcement.title"
          :announcement="announcement"
          :isCSEP="false"
          :isSW="true"
        >
        </HomeNoticeItem>
      </ul>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'
import ShineWrapper from "../../../components/ShineWrapper.vue";
import HomeNoticeItem from "./HomeNoticeItem.vue";

export default {
  name: 'HomeNoticeBox',
  components: {HomeNoticeItem, ShineWrapper},
  data() {
    return {
      limit: 10,
      total: 10,
      loadingCSEP: false,
      loadingSW: false,
      errorCSPE: false,
      errorSW: false,
      csepAnnouncements: [],
      announcement: '',
      swAnnouncements: [],
      swUrl: 'https://swedu.pusan.ac.kr/swedu/index.do',
      logos: {
        csep: require('@/assets/code-place-logo.svg'),
        sw: require('@/assets/pnu.png')
      }
    }
  },
  mounted() {
    this.getAnnouncementList()
    this.getSWCenterList()
  },
  methods: {
    getAnnouncementList(page = 1) {
      this.loadingCSEP = true;
      api.getAnnouncementList((page - 1) * this.limit, this.limit).then(
        res => {
          this.loadingCSEP = false;
          this.csepAnnouncements = res.data.data.results;
          this.total = res.data.data.total;
        },
        () => {
          this.loadingCSEP = false;
          this.errorCSPE = true;
        }
      );
    },
    getSWCenterList() {
      this.loadingSW = true;
      api.getSWCenterList().then(
        res => {
          this.loadingSW = false;
          this.swAnnouncements = res.data.data;
          this.total = res.data.data.total;
        },
        () => {
          this.loadingSW = false;
          this.errorSW = true;
        }
      );
    },
    goSW() {
      window.open(this.swUrl);
    },
    handleRoute(route) {
      this.$router.push({name: route});
    },
    goAnnouncement(announcement) {
      this.$router.push({name: "notice", params: {announcement: announcement}});
    }
  },
}
</script>

<style scoped lang="less">
.noticeBox {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 457px;
  padding: 0 30px;
  margin-bottom: 20px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow-y: hidden;

  .noticeBoxHeader {
    padding: 15px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;

    span:first-child {
      font-weight: 650;
      font-size: 18px;
    }
  }
}

.noticeBox:hover {
  border: 1px solid #cccccc;
}

.announcements-container {
  --announcement-date-width: 100px;
  margin: 10px 0;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.announcement-header {
  height: 40px;
  width: 100%;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;

  img {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-40%);
    width: 250px;
    height: auto;
    opacity: 0.7;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  }

  &.csep {
    background-color: var(--point-color);
  }

  &.sw {
    background-image: linear-gradient(45deg, var(--pnu-blue), var(--pnu-green));
  }

  .facility-name {
    font-size: 15px;
    font-weight: 650;
    color: white;
  }

  .facility-description {


    span {
      color: var(--box-background-color);
      font-size: 12px;
      font-weight: 900;
    }
  }

  &:hover {
    transform: scale(1.01);
    text-shadow: 0 0 7px rgba(255, 255, 255, 1);
    font-weight: 900;

    img {
      opacity: 1;
      transform: translateY(-30%);
    }
  }
}

.loading-container {
  width: 100%;
  margin: 10px 0;

  .loading-skeleton {
    width: 100%;
    height: 35px;
    border-radius: 7px;
    margin-bottom: 5px;
    animation: loading 1s infinite;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.notice-sign {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 35px;
  font-size: 15px;
  font-weight: 650;
  color: var(--ps-content-text-color);
  margin: 10px 0;
}

@keyframes loading {
  0% {
    background-color: #e3e3e3;
  }
  50% {
    background-color: #f5f5f5;
  }
  100% {
    background-color: #e3e3e3;
  }
}
</style>

