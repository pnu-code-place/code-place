<script>
export default {
  name: "draw-card",
  props: {
    title: {
      type: String,
      default: "title",
    },
    createTime: {
      type: String,
      default: "2024-10-10",
    },
    author: {
      type: String,
      default: "author",
    },
    link: {
      type: String,
      default: "no-link",
    },
    noticeIndex: {
      type: Number,
      default: -1,
    },
  },
  computed: {
    hasLink() {
      return this.link !== "no-link"
    },
  },
  methods: {
    goLink() {
      if (this.hasLink) {
        window.open(this.link, "_blank")
      }
    },
    goAnnouncement() {
      if (this.noticeIndex !== -1) {
        this.$router.push({
          name: "notice",
          params: { notice: this.noticeIndex },
        })
      }
    },
    clickHandler() {
      if (this.hasLink) {
        this.goLink()
      } else {
        this.goAnnouncement()
      }
    },
    goAuthor() {
      if (this.link === "no-link") {
        this.$router.push({
          name: "user-profile",
          params: { username: this.author },
        })
      }
    },
  },
  // methods: {
  //   goAnnouncement(announcement) {
  //     this.$router.push({})
  //   }
  // }
}
</script>

<template>
  <li class="notice-wrapper">
    <div class="notice-item">
      <div class="notice-header">
        <span class="notice-author" @click="goAuthor"
          >{{ author }}
          <span v-if="hasLink" class="sw-center"
            >({{ $t("m.SWCenter") }})</span
          ></span
        >
        <span class="notice-date"
          ><span class="new-badge">new</span>{{ createTime }}</span
        >
      </div>
      <h3 class="notice-title" @click="clickHandler">
        {{ title }}
      </h3>
    </div>
  </li>
</template>

<style scoped lang="less">
.notice-wrapper {
  height: 75px;
  transform: matrix3d(
    1,
    0,
    0,
    0,
    0,
    0.98,
    -0.17,
    0,
    0,
    0.17,
    0.98,
    0,
    0,
    0,
    0,
    1
  );
  list-style: none;
  transition: transform 0.3s;

  &:hover {
    transform: matrix3d(
      1,
      0,
      0,
      0,
      0,
      0.98,
      -0.17,
      0,
      0,
      0.17,
      0.98,
      0,
      0,
      -50,
      0,
      1
    );
  }
}

.notice-item {
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: var(--box-background-color);
  border-radius: 5px;
  padding: 15px 30px 15px;
  height: 400px;
  box-shadow: rgba(0, 0, 0, 0.3) 0 0 8px 0;
  flex-shrink: 0;

  .notice-header {
    display: flex;
    font-size: 14px;
    color: #888;
    justify-content: space-between;

    .new-badge {
      background-color: #f55;
      color: #fff;
      padding: 2px 5px;
      border-radius: 5px;
      font-size: 12px;
      font-weight: 600;
      margin-right: 10px;
    }

    .sw-center {
      font-size: 12px;
      color: #888;
    }
  }

  .notice-title {
    font-size: 20px;
  }

  &:hover {
    border: 1px solid #ccc;
  }
}
</style>
