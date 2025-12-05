<template>
  <main>
    <div class="container">
      <div class="session-title-wrapper">
        <h1 class="session-title main-title">
          <Icon type="ios-create" size="32"></Icon>
          {{ $t("m.Community_Create_Post") }}
        </h1>
      </div>

      <div class="form-card">
        <Form :model="post" :rules="ruleValidate" ref="form" label-position="top">
          <Row :gutter="20">
            <Col :span="20">
            <FormItem :label="$t('m.Community_Title')" prop="title">
              <Input v-model="post.title" type="text" size="large" :placeholder="$t('m.Community_Title_Placeholder')" />
            </FormItem>
            </Col>
            <Col :span="4">
            <FormItem :label="$t('m.Community_Post_Type')" prop="post_type">
              <Select v-model="post.post_type" size="large">
                <Option v-for="(type, key) in availablePostTypes" :key="key" :value="key">{{ type.name }}</Option>
              </Select>
            </FormItem>
            </Col>
          </Row>
          <FormItem :label="$t('m.Community_Content')" prop="content" class="content-form-item">
            <TiptapEditor v-model="post.content" />
          </FormItem>
          <div class="form-actions">
            <Button type="primary" @click.prevent="submitPost" :loading="loading" size="large">
              <Icon type="ios-checkmark-circle-outline"></Icon>
              {{ $t("m.Submit") }}
            </Button>
            <Button @click="$router.go(-1)" size="large">
              <Icon type="ios-close-circle-outline"></Icon>
              {{ $t("m.Cancel") }}
            </Button>
          </div>
        </Form>
      </div>
    </div>
  </main>
</template>

<script>
import api from "@oj/api";
import { POST_TYPE } from "@/utils/constants";
import { mapGetters } from "vuex";
import TiptapEditor from "../../components/TiptapEditor.vue";

export default {
  name: "CreatePostPage",
  components: {
    TiptapEditor,
  },
  data() {
    return {
      loading: false,
      post: {
        title: "",
        content: "",
        post_type: "ARTICLE",
        problem_id: null,
        contest_id: null,
      },
      ruleValidate: {
        title: [
          { required: true, message: this.$t("m.Community_Title_Required"), trigger: "blur" },
        ],
        content: [
          {
            required: true,
            message: this.$t("m.Community_Content_Required"),
            trigger: "blur",
          },
        ],
      },
    };
  },
  computed: {
    ...mapGetters(["isSuperAdmin"]),
    availablePostTypes() {
      // Super Admin이 아닌 경우 ANNOUNCEMENT 타입 제외
      if (!this.isSuperAdmin) {
        const { ANNOUNCEMENT, ...filteredTypes } = POST_TYPE;
        return filteredTypes;
      }
      return POST_TYPE;
    },
  },
  created() {
    this.post.problem_id = this.$route.query.problemID || null;
    this.post.contest_id = this.$route.query.contestID || null;
  },
  methods: {
    submitPost() {
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.loading = true;
          api
            .createPost(this.post)
            .then((res) => {
              this.$success("Post created successfully");
              this.$router.push({
                name: "community-detail",
                params: { postId: res.data.data.id },
              });
            })
            .catch((err) => {
              console.error("Error creating post:", err);
            })
            .finally(() => {
              this.loading = false;
            });
        }
      });
    },
  },
};
</script>

<style lang="less" scoped>
main {
  width: var(--global-width);
  margin: 0 auto;
  padding: 30px 0;
}

.container {
  width: 100%;
}

.session-title-wrapper {
  margin: 0 4px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
}

.session-title {
  font-weight: 700;
  font-size: 32px;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 12px;

  .ivu-icon {
    color: #3498db;
  }
}

.form-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e8ecef;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  }
}

/deep/ .ivu-form-item-label {
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  padding-bottom: 8px;
}

/deep/ .ivu-input {
  border: 1px solid #e8ecef;
  border-radius: 8px;
  font-size: 15px;
  color: #2c3e50;
  transition: all 0.3s ease;

  &:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  }

  &:hover {
    border-color: #d5dce0;
  }
}

/deep/ .ivu-input-large {
  padding: 10px 14px;
  font-size: 16px;
}

/deep/ .ivu-select-selection {
  border: 1px solid #e8ecef;
  border-radius: 8px;
  transition: all 0.3s ease;

  &:hover {
    border-color: #d5dce0;
  }
}

/deep/ .ivu-select-focused .ivu-select-selection {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.content-form-item {
  margin-top: 24px;

  /deep/ .ivu-form-item-content {
    line-height: normal;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 2px solid #f0f3f7;

  /deep/ .ivu-btn {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 10px 24px;

    .ivu-icon {
      font-size: 18px;
    }
  }

  /deep/ .ivu-btn-primary {
    background: #3498db;
    border-color: #3498db;

    &:hover {
      background: #2980b9;
      border-color: #2980b9;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    }

    &:active {
      transform: translateY(0);
    }
  }

  /deep/ .ivu-btn-default {
    background: #f8f9fa;
    border-color: #e8ecef;
    color: #7f8c8d;

    &:hover {
      background: #ecf0f1;
      border-color: #d5dce0;
      color: #2c3e50;
      transform: translateY(-1px);
    }

    &:active {
      transform: translateY(0);
    }
  }

  /deep/ .ivu-btn-loading {
    &:hover {
      transform: none;
    }
  }
}
</style>
