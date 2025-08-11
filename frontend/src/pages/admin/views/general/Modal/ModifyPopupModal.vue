<template>
  <ConfirmModal
    :title="$t('m.Modify_Popup_Banner')"
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
  name: "ModifyPopupModal",
  data() {
    return {
      linkUrl: "",
      imageUrl: "",
      imageFile: null,
      hasLinkUrlError: false,
      hasImageFileError: false,
      hasWidthError: false,
      width: 300,
    }
  },
  components: {
    ConfirmModal,
    ImageDragAndDropBox,
  },
  props: {
    banner: Object,
  },
  mounted() {
    this.imageUrl = this.banner.popup_image
    this.linkUrl = this.banner.link_url
    this.width = this.banner.popup_image_width || 300
  },
  methods: {
    handleClose() {
      this.resetData()
      this.$emit("onClose")
    },
    async handleConfirmButtonClick() {
      if (this.linkUrl === "") this.hasLinkUrlError = true
      if (this.imageFile === null && this.imageFile !== "")
        this.imageFile = await this.convertURLtoFile(this.imageUrl)
      if (this.imageFile === null) this.hasImageFileError = true

      if (this.hasLinkUrlError || this.hasImageFileError) return

      const formData = new FormData()
      formData.append("link_url", this.linkUrl)
      formData.append("image", this.imageFile)
      formData.append("image_width", this.width)

      api
        .modifyPopup(this.banner.id, formData)
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
    async convertURLtoFile(url) {
      const response = await fetch(url)
      const data = await response.blob()
      const filename = url.split("/").pop() // url 구조에 맞게 수정할 것
      const metadata = { type: `image/jpeg` }
      return new File([data], filename, metadata)
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
