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
        <draggable tag="ul" :list="banners" handle=".handle">
          <li
            v-for="(banner, idx) in banners"
            :key="banner.id"
            class="drag-item"
          >
            <i class="el-icon-fa-bars handle" style="color: #868991"></i>
            <span class="drag-item-text" style="font-size: 18px">
              {{ banner.id }}
            </span>
            <img src="@/assets/banner1.svg" width="100%" />
            <!-- <img :src="banner.banner_image" width="100%" /> -->
            <span class="drag-item-text">
              {{ banner.create_time | localtime }}
            </span>
            <span class="drag-item-text">
              {{ banner.last_update_time | localtime }}
            </span>
            <el-switch v-model="banner.visible"> </el-switch>
            <div>
              <icon-btn
                :name="$t('m.Icon_Edit')"
                icon="edit"
                @click.native="openUserDialog(row.id)"
              ></icon-btn>
              <icon-btn
                :name="$t('m.Icon_Delete')"
                icon="trash"
                @click.native="deleteUsers([row.id])"
              ></icon-btn>
            </div>
          </li>
        </draggable>
      </div>
    </section>
  </div>
</template>

<script>
import draggable from "vuedraggable";

export default {
  name: "home-banner-management",
  components: {
    draggable,
  },
  data() {
    return {
      banners: [
        {
          id: 4,
          banner_image: "/public/banner/a846633f83.png",
          link_url: "https://www.naver.com",
          visible: false,
          order: null,
          create_time: "2024-07-10T07:17:15.289541Z",
          last_update_time: "2024-07-10T07:17:15.289581Z",
        },
        {
          id: 5,
          banner_image: "/public/banner/f45ebadcfc.png",
          link_url: "https://www.naver.com",
          visible: false,
          order: null,
          create_time: "2024-07-10T07:43:50.566984Z",
          last_update_time: "2024-07-10T07:43:50.566998Z",
        },
        {
          id: 6,
          banner_image: "/public/banner/8c3c7a048f.png",
          link_url: "https://www.naver.com",
          visible: false,
          order: null,
          create_time: "2024-07-10T07:44:44.757389Z",
          last_update_time: "2024-07-10T07:44:44.757405Z",
        },
        {
          id: 7,
          banner_image: "/public/banner/7532e4aaf6.png",
          link_url: "https://www.naver.com",
          visible: false,
          order: null,
          create_time: "2024-07-10T07:44:46.481548Z",
          last_update_time: "2024-07-10T07:44:46.481582Z",
        },
        {
          id: 8,
          banner_image: "/public/banner/d29abda52b.png",
          link_url: "https://www.naver.com",
          visible: false,
          order: null,
          create_time: "2024-07-10T07:44:47.986667Z",
          last_update_time: "2024-07-10T07:44:47.986731Z",
        },
      ],
    };
  },
  methods: {},
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
</style>
