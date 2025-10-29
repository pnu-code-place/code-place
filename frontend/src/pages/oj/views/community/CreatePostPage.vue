<template>
  <div class="container">
    <Card :padding="20" dis-hover>
      <div class="header">
        <h1 class="title">{{ $t("m.Community_Create_Post") }}</h1>
      </div>
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
          <Input v-model="post.content" type="textarea" :autosize="{ minRows: 10, maxRows: 20 }"
            :placeholder="$t('m.Community_Content_Placeholder')" />
          <!--
            TODO: Simditor나 다른 WYSIWYG 에디터 컴포넌트로 교체하기
          -->
        </FormItem>
        <div class="form-actions">
          <Button type="primary" @click.prevent="submitPost" :loading="loading">
            {{ $t("m.Submit") }}
          </Button>
          <Button @click="$router.go(-1)" style="margin-left: 8px">{{
            $t("m.Cancel")
            }}</Button>
        </div>
      </Form>
    </Card>
  </div>
</template>

<script>
import api from "@oj/api";
import { POST_TYPE } from "@/utils/constants";
import { mapGetters } from "vuex";

export default {
  name: "CreatePostPage",
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
.container {
  width: var(--global-width);
  margin: 20px auto;
}

.header {
  margin-bottom: 20px;
}

.title {
  font-size: 24px;
  font-weight: 600;
}

.content-form-item {
  margin-top: 20px;
}

.form-actions {
  text-align: right;
  margin-top: 20px;
}
</style>
