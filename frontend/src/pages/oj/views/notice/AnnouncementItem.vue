<script>
export default {
  data() {
    return {}
  },
  props: {
    announcement: {
      type: Object,
      default: () => {
        return {
          id: 1,
          created_by: {
            id: 1,
            username: "root",
            email: "root",
            real_name: null,
            student_id: null,
            school: "대학",
            major: "전공",
          },
          title: "제목",
          content: "<p>컨텐츠가 없습니다.</p>",
          create_time: "2024-07-21T16:33:17.914693Z",
          last_update_time: "2024-07-21T16:33:17.914733Z",
          visible: true,
        }
      },
    },
  },
  computed: {
    createTime() {
      if (this.announcement.create_time.split("T").length > 1) {
        return this.announcement.create_time.split("T")[0]
      } else {
        return this.announcement.create_time
      }
    },
  },
  methods: {
    goAnnouncement() {
      this.$router.push({
        name: "notice-details",
        params: { noticeID: this.announcement.id },
      })
    },
  },
}
</script>

<template>
  <tr
    class="announcement-item"
    :class="{ pinned: announcement.is_pinned }"
    @click="goAnnouncement"
  >
    <td class="id">{{ announcement.id }}</td>
    <td class="title">
      <span v-if="announcement.is_pinned">&#x1F4CC; </span>
      {{ announcement.title }}
    </td>
    <td class="date">{{ this.createTime }}</td>
    <td class="creator">{{ announcement.created_by.username }}</td>
  </tr>
</template>

<style scoped lang="less">
.announcement-item.pinned {
  background-color: rgba(242, 224, 254, 0.5) !important;
  td {
    border-bottom: 1px solid #e0e0e0 !important;
  }
}
.announcement-item {
  cursor: pointer;
  transition:
    background-color 0.2s ease-in-out,
    box-shadow 0.2s ease-in-out;
  td {
    padding: 10px;
    border-bottom: 1px solid #f0f0f0;
    font-size: 16px;
  }
  .id {
    width: 10%;
    text-align: center;
  }
  .title {
    width: 60%;
    text-align: left;
    font-size: 18px;
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .date {
    width: 15%;
    text-align: center;
  }
  .creator {
    width: 15%;
    text-align: center;
  }
  &:hover {
    background-color: var(--site-background-color);
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
  }
}
</style>
