<template>
  <div class="mainBox">
    <div class="boxWrapper">
      <div class="left-container">
        <div class="bannerBox">
          <Carousel v-model="value1" autoplay loop arrow="never" radius-dot="true">
            <CarouselItem>
              <div class="demo-carousel">Banner 1</div>
            </CarouselItem>
            <CarouselItem>
              <div class="demo-carousel">Banner 2</div>
            </CarouselItem>
            <CarouselItem>
              <div class="demo-carousel">Banner 3</div>
            </CarouselItem>
            <CarouselItem>
              <div class="demo-carousel">Banner 4</div>
            </CarouselItem>
          </Carousel>
        </div>
        <div class="noticeBox">
          <div class="noticeBoxHeader">
            <span @click="handleRoute('notice')">공지사항</span>
            <div class="plusDiv" @click="handleRoute('notice')">
              <Icon type="android-add" size="13" color="#7a7a7a"></Icon>
              <span>더보기</span>
            </div>
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
        <div class="problemRecommendationBox">
          <div class="problemRecommendationBoxHeader">
            <span @click="handleRoute('notice')">이번 주 보너스 문제</span>
            <div class="plusDiv">
              <Icon type="ios-information" size="13" color="#7a7a7a"></Icon>
              <span class="plusSpan">주마다 보너스 점수가 있는 문제를 추천해드려요!</span>
            </div>

          </div>
        </div>
      </div>
      <div class="right-container">
        <div class="profileBox">
          <template v-if="!isAuthenticated">
            <span>
              안전한 서비스 이용을 위해 로그인을 해주세요
            </span>
            <div class="loginBtn" @click="handleLoginBtnClick('login')">
              <Icon type="android-lock" size="20"></Icon>
              <span>로그인</span>
            </div>
            <div class="profileBoxFooter">
              <span @click.stop="handleLoginBtnClick('register')">회원가입</span>
              <span @click.stop="goResetPassword">비밀번호 찾기</span>
            </div>
          </template>
          <template v-else>
            <div class="authenticatedBox">
              <div class="authenticatedBody">
                <div class="userAvatarWrapper">
                  <img class="avatar" :src="profile.avatar"/>
                </div>
                <div class="userInfoWrapper">
                  <span>
                    {{ user.username+'님' }}
                    <img src="@/assets/badgeExample.png" width="13px"/>
                  </span>
                  <br>
                  <span>{{ user.email }}</span>
                  <br>
                  <span>ACM 56000p</span>
                </div>
                <div class="logoutBtn">
                  <span @click="goRouter('logout')">
                    로그아웃
                  </span>
                </div>
              </div>
              <div class="authenticatedFooter">
                <span @click="goRouter('user-home')">마이페이지</span>
                <span>{{'|'}}</span>
                <span @click="goRouter('profile-setting')">환경설정</span>
              </div>
            </div>

          </template>
        </div>
        <div class="rankingBox">
          <div class="rankingBoxHeader">
            <span>실시간 랭킹</span>
            <div>
              <Icon type="ios-information-outline" size="13" color="#7a7a7a"></Icon>
              <span>순위는 매일 밤 12시 갱신됩니다</span>
            </div>
          </div>
          <ul class="ranking-container" key="list">
            <li
                v-for="(rankingInfo, idx) in rankingItems.testRealTimeRankingDTO"
                v-if="idx <= 9"
            >
              <div class="flex-container">
                <div class="title">
                  <a class="entry">
                    {{ rankingInfo.ranking + '위' }}
                  </a>
                  <a class="entry">
                    {{ rankingInfo.userName }}
                  </a>
                  <img src="@/assets/badgeExample.png" width="13px"/>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
/*eslint-disable*/
import Announcements from "./Announcements.vue";
import api from "@oj/api";
import time from "@/utils/time";
import {CONTEST_STATUS} from "@/utils/constants";
import testRealTimeRankingDTO from "./testRealTimeRankingDTO";
import {mapActions, mapGetters} from "vuex";

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
      rankingItems: testRealTimeRankingDTO,
      value1: 0
    };
  },
  mounted() {
    let params = {status: CONTEST_STATUS.NOT_START};
    api.getContestList(0, 5, params).then(res => {
      this.contests = res.data.data.results;
    });
    this.init();
    console.log(this.rankingItems);
    this.getProfile()
  },
  methods: {
    ...mapActions(['getProfile', 'changeModalStatus']),
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
    handleLoginBtnClick(mode) {
      console.log("setting complete!")
      this.changeModalStatus({
        visible: true,
        mode: mode
      })
    },
    goAnnouncement(announcement) {
      this.$router.push("notice");
      setTimeout(() => {
      }, 1000);
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
      this.$router.push({name: route});
    },
    getDuration(startTime, endTime) {
      return time.duration(startTime, endTime);
    },
    goContest() {
      this.$router.push({
        name: "contest-details",
        params: {contestID: this.contests[this.index].id}
      });
    },
    goResetPassword() {
      this.changeModalStatus({ visible: false });
      this.$router.push({ name: "apply-reset-password" });
    },
    goRouter(routeName){
      this.$router.push({name: routeName})
    }
  },
  computed: {
    ...mapGetters(['website', 'modalStatus', 'user', 'isAuthenticated', 'isAdminRole']),
    ...mapGetters(['profile']),
    testRealTimeRankingDTO() {
      return testRealTimeRankingDTO;
    },
    isContest() {
      return !!this.$route.params.contestID;
    },
    modalVisible: {
      get() {
        return this.modalStatus.visible
      },
      set(value) {
        this.changeModalStatus({visible: value})
      }
    }
  }
};
</script>

