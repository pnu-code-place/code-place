<script>
export default {
  data() {
    return {
      activeTab: "all",
    }
  },
  methods: {
    goToCreatePost() {
      this.$router.push({
        name: "contest-community-create",
        params: { contestID: this.$route.params.contestID },
      })
    },
  },
}
</script>

<template>
  <div class="contest-community">
    <div class="community-header">
      <div class="left-section">
        <p>{{ $t("m.Contest_Community") }}</p>
        <div class="segmented">
          <div class="indicator" :class="{ right: activeTab === 'my' }"></div>
          <button
            :class="{ active: activeTab === 'all' }"
            @click="activeTab = 'all'"
          >
            {{ $t("m.Contest_All_Posts") }}
          </button>
          <button
            :class="{ active: activeTab === 'my' }"
            @click="activeTab = 'my'"
          >
            {{ $t("m.Contest_My_Questions") }}
          </button>
        </div>
      </div>
      <Button class="write-btn" @click="goToCreatePost">{{
        $t("m.Community_Create_Comment_Btn")
      }}</Button>
    </div>
  </div>
</template>

<style scoped lang="less">
.contest-community {
  border: 1px solid #e9ece9;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--box-background-color);
  padding: 15px 20px;
  border-radius: 7px;
}
.community-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  p {
    text-decoration: none;
    font-size: 24px;
    font-weight: bold;
  }
}
.left-section {
  display: flex;
  gap: 20px;
  align-items: center;
}
.segmented {
  position: relative;
  display: flex;
  width: 150px;
  height: 30px;
  border-radius: 10px;
  overflow: hidden;
  background: #f3f4f6;
}
.segmented button {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: medium;
  cursor: pointer;
  z-index: 2;
  transition: color 0.25s ease;
}
.segmented button.active {
  color: white;
  font-weight: 600;
}
.indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background: #494a67;
  border-radius: 10px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
}
.indicator.right {
  transform: translateX(100%);
}
.write-btn {
  background: #3475e0;
  color: white;
  border-radius: 10px;
  font-weight: bold;
}
</style>
