<script>
export default {
  name: 'ProblemSkeleton'
}
</script>

<template>
  <div class="problem-skeleton">
    <ul class="problem-skeleton__status">
      <li class="problem-skeleton__status__item"></li>
      <li class="problem-skeleton__status__item"></li>
      <li class="problem-skeleton__status__item"></li>
      <li class="problem-skeleton__status__item"></li>
    </ul>
    <hr/>
    <div class="problem-tab">
      <div class="title"></div>
      <ul class="problem-tab__content">
        <li class="problem-tab__content__item"></li>
<!--        <li class="problem-tab__content__item"></li>-->
<!--        <li class="problem-tab__content__item"></li>-->
      </ul>
    </div>
    <hr/>
    <div class="problem-tab">
      <div class="title"></div>
      <ul class="problem-tab__content">
        <li class="problem-tab__content__item"></li>
<!--        <li class="problem-tab__content__item"></li>-->
<!--        <li class="problem-tab__content__item"></li>-->
      </ul>
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

li {
  list-style: none;
}

hr {
  border: 0;
  border-top: 0.5px solid #dedede;
  margin: 20px 0;
}

.problem-skeleton {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  padding: 0 30px 0 10px;

  .problem-skeleton__status {
    width: 100%;
    display: flex;
    gap: 30px;
    flex-shrink: 0;
    justify-content: space-between;
    padding: 50px 25%;

    .problem-skeleton__status__item {
      width: 75px;
      height: 42px;
      background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
      background-size: 400% 100%;
      animation: loading 1.5s infinite;
      border-radius: 10px;
    }
  }

  .problem-tab {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px;

    .title {
      width: 200px;
      height: 35px;
      margin-bottom: 20px;
      background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
      background-size: 400% 100%;
      animation: loading 1.5s infinite;
      border-radius: 20px;
    }

    .problem-tab__content {
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 20px;

      .problem-tab__content__item {
        width: 100%;
        height: 25px;
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 400% 100%;
        animation: loading 1.5s infinite;
        border-radius: 20px;
      }
    }
  }
}
</style>
