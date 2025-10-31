<template>
  <div class="create-post-container">
    <button class="create-post-btn" @click="goToCreatePost">
      <span>{{ $t("m.Community_Create_Post") }}</span>
    </button>
  </div>
</template>

<script>
export default {
  name: "CreatePost",
  methods: {
    goToCreatePost() {
      this.$router.push({ name: "community-create" });
    },
  },
};
</script>

<style lang="less" scoped>
.create-post-container {
  margin-bottom: 20px;
}

.create-post-btn {
  width: 100%;
  padding: 16px 20px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  span {
    position: relative;
    z-index: 1;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(52, 152, 219, 0.3);
    background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);

    &::before {
      opacity: 1;
    }
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
  }
}
</style>
