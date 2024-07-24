<template>
  <ConfirmModal
    :title="$t('m.Modify_Home_Banner')"
    :confirmButtonText="$t('m.Save')"
    open
    @onClose="handleClose"
    @onConfirmButtonClick="handleConfirmButtonClick"
  >
    <div style="display: flex; flex-direction: column; gap: 10px">
      <span class="text">
        <span style="color: #ed4b4b">*</span>
        {{ $t("m.Connect_Banner_Link") }}
      </span>
      <input
        type="text"
        :placeholder="$t('m.Link')"
        style="margin-bottom: 20px"
        v-model="linkUrl"
      />
      <span class="text">
        <span style="color: #ed4b4b">*</span>
        {{ $t("m.Banner_Image") }}
      </span>
      <ImageDragAndDropBox @onBannerImageChange="handleBannerImageChange">
      </ImageDragAndDropBox>
      <img
        :src="imageUrl"
        style="width: 100%; border: 1px dashed #bbbbbb; border-radius: 5px"
      />
    </div>
  </ConfirmModal>
</template>

<script>
import ConfirmModal from "@/pages/oj/components/modal/ConfirmModal";
import ImageDragAndDropBox from "@/pages/oj/components/ImageDragAndDropBox";

export default {
  name: "ModifyBannerModal",
  data() {
    return {
      linkUrl: "",
      imageUrl: "",
      imageFile: null,
    };
  },
  components: {
    ConfirmModal,
    ImageDragAndDropBox,
  },
  props: {
    banner: Object,
  },
  mounted() {
    // TODO: 배너 이미지 잘 뜨는지 확인하기.
    this.imageUrl = this.banner.banner_image;
    this.linkUrl = this.banner.link_url;
  },
  methods: {
    handleClose() {
      this.resetData();
      this.$emit("onClose");
    },
    handleConfirmButtonClick() {
      // TODO: 검증 로직 추가.
      // TODO: 배너 추가 api 연결.
      this.resetData();
      this.$emit("onClose");
    },
    resetData() {
      this.linkUrl = "";
      this.imageFile = null;
      this.imageUrl = "";
    },
    async handleBannerImageChange(image) {
      this.imageFile = image;
      this.imageUrl = await this.readImage(image);
    },
    async readImage(image) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = async (e) => {
          resolve(e.target.result);
        };
        reader.readAsDataURL(image);
      });
    },
  },
};
</script>

<style lang="less" scoped>
.text {
  font-size: 15px;
  font-weight: 200;
}

input {
  border: 1px solid #e6e6e6;
  border-radius: 7px;
  font-size: 15px;
  padding: 8px;
  outline: none;
  &::placeholder {
    font-weight: 200;
  }
}
</style>
