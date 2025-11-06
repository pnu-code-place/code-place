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
  background: var(--point-color);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(50, 48, 107, 0.25);
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
    box-shadow: 0 6px 16px rgba(50, 48, 107, 0.35);
    background: #4a4890;

    &::before {
      opacity: 1;
    }
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(50, 48, 107, 0.25);
  }
}
</style>
