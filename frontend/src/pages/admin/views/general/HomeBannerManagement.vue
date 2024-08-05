<template>
  <div style="padding: 20px; min-width: 1200px">
    <section
      style="display: flex; justify-content: space-between; margin: 12px"
    >
      <h1 class="title">{{ $t("m.Home_Banner_Management") }}</h1>
      <span
        class="alert-description"
        style="display: flex; gap: 10px; align-items: center"
      >
        <img src="@/assets/information_icon.svg" width="17px" />
        {{ $t("m.Home_Banner_Notice") }}
      </span>
    </section>
    <hr style="border: 0.5px solid #e6e6e6" />
    <section style="padding: 20px">
      <div
        style="
          display: grid;
          padding: 12px;
          border-bottom: 1px solid #e6e6e6;
          justify-items: center;
          grid-template-columns: 0.2fr 0.4fr 2.5fr repeat(3, 1fr) 0.6fr;
        "
      >
        <p></p>
        <p class="table-title">{{ $t("m.Home_Banner_ID") }}</p>
        <p class="table-title">{{ $t("m.Banner_Image") }}</p>
        <p class="table-title">{{ $t("m.Create_Time") }}</p>
        <p class="table-title">{{ $t("m.Last_Update_Time") }}</p>
        <p class="table-title">{{ $t("m.Enable_Disable") }}</p>
        <p class="table-title">{{ $t("m.Setting") }}</p>
      </div>
      <div>
        <div
          v-if="banners.length === 0"
          class="table-title"
          style="width: 100%; text-align: center; margin: 50px 0px"
        >
          {{ $t("m.Home_Banner_Does_Not_Exist") }}
        </div>
        <draggable
          v-else
          tag="ul"
          :list="banners"
          handle=".handle"
          v-bind="dragOptions"
          @end="handleBannerOrderChange"
        >
          <li
            v-for="(banner, idx) in banners"
            :key="banner.id"
            class="drag-item"
          >
            <i class="el-icon-fa-bars handle" style="color: #868991"></i>
            <span class="drag-item-text" style="font-size: 18px">
              {{ banner.id }}
            </span>
            <img :src="banner.banner_image" width="100%" />
            <span class="drag-item-text">
              {{ banner.create_time | localtime }}
            </span>
            <span class="drag-item-text">
              {{ banner.last_update_time | localtime }}
            </span>
            <el-switch
              v-model="banner.visible"
              @change="handleVisibleSwitchChange(banner.id, banner.visible)"
            >
            </el-switch>
            <div>
              <icon-btn
                :name="$t('m.Icon_Edit')"
                icon="edit"
                @click.native="handleModifyButtonClick(banner)"
              ></icon-btn>
              <icon-btn
                :name="$t('m.Icon_Delete')"
                icon="trash"
                @click.native="handleDeleteButtonClick(banner.id)"
              ></icon-btn>
            </div>
          </li>
        </draggable>
      </div>
    </section>
    <section style="margin: 12px">
      <button
        class="button"
        style="color: white; background-color: #409eff"
        @click="handleAddButtonClick"
      >
        <i class="el-icon-plus"></i> {{ $t("m.Add") }}
      </button>
    </section>
    <AddBannerModal v-if="addModalOpen" @onClose="handleModalClose" />
    <ModifyBannerModal
      v-if="modifyModalOpen"
      @onClose="handleModalClose"
      :banner="this.currentBanner"
    />
  </div>
</template>

<script>
import api from "../../api.js";
import draggable from "vuedraggable";
import AddBannerModal from "./HomeBanner/AddBannerModal";
import ModifyBannerModal from "./HomeBanner/ModifyBannerModal";

export default {
  name: "home-banner-management",
  components: {
    draggable,
    AddBannerModal,
    ModifyBannerModal,
  },
  data() {
    return {
      addModalOpen: false,
      modifyModalOpen: false,
      banners: [],
    };
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      api.getBanners().then((res) => {
        vm.banners = res.data.data;
      });
    });
  },
  methods: {
    getBanners() {
      api.getBanners().then((res) => {
        this.banners = res.data.data;
      });
    },
    handleVisibleSwitchChange(id, visible) {
      api.editEnableBanner(id, { visible: visible }).then((res) => {
        if (res.status === 200) {
          this.banners = res.data.data;
        }
      });
    },
    handleBannerOrderChange(id) {
      const reorder_list = this.banners.map((banner) => banner.id);

      api.reorderBanner({ reorder_list: reorder_list }).catch((err) => {
        this.getBanners();
      });
    },
    handleAddButtonClick() {
      this.addModalOpen = true;
    },
    handleModifyButtonClick(banner) {
      this.currentBanner = banner;
      this.modifyModalOpen = true;
    },
    handleDeleteButtonClick(id) {
      api.deleteBanner(id).then((res) => {
        if (res.status === 200) this.getBanners();
      });
    },
    handleModalClose() {
      this.getBanners();
      this.addModalOpen = false;
      this.modifyModalOpen = false;
    },
  },
  computed: {
    dragOptions() {
      return {
        ghostClass: "ghost",
      };
    },
  },
};
</script>

<style lang="less" scoped>
.title {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 300;
}
.alert-description {
  color: #666;
  font-size: 18px;
  font-weight: 500;
}

.table-title {
  color: #666;
  font-size: 18px;
  font-weight: 700;
}

ul,
li,
p {
  margin: 0;
  padding: 0;
}

.drag-item {
  display: grid;
  grid-template-columns: 0.2fr 0.4fr 2.5fr repeat(3, 1fr) 0.6fr;
  list-style-type: none;
  list-style: none;
  padding: 15px;
  justify-items: center;
  align-items: center;
  border-bottom: 1px solid #e6e6e6;
}
.drag-item-text {
  color: #606266;
  font-size: 15px;
  font-weight: 600;
}

.button {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  background-color: white;
  font-size: 13px;
  font-weight: 450;
  cursor: pointer;
  &:hover {
    opacity: 70%;
  }
}

.ghost {
  opacity: 0.1;
  background: #409eff;
}
</style>
