<template>
  <div class="mainBoxWrapper">
    <div class="mainBox">
      <div class="boxWrapper">
        <div class="noticeBox">
          <div class="noticeBoxHeader">
            <span @click="handleRoute('notice')">공지사항</span>
          </div>
          <template v-if="listVisible">
            <ul class="announcements-container" key="list">
              <li
                v-for="(announcement, idx) in announcements"
                :key="announcement.title"
              >
                <div class="flex-container">
                  <div class="title">
                    <a class="entry" @click="goAnnouncement(announcement)">
                      {{ announcement.title }}
                    </a>
                    <span class="newAnnotator" v-if="idx == 0">new</span>
                  </div>

                  <div class="date">
                    {{ getOnlyDate(announcement.create_time) }}
                  </div>
                </div>
              </li>
            </ul>
            <Pagination
              v-if="!isContest"
              key="page"
              :total="total"
              :page-size="limit"
              @on-change="getAnnouncementList"
            >
            </Pagination>
          </template>
        </div>
        <div class="rankingBox">
          <div class="rankingBoxHeader">
            <span>실시간 랭킹</span>
            <img src="@/assets/arrow-rotate.png" width="15px" height="15px" />
          </div>
          <ul class="ranking-container" key="list">
            <li
              v-for="(rankingInfo, idx) in rankingItems.testRealTimeRankingDTO"
              v-if="idx <= 8"
            >
              <div class="flex-container">
                <div class="title">
                  <a class="entry">
                    {{ rankingInfo.ranking }}
                  </a>
                  <img src="@/assets/badgeExample.png" width="15px" />
                  <a class="entry">
                    {{ rankingInfo.userName }}
                  </a>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div class="contestBox" @click="handleRoute('contest-list')">
        <span>진행중인 대회</span>
      </div>
    </div>
  </div>
</template>

<script>
/*eslint-disable*/
import Announcements from "./Announcements.vue";
import api from "@oj/api";
import time from "@/utils/time";
import { CONTEST_STATUS } from "@/utils/constants";
import testRealTimeRankingDTO from "./testRealTimeRankingDTO";

export default {
  name: "home",
  components: {
    Announcements
  },
  data() {
    return {
      contests: [],
      index: 0,
      announcements: [],
      announcement: "",
      listVisible: true,
      btnLoading: false,
      rankingItems: testRealTimeRankingDTO
    };
  },
  mounted() {
    let params = { status: CONTEST_STATUS.NOT_START };
    api.getContestList(0, 5, params).then(res => {
      this.contests = res.data.data.results;
    });
    this.init();
    console.log(this.rankingItems);
  },
  methods: {
    init() {
      if (this.isContest) {
        this.getContestAnnouncementList();
      } else {
        this.getAnnouncementList();
      }
    },
    getOnlyDate(date) {
      let onlyDate = new Date(date);
      return onlyDate.toLocaleDateString();
    },
    goAnnouncement(announcement) {
      this.$router.push("notice");
      setTimeout(() => {}, 1000);
      this.announcement = announcement;
      // this.listVisible = false;
    },
    getAnnouncementList(page = 1) {
      this.btnLoading = true;
      api.getAnnouncementList((page - 1) * this.limit, this.limit).then(
        res => {
          this.btnLoading = false;
          this.announcements = res.data.data.results;
          this.total = res.data.data.total;
        },
        () => {
          this.btnLoading = false;
        }
      );
    },
    handleRoute(route) {
      this.$router.push({ name: route });
    },
    getDuration(startTime, endTime) {
      return time.duration(startTime, endTime);
    },
    goContest() {
      this.$router.push({
        name: "contest-details",
        params: { contestID: this.contests[this.index].id }
      });
    }
  },
  computed: {
    testRealTimeRankingDTO() {
      return testRealTimeRankingDTO;
    },
    isContest() {
      return !!this.$route.params.contestID;
    }
  }
};
</script>

<style lang="less" scoped>
.mainBox {
  padding-left: 3%;
  padding-right: 3%;
}
.boxWrapper {
  display: flex;
  justify-content: space-between;
}
.noticeBox {
  background-color: #ffffff;
  border-radius: 20px;
  width: 63%;
  height: 400px;
  box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.rankingBox {
  background-color: #ffffff;
  border-radius: 20px;
  width: 35%;
  height: 400px;
  box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.noticeBoxHeader {
  padding: 13px;
  padding-left: 20px;
  display: flex;
}
.rankingBoxHeader {
  padding: 13px;
  padding-left: 20px;
  display: flex;
  justify-content: space-between;
}
.contestBox {
  margin-top: 30px;
  padding-left: 3%;
  padding-top: 1%;
  padding-right: 3%;
  background-color: #ffffff;
  border-radius: 20px;
  box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
  height: 200px;
}
span {
  font-weight: 650;
  font-size: 15px;
  cursor: pointer;
}
.contest {
  &-title {
    font-style: italic;
    font-size: 21px;
  }
  &-content {
    padding: 0 70px 40px 70px;
    &-description {
      margin-top: 25px;
    }
  }
}

.announcement {
  margin-top: 20px;
}
.announcements-container {
  margin-top: -10px;
  margin-bottom: 10px;
  li {
    padding-top: 15px;
    list-style: none;
    padding-bottom: 15px;
    background-color: #fbfbfb;
    margin-top: 8px;
    padding-left: 30px;
    border-radius: 15px;
    margin-left: 20px;
    margin-right: 20px;
    font-size: 16px;
    &:last-child {
      border-bottom: none;
    }
    .flex-container {
      .title {
        flex: 1 1;
        text-align: left;
        padding-left: 10px;
        a.entry {
          color: #495060;
          &:hover {
            color: #4a86c0;
            //border-bottom: 1px solid #4a86c0;
          }
        }
      }
      .newAnnotator {
        background-color: #ff8a8a;
        border-radius: 10px;
        color: #ffffff;
        font-size: x-small;
        text-align: center;
        width: 23px;
        margin: auto;
        padding-left: 3px;
        padding-right: 3px;
      }
      .date {
        flex: none;
        width: 200px;
        text-align: center;
        font-size: small;
        color: #737373;
      }
    }
  }
}

.ranking-container {
  margin-top: -5px;
  margin-bottom: 5px;
  li {
    padding-top: 5px;
    list-style: none;
    padding-bottom: 5px;
    margin-top: 4px;
    padding-left: 30px;
    border-radius: 15px;
    margin-left: 20px;
    margin-right: 20px;
    font-size: 16px;
    font-weight: bold;
    &:last-child {
      border-bottom: none;
    }
    .flex-container {
      img {
        margin-right: 10px;
      }
      .title {
        flex: 1 1;
        text-align: left;
        padding-left: 10px;
        a.entry {
          margin-right: 40px;
          color: #495060;
        }
      }
    }
  }
}
</style>
