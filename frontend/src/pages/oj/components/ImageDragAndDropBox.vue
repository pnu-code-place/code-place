<template>
  <div class="container">
    <input
      type="file"
      ref="fileInput"
      accept=".png,.jpg,.jpeg"
      id="input-file"
      style="display: none"
      @change="onFileChange"
    />
    <div
      class="drag-n-drop-box"
      @dragenter="onDragenter"
      @dragover="onDragover"
      @dragleave="onDragleave"
      @drop="onDrop"
      @click="onClick"
    >
      <i class="el-icon-picture" style="color: #bbbbbb; font-size: 40px"></i>
      <span style="color: #bbbbbb">{{ $t("m.Image_Max_Size_Alert") }}</span>
      <label htmlFor="input-file" role="button" class="label">
        {{ $t("m.Bring_Image") }}
      </label>
    </div>
  </div>
</template>

<script>
export default {
  name: "ImageDragAndDropBox",
  props: {
    bannerImage: File,
  },
  data() {
    return {
      isDragging: true,
      imageUrl: "",
    };
  },
  methods: {
    onClick() {
      this.$refs.fileInput.click();
    },
    onDragenter(event) {
      event.preventDefault();
      event.stopPropagation();
      this.isDragging = true;
    },
    onDragleave(event) {
      event.preventDefault();
      event.stopPropagation();
      this.isDragging = false;
    },
    onDragover(event) {
      event.preventDefault();
      event.stopPropagation();
      if (event.dataTransfer.files) {
        this.isDragging = true;
      }
    },
    onDrop(event) {
      event.preventDefault();
      event.stopPropagation();
      this.isDragged = false;
      if (
        event.dataTransfer.files &&
        this.checkFileSize(event.dataTransfer.files[0])
      ) {
        this.$emit("onBannerImageChange", event.dataTransfer.files[0]);
      }
    },
    onFileChange(event) {
      if (event.target.files && this.checkFileSize(event.target.files[0])) {
        this.$emit("onBannerImageChange", event.target.files[0]);
      }
    },
    checkFileSize(file) {
      // const limitSize = 1024 ** 2 * 10; // 10MB
      const limitSize = 1024 * 10; // 10MB
      if (file.size > limitSize) {
        alert(this.$t("m.Image_Max_Size_Alert"));
        return false;
      }
      return true;
    },
  },
};
</script>

<style lang="less" scoped>
.container {
  width: 100%;
  margin: 0 auto;
}
.drag-n-drop-box {
  border-radius: 10px;
  border: 1px dashed #bbbbbb;
  padding: 12px;
  background-color: #fafafa;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}
.label {
  background-color: #bbbbbb;
  border-radius: 5px;
  padding: 4px 8px;
  color: white;
  cursor: pointer;
}
</style>
