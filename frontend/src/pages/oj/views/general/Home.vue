<template>
  <div class="home-wrapper">
    <PopUp
      v-for="(popup, index) in filteredPopup"
      :key="popup.id"
      :id="popup.id"
      :link="popup.link_url"
      :width="
        popup.popup_image_width === null || popup.popup_image_width <= 50
          ? 0
          : popup.popup_image_width
      "
      :p_position="{ x: 100 + index * 50, y: 100 + index * 50 }"
      :is-top-popup="topPopupId === popup.id"
      @selected="popupSelect"
    >
      <img
        :src="popup.popup_image"
        :alt="popup.alt"
        draggable="false"
        :style="{ width: '100%', objectFit: 'contain' }"
      />
    </PopUp>

    <HomeHeroSection />
    <!-- 바로가기 카드: 상단 네비바와 메뉴가 중복되어 숨김 처리 (교수님 피드백). 컴포넌트 파일은 보존, 복구 시 아래 주석 해제. -->
    <!-- <HomeQuickNavCards /> -->
    <div class="notice-rank-row">
      <HomeNoticeProblemRow />
      <div class="sidebar-col">
        <HomeRankingSidebar />
        <HomeActivitySidebar />
      </div>
    </div>
    <HomeOngoingContests />
    <HomeWeeklyServices />
    <HomeCTABanner />
    <HomeFamilySite />
  </div>
</template>

<script>
/*eslint-disable*/
import api from "@oj/api"
import { mapActions, mapGetters } from "vuex"
import PopUp from "../../components/modal/PopUp.vue"
import storage from "../../../../utils/storage"

import HomeHeroSection from "../home/HomeHeroSection.vue"
import HomeQuickNavCards from "../home/HomeQuickNavCards.vue"
import HomeNoticeProblemRow from "../home/HomeNoticeProblemRow.vue"
import HomeRankingSidebar from "../home/HomeRankingSidebar.vue"
import HomeActivitySidebar from "../home/HomeActivitySidebar.vue"
import HomeOngoingContests from "../home/HomeOngoingContests.vue"
import HomeWeeklyServices from "../home/HomeWeeklyServices.vue"
import HomeCTABanner from "../home/HomeCTABanner.vue"
import HomeFamilySite from "../home/HomeFamilySite.vue"

export default {
  name: "home",
  components: {
    PopUp,
    HomeHeroSection,
    HomeQuickNavCards,
    HomeNoticeProblemRow,
    HomeRankingSidebar,
    HomeActivitySidebar,
    HomeOngoingContests,
    HomeWeeklyServices,
    HomeCTABanner,
    HomeFamilySite,
  },
  data() {
    return {
      popupData: [],
      topPopupId: 0,
      removedPopups: [],
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    ...mapActions(["getProfile"]),
    init() {
      api.getPopup().then((res) => {
        this.popupData = Array.isArray(res.data.data) ? res.data.data : []
      })
      const removedPopup = storage.get("removedPopup")
      this.removedPopups = Array.isArray(removedPopup)
        ? removedPopup.map((popup) => popup.id)
        : []
    },
    popupSelect(value) {
      this.topPopupId = value
    },
  },
  computed: {
    ...mapGetters(["website", "isAdminRole", "removedPopupId"]),
    filteredPopup() {
      return this.popupData.filter(
        (popup) => !this.removedPopups.includes(popup.id),
      )
    },
  },
}
</script>

<style lang="less" scoped>
.home-wrapper {
  width: 100%;
  max-width: var(--global-width);
  background-color: #f8f8fc;
  min-height: 100vh;
  padding: 0 30px;

  @media (max-width: 1024px) {
    padding: 0 20px;
  }
  @media (max-width: 768px) {
    padding: 0 14px;
    width: 100%;
  }
}

.notice-rank-row {
  display: flex;
  align-items: stretch;
  gap: 20px;

  & > *:first-child {
    flex: 2;
    min-width: 0;
  }

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 0;
  }
}

.sidebar-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;

  @media (max-width: 768px) {
    flex-direction: row;
    gap: 12px;
  }
  @media (max-width: 480px) {
    flex-direction: column;
  }
}
</style>
