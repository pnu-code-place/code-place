<script setup>
export default {
  name: "DashboardSkeleton",
}
</script>

<template>
  <div class="dashboard-skeleton">
    <div class="dashboard-skeleton__graph">
      <div class="dashboard-skeleton__header__title"></div>
      <div class="dashboard-skeleton__header__subtitle"></div>
    </div>
    <div class="dashboard-skeleton__content">
      <div class="dashboard-skeleton__content__row" />
      <div class="dashboard-skeleton__content__row" />
      <div class="dashboard-skeleton__content__row" />
      <div class="dashboard-skeleton__content__row" />
      <div class="dashboard-skeleton__content__row" />
      <div class="dashboard-skeleton__content__row" />
    </div>
  </div>
</template>

<style scoped lang="less">
@keyframes loading {
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 100% 0%;
  }
}

.dashboard-skeleton {
  display: flex;
  gap: 20px;
  width: 100%;
  padding: 0 30px 0 10px;

  .dashboard-skeleton__graph {
    height: 250px;
    width: 30%;
    flex-direction: column;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 400% 100%;
    animation: loading 1.5s infinite;
    border-radius: 100%;
  }

  .dashboard-skeleton__content {
    width: 75%;
    display: flex;
    flex-direction: column;
    gap: 15px;

    .dashboard-skeleton__content__row {
      width: 100%;
      height: 25px;
      background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
      background-size: 400% 100%;
      animation: loading 1.5s infinite;
      border-radius: 20px;
    }
  }
}
</style>
