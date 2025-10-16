<template>
  <main>
    <div class="session-title-wrapper">
      <h1 class="session-title main-title">{{ $t("m.Community") }}</h1>
    </div>
    <table class="community-table">
      <thead>
        <th>ID</th>
        <th style="padding-left: 50px; text-align: left">
          {{ $t("m.Community_Title") }}
        </th>
        <th>
          {{ $t("m.Community_Author") }}
        </th>
        <th>
          {{ $t("m.Community_CreatedAt") }}
        </th>
      </thead>
      <tbody>
        <tr v-for="post in posts" :key="post.id">
          <td>{{ post.id }}</td>
          <td class="td-title">
            <p class="community-title">{{ post.title }}</p>
            <p class="community-content">{{ truncate(post.content, 100) }}</p>
          </td>
          <td>{{ post.author_name }}</td>
          <td style="font-size: 13px">
            <p>{{ post.created_at | localtime("YYYY / MM / DD") }}</p>
          </td>
        </tr>
      </tbody>
    </table>
    <Pagination
      :total="total"
      :page-size.sync="query.limit"
      @on-change="handlePageChange"
      :current.sync="query.page"
      :show-sizer="true"
      @on-page-size-change="handleSizeChange"
    ></Pagination>
  </main>
</template>

<script>
import api from "../../api"
import Pagination from "@/pages/admin/components/Pagination.vue"

export default {
  name: "Community",
  components: {
    Pagination,
  },
  mounted() {
    this.fetchPosts()
  },
  data() {
    return {
      posts: [],
      total: 0,
      query: {
        page: 1,
        limit: 10,
      },
    }
  },
  methods: {
    async fetchPosts() {
      const offset = (this.query.page - 1) * this.query.limit
      const res = await api.getCommunityPostList(offset, this.query.limit)
      this.posts = res.data.data.results
      this.total = res.data.data.total
    },
    handlePageChange(page) {
      this.query.page = page
      this.fetchPosts()
    },
    handleSizeChange(size) {
      this.query.page = 1
      this.query.limit = size
      this.fetchPosts()
    },
    truncate(text, length) {
      if (text.length > length) {
        return text.substring(0, length) + "..."
      }
      return text
    },
  },
}
</script>

<style lang="less" scoped>
main {
  width: var(--global-width);

  .session-title-wrapper {
    margin: 0 4px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .session-title {
    font-weight: 700;
  }

  .community-table {
    margin-bottom: 20px;
    border: 1px solid var(--container-border-color);
    border-radius: var(--container-border-radius);
    background-color: white;
    text-align: center;
    border-collapse: collapse;
    width: 100%;

    thead {
      border-bottom: 1px solid var(--container-border-color);
    }

    th {
      padding: 10px 0px;
      font-size: 16px;
      font-weight: 600;
      color: var(--container-comment-color);
    }

    tbody tr {
      transition: all 0.3s ease;
      border-bottom: 1px solid var(--container-border-color);
    }

    tbody tr:last-child {
      border-bottom: none;
    }

    tbody tr:hover {
      background-color: #f5f7fa;
    }

    td {
      cursor: default;
      width: 80px;
      padding: 10px;
      font-size: 15px;
    }

    .td-title {
      cursor: pointer;
      width: 350px;
      padding-left: 50px;
      text-align: left;

      .community-title {
        font-size: 18px;
        font-weight: 600;
      }

      .community-content {
        color: #a9a9a9;
        font-size: 14px;
      }
    }
  }
}
</style>
