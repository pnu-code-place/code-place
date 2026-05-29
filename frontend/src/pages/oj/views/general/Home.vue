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
    <HomeQuickNavCards />
    <HomeNoticeProblemRow />
    <HomeWeeklyServices />
    <HomeRankingActivityRow />
    <HomeCTABanner />
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
import HomeWeeklyServices from "../home/HomeWeeklyServices.vue"
import HomeRankingActivityRow from "../home/HomeRankingActivityRow.vue"
import HomeCTABanner from "../home/HomeCTABanner.vue"

export default {
  name: "home",
  components: {
    PopUp,
    HomeHeroSection,
    HomeQuickNavCards,
    HomeNoticeProblemRow,
    HomeWeeklyServices,
    HomeRankingActivityRow,
    HomeCTABanner,
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
        this.popupData = res.data.data
      })
      this.removedPopups = storage.get("removedPopup").map((popup) => popup.id)
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
  width: var(--global-width);
  background-color: #f8f8fc;
  min-height: 100vh;
  padding: 0 30px;
}
</style>