<style lang="less" scoped>
.mainBox {
  padding-left: 8.5%;
  padding-right: 8.5%;
}

.boxWrapper {
  display: flex;
  justify-content: space-between;
}

.left-container {
  width: 65%;
  height: 100%;
}

.right-container {
  width: 33%;
  height: auto;
}

.bannerBox {
  margin-bottom: 20px;
  .demo-carousel{
    cursor: pointer;
    border-radius: 7px;
    width: 100%;
    height: 150px;
    line-height: 150px;
    border: 1px solid #dedede;
    text-align: center;
    background-color: #ffffff;
    font-size: 20px;
  }
}

.noticeBox {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 400px;
  padding-left: 30px;
  padding-right: 30px;
  margin-bottom: 20px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .noticeBoxHeader {
    padding-top: 15px;
    padding-bottom: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #dedede;

    span:first-child {
      font-weight: 650;
      font-size: 15px;
    }

    .plusDiv{
      cursor: pointer;

      span {
        color: #7a7a7a;
        font-size: 12px;
      }
    }

  }
}

.problemRecommendationBox{
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 300px;
  padding-left: 30px;
  padding-right: 30px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  .problemRecommendationBoxHeader{
    padding-top: 15px;
    padding-bottom: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #dedede;

    span:first-child {
      font-weight: 650;
      font-size: 15px;
    }

    .plusDiv{
      cursor: pointer;

      .plusSpan {
        color: #7a7a7a;
        font-size: 12px;
      }
    }

  }
}

.rankingBox {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 450px;
  padding-left: 30px;
  padding-right: 30px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .rankingBoxHeader {

    padding-top: 15px;
    padding-bottom: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #dedede;

    span:first-child {
      font-weight: 650;
      font-size: 15px;
    }

    span:nth-child(2) {
      color: #7a7a7a;
      font-size: 12px;
    }
  }
}

.profileBox {
  background-color: #ffffff;
  border-radius: 7px;
  border: 1px solid #dedede;
  width: 100%;
  height: 200px;
  margin-bottom: 20px;
  text-align: center;
  padding-left: 30px;
  padding-right: 30px;
  padding-top: 25px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  .loginBtn {
    cursor: pointer;
    color: white;
    border-radius: 5px;
    height: 60px;
    line-height: 60px;
    background-color: #4A86C0;
    margin-top: 30px;
    margin-bottom: 30px;
    span {
      margin-left: 10px;
      font-weight: 650;
      font-size: 15px;
    }
  }

  .profileBoxFooter {
    display: flex;
    justify-content: right;

    span {
      cursor: pointer;
    }

    span:nth-child(1) {
      margin-right: 10px;
    }
  }
}

.authenticatedBox{

  @avatar-radius: 50%;
  .avatar {
    width: 100%;
    height: auto;
    max-width: 100%;
    display: block;
    border-radius: @avatar-radius;
    box-shadow: 0px 0px 1px 0px;
  }

  .authenticatedBody{
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin-bottom: 30px;
    .userAvatarWrapper{
      width: 20%;
      height: auto;
    }
    .userInfoWrapper{
      text-align: left;
      span:first-child{
        font-size: 13px;
        font-weight: 600;
      }
    }
    .logoutBtn{
      cursor: pointer;
      width: 80px;
      border-radius: 10px;
      border: 1px solid #ACCCDE;
    }
  }

  .authenticatedFooter{
    display: flex;
    background-color: #FBFBFB;
    justify-content: space-around;
    align-items: center;
    height: 35px;
    span{
      cursor: pointer;
    }
  }
}

.contestBox {
  margin-top: 30px;
  padding-left: 3%;
  border: 0.5px solid #B6B6B6;
  padding-top: 1%;
  padding-right: 3%;
  background-color: #ffffff;
  border-radius: 7px;
  height: 200px;
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

.announcements-container {
  margin-top: 10px;
  margin-bottom: 10px;

  li {
    padding-top: 15px;
    list-style: none;
    padding-bottom: 15px;
    background-color: #fbfbfb;
    padding-left: 30px;
    border-radius: 7px;
    font-size: 16px;
    margin-bottom: 5px;

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
    margin-top: 9px;
    border-radius: 15px;
    margin-left: 20px;
    margin-right: 20px;
    font-size: 12px;
    font-weight: bold;

    &:last-child {
      border-bottom: none;
    }

    .flex-container {
      img {
        margin-right: 1px;
      }

      .title {
        flex: 1 1;
        text-align: left;
        a.entry:first-child {
          margin-left: 12px;
          margin-right: 80px;
          color: #495060;
        }
      }
    }
  }
}
</style>
