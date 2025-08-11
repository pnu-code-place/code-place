<script>
export default {
  name: "ProblemSkeleton",
  data() {
    return {
      amount: 3,
      interval: null,
    }
  },
  mounted() {
    this.interval = setInterval(() => {
      this.amount += 1
      if (this.amount > 120) {
        clearInterval(this.interval)
      }
    }, 200)
  },
}
</script>

<template>
  <div class="problem-skeleton">
    <transition-group name="fade" tag="ul" class="problem-tab__content">
      <li
        v-for="i in 100"
        :key="i"
        v-if="i < amount"
        class="problem-tab__content__item"
      ></li>
    </transition-group>
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

li {
  list-style: none;
}

.problem-skeleton {
  display: flex;
  gap: 20px;
  width: 100%;
  padding: 10px 20px;
  align-content: center;

  .problem-tab__content {
    width: 100%;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    .problem-tab__content__item {
      padding: 4px;
      font-size: 1rem;
      background-color: #cfe2ff;
      border-radius: 5px;
      min-width: 59px;
      height: 35px;
      display: block;
    }
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: transform 1s;
}
.fade-enter,
.fade-leave-to {
  transform: translateX(100%);
}
</style>
