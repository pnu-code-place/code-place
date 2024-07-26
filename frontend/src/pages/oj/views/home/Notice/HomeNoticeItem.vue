<script>

import {defineComponent} from "vue";
import ShineWrapper from "../../../components/ShineWrapper.vue";

export default defineComponent({
  name: 'HomeNoticeItem',
  components: {ShineWrapper},
  data() {
    return {
      DAYS_TO_BE_NEW: 3
    }
  },
  props: {
    announcement: {
      type: Object,
      default: () => {
        return {
          title: 'title',
          create_time: '2024-10-10',
          new_flag: false
        }
      }
    },
    isCSEP: {
      type: Boolean,
      default: false
    },
    isSW: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    dateStr() {
      if (this.isCSEP) {
        let onlyDate = new Date(this.announcement.create_time);
        return onlyDate.toLocaleDateString();
      } else if (this.isSW) {
        return this.announcement.pubDate.split(' ')[0];
      }
    },
    isNew() {
      if (this.isCSEP) {
        const currentTime = new Date().getTime();
        const createTimestamp = new Date(this.announcement.create_time).getTime();
        const oneDayInMilliseconds = 24 * 60 * 60 * 1000 * this.DAYS_TO_BE_NEW;
        return (currentTime - createTimestamp) <= oneDayInMilliseconds;
      } else if (this.isSW) {
        this.dateStr === new Date().toISOString().split('T')[0];
      }
    },
    csepClass() {
      return this.isCSEP ? 'csep' : '';
    },
    swClass() {
      return this.isSW ? 'sw-center' : '';
    },
    itemClass() {
      return `${this.csepClass} ${this.swClass}`;
    }
  },
  methods: {
    goAnnouncement() {
      this.$router.push({name: 'notice', params: {announcement: this.announcement}});
    },
    goSW() {
      window.open(this.announcement.link);
    },
    clickHandler() {
      if (this.isCSEP) {
        this.goAnnouncement();
      } else if (this.isSW) {
        this.goSW();
      }
    }
  }
})
</script>

<template>
  <li :class="this.itemClass" @click="clickHandler">
    <div class="flex-container">
      <div class="left">
        <div class="title">
          {{ announcement.title }}
        </div>
        <span class="new-annotator" v-if="isNew"><span>NEW</span></span>
        <span class="csep-annotator" v-if="isCSEP">
                  <shine-wrapper>CSEP</shine-wrapper>
          </span>
        <span class="sw-center-annotator" v-if="isSW">
                  <shine-wrapper>SW</shine-wrapper>
          </span>
      </div>
      <div class="right">
        <div class="date">
          {{ dateStr }}
        </div>
      </div>
    </div>
  </li>
</template>

<style scoped lang="less">
li {
  width: 100%;
  padding: 7px 0 7px 20px;
  list-style: none;
  background-color: rgba(251, 251, 251, 0.5);
  border-radius: 7px;
  font-size: 16px;
  margin-bottom: 5px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  cursor: pointer;

  &:last-child {
    border-bottom: none;
  }

  .flex-container {
    width: 100%;
    display: flex;
    justify-content: space-between;

    .left {
      width: calc(100% - var(--announcement-date-width));
      display: flex;
      gap: 6px;
      justify-content: space-between;

      .title {
        width: 100%;
        text-align: left;
        text-decoration: none;
        font-size: 14px;
        font-weight: 600;
        color: var(--ps-content-text-color);
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }

      .new-annotator {
        background-color: #fa6c6c;
        border-radius: 4px;
        color: #ffffff;
        font-size: 10px;
        text-align: center;
        width: 35px;
        margin: auto;
        font-weight: 600;
      }

      .csep-annotator {
        background-color: var(--point-color);
        border-radius: 4px;
        color: #ffffff;
        font-size: 10px;
        text-align: center;
        width: 35px;
        margin: auto;
        font-weight: 600;
      }

      .sw-center-annotator {
        background-image: linear-gradient(45deg, var(--pnu-blue), var(--pnu-green));
        border-radius: 4px;
        color: #ffffff;
        font-size: 10px;
        text-align: center;
        width: 35px;
        margin: auto;
        font-weight: 600;
      }
    }

    .right {
      .date {
        flex: none;
        width: var(--announcement-date-width);
        text-align: center;
        font-size: small;
        color: #737373;
      }
    }
  }

  &.csep {
    background-color: var(--pale-point-color);
    color: #ffffff;
  }

  &.sw-center {
    // duel background color divided by diagonal line
    background-image: linear-gradient(45deg, var(--pale-pnu-blue), var(--pale-pnu-green));
  }

  &:hover {
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
    transform: scale(1.01);
  }
}
</style>
