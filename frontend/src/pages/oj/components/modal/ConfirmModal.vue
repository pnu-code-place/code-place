<template>
  <div v-if="isOpen" class="modal-wrapper" @click="onCloseEmit">
    <div class="modal-container" :style="modalStyles">
      <div class="modal-title">
        {{ title }}
        <i class="el-icon-close" style="width: 20px; cursor: pointer"></i>
      </div>
      <div class="modal-content">
        <slot></slot>
      </div>
      <div class="modal-foot">
        <button
          style="
            border: 1px solid #409eff;
            color: #409eff;
            background-color: rgb(239, 245, 253);
          "
          @click="onCloseEmit"
        >
          {{ $t("m.Modal_Cancel") }}
        </button>
        <button
          style="background-color: #409eff; color: white"
          @click="onConfirmButtonClickEmit"
        >
          {{ confirmButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ConfirmModal",
  props: {
    isOpen: Boolean,
    title: String,
    confirmButtonText: String,
    width: { type: Number, default: 400 },
  },
  methods: {
    onCloseEmit() {
      this.$emit("onClose");
    },
    onConfirmButtonClickEmit() {
      this.$emit("onConfirmButtonClick");
    },
  },
  computed: {
    modalStyles() {
      return {
        width: `${this.width}px`,
      };
    },
  },
};
</script>

<style lang="less" scoped>
.modal-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 101;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.3);
}
.modal-container {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 10px;
  border-radius: 5px;
  background-color: white;
}
.modal-title {
  padding: 10px;
  display: flex;
  justify-content: space-between;
  color: #333;
  font-size: 18px;
  font-weight: 300;
}
.modal-content {
  padding: 20px;
}
.modal-foot {
  display: flex;
  justify-content: right;
  gap: 10px;
}

button {
  cursor: pointer;
  background-color: white;
  border-radius: 5px;
  border: none;
  padding: 8px 16px;
  margin: 0;
  &:hover {
    opacity: 70%;
  }
}
</style>
