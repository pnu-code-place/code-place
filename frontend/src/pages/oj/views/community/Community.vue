<template>
  <main>
    <ErrorSign v-if="this.error" :code="this.error.code || 404" :description="this.error.description || ''"
      :solution="this.error.solution || ''" />
    <div class="contents" v-else>
      <div class="session-title-wrapper">
        <h1 class="session-title main-title">{{ $t("m.Community") }}</h1>
      </div>
      <div class="box-wrapper">
        <div class="left-container">
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
              <tr v-for="post in posts" :key="post.id" @click="goToPost(post.id)" class="post-row">
                <td>{{ post.id }}</td>
                <td class="td-title">
                  <div class="title-wrapper">
                    <p class="community-title">{{ post.title }}</p>
                    <span v-if="post.comment_count > 0" class="comment-count">
                      <i class="fa fa-comment"></i>
                      {{ post.comment_count }}
                    </span>
                  </div>
                  <p class="community-content">{{ post.content_preview }}</p>
                </td>
                <td class="user-info">
                  <router-link :to="{
                    name: 'user-home',
                    params: { username: post.author_name },
                  }">
                    <img class="avatar" :src="post.author_avatar ||
                      'https://cdn-icons-png.flaticon.com/512/473/473406.png'
                      " alt="avatar" />
                    <span>{{ post.author_name }}</span>
                  </router-link>
                </td>
                <td style="font-size: 13px">
                  <p>{{ post.created_at | localtime("YYYY / MM / DD") }}</p>
                </td>
              </tr>
            </tbody>
          </table>
          <Pagination :total="total" :page-size.sync="query.limit" @on-change="handlePageChange"
            :current.sync="query.page" :show-sizer="true" @on-page-size-change="handleSizeChange"></Pagination>
        </div>
        <div class="right-container">
          <CreatePost />
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import api from "../../api"
import Pagination from "@/pages/admin/components/Pagination.vue"
import ErrorSign from "../general/ErrorSign.vue"
import CreatePost from "./communityComponent/CreatePost.vue";

export default {
  name: "Community",
  components: {
    CreatePost,
    Pagination,
    ErrorSign,
  },
  mounted() {
    this.fetchPosts()
  },
  data() {
    return {
      isLoading: false,
      error: null,
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
      this.isLoading = true

      const offset = (this.query.page - 1) * this.query.limit

      api
        .getCommunityPostList(offset, this.query.limit)
        .then((res) => {
          this.posts = res.data.data.results
          this.total = res.data.data.total
        })
        .catch((err) => {
          // TODO: 현재 프론트엔드 버전 상 Optional Chaining 문법을 사용할 수 없습니다.
          // 만약 사용 가능하다면, err?.response?.status 와 같은 문법으로 변경해야 합니다.
          this.error = {
            code: (err.response && err.response.status) || 500,
            description:
              (err.response &&
                err.response.data &&
                err.response.data.message) ||
              this.$t("m.Community_Default_Error_Description"),
            solution: this.$t("m.Community_Default_Error_Solution"),
          }
        })
        .finally(() => {
          this.isLoading = false
        })
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
    goToPost(postId) {
      this.$router.push({ name: "community-detail", params: { postId } })
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

  .box-wrapper {
    display: flex;
    justify-content: space-between;
  }

  .left-container {
    width: 72%;
    height: 100%;
  }

  .right-container {
    width: 26%;
    height: auto;
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

    .post-row {
      cursor: pointer;
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

      .title-wrapper {
        display: flex;
        align-items: center;
      }

      .community-title {
        font-size: 18px;
        font-weight: 600;
        margin-right: 8px;
      }

      .comment-count {
        font-size: 14px;
        color: #8792a2;

        .fa-comment {
          margin-right: 3px;
        }
      }

      .community-content {
        color: #a9a9a9;
        font-size: 14px;
      }
    }

    .user-info {
      width: 200px;
    }

    .user-info a {
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      color: #495060;
    }

    .user-info a:hover {
      color: #2d8cf0;
    }

    .avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      margin-right: 10px;
      background: linear-gradient(90deg, #f0f0f0 25%, #f5f5f5 50%, #f0f0f0 75%);
    }
  }
}
</style>
