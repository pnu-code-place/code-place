<template>
  <ConfirmModal
    :title="$t('m.Add_Home_Popup')"
    :confirmButtonText="$t('m.Save')"
    open
    @onClose="handleClose"
    @onConfirmButtonClick="handleConfirmButtonClick"
  >
    <div style="display: flex; flex-direction: column; gap: 10px">
      <span class="text">
        <span style="color: #ed4b4b">*</span>
        {{ $t("m.Connect_Popup_Link") }}
      </span>
      <input
        type="text"
        :placeholder="$t('m.Link')"
        :style="[hasLinkUrlError && { 'border-color': '#ed4b4b' }]"
        v-model="linkUrl"
        @click="hasLinkUrlError = false"
      />
      <span class="text">
        <span style="color: #ed4b4b">*</span>
        {{ $t("m.Width") }}
      </span>
      <input
        type="number"
        :placeholder="$t('m.Width')"
        :style="[hasWidthError && { 'border-color': '#ed4b4b' }]"
        v-model="width"
        @click="hasWidthError = false"
      />
      <span v-if="hasLinkUrlError" style="color: #ed4b4b; font-size: 13px">
        {{ $t("m.URL_Link_Has_Error") }}
      </span>
      <span class="text" style="margin-top: 20px">
        <span style="color: #ed4b4b">*</span>
        {{ $t("m.Popup_Image") }}
      </span>
      <div
        style="border-radius: 10px"
        :style="[hasImageFileError && { border: '1px solid #ed4b4b' }]"
        @click="hasImageFileError = false"
      >
        <ImageDragAndDropBox @onBannerImageChange="handlePopupImageChange">
        </ImageDragAndDropBox>
      </div>
      <span v-if="hasImageFileError" style="color: #ed4b4b; font-size: 13px">
        {{ $t("m.Image_File_Has_Error") }}
      </span>

      <img
        v-if="imageUrl !== ''"
        :src="imageUrl"
        style="width: 100%; border: 1px dashed #bbbbbb; border-radius: 5px"
      />
    </div>
  </ConfirmModal>
</template>

<script>
import api from "../../../api.js"

import ConfirmModal from "@/pages/oj/components/modal/ConfirmModal"
import ImageDragAndDropBox from "@/pages/oj/components/ImageDragAndDropBox"

export default {
  name: "AddPopupModal",
  data() {
    return {
      linkUrl: "",
      imageUrl: "",
      imageFile: null,
      hasLinkUrlError: false,
      hasImageFileError: false,
      width: 300,
    }
  },
  components: {
    ConfirmModal,
    ImageDragAndDropBox,
  },
  methods: {
    handleClose() {
      this.resetData()
      this.$emit("onClose")
    },
    handleConfirmButtonClick() {
      if (this.linkUrl === "") this.hasLinkUrlError = true
      if (this.imageFile === null) this.hasImageFileError = true

      if (this.hasLinkUrlError || this.hasImageFileError) return
      if (this.width === "") {
        alert("너비를 입력해주세요.")
        return
      }
      if (this.width < 50) {
        alert("너비는 50 이상이어야 합니다.")
        return
      }

      const formData = new FormData()
      formData.append("link_url", this.linkUrl)
      formData.append("image", this.imageFile)
      formData.append("image_width", this.width)

      api
        .addPopup(formData)
        .then((res) => {
          if (res.status === 200) {
            this.resetData()
            this.$emit("onClose")
          }
        })
        .catch((res) => {
          if (res.data.data === "Invalid URL") this.hasLinkUrlError = true
        })
    },
    resetData() {
      this.linkUrl = ""
      this.imageFile = null
      this.imageUrl = ""
    },
    async handlePopupImageChange(image) {
      this.imageFile = image
      this.imageUrl = await this.readImage(image)
    },
    async readImage(image) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = async (e) => {
          resolve(e.target.result)
        }
        reader.readAsDataURL(image)
      })
    },
  },
}
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
