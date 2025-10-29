<template>
  <div class="create-post-container">
    <button class="create-post-btn" @click="goToCreatePost">
      <i class="fa fa-plus"></i>
      {{ $t("m.Community_Create_Post") }}
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
  padding: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background-color: #409eff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;

  .fa-plus {
    margin-right: 8px;
  }

  &:hover {
    background-color: #66b1ff;
  }
}
</style>
