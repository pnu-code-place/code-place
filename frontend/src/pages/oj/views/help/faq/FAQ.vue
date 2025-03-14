<template>
  <div class="faq">
    <div class="section-title">{{ $t('m.Frequently_Asked_Questions') }}</div>

    <nav class="faq-nav">
      <router-link :to="{name: 'faq-judge'}" class="nav-item">채점 프로그램</router-link>
      <router-link :to="{name: 'faq-account'}" class="nav-item">계정</router-link>
      <router-link :to="{name: 'faq-problem'}" class="nav-item">대회 및 문제</router-link>
      <router-link :to="{name: 'faq-tier'}" class="nav-item">티어정보</router-link>
    </nav>
    <router-view></router-view>
  </div>
</template>

<script>
import {defineComponent} from "vue";
import FAQItem from "./FAQItem.vue";

export default defineComponent({
  components: {FAQItem}
})
</script>

<style lang="less" scoped>
.faq {
  width: var(--global-width);

  .faq-nav {
    width: 100%;
    border: 1px solid #dedede;
    border-radius: 7px;
    display: flex;
    background-color: var(--box-background-color);
    margin-bottom: 20px;

    .nav-item {
      font-size: 16px;
      padding: 10px;
      width: 100%;
      text-align: center;
      border-right: 1px solid #dedede;

      &:last-child {
        border-right: none
      }
    }

    a {
      color: var(--text-color);
      font-weight: 700;

      &.router-link-active {
        background-color: rgba(34, 33, 72, 0.82);
        color: #e6f2ff;

        &:hover {
          background-color: rgba(34, 33, 72, 0.82);
        }
      }

      &:hover {
        background: var(--pale-point-color)
      }
    }


  }
}


</style>
