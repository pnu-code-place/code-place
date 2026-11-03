<template>
  <div class="import-error-report">
    <el-alert
      type="error"
      show-icon
      :title="error.message"
      @close="$emit('close')"
    >
      <el-button type="text" size="mini" @click="visible = true"
        >자세히 보기</el-button
      >
    </el-alert>

    <el-dialog
      :title="error.message"
      :visible.sync="visible"
      width="720px"
      append-to-body
    >
      <p class="notice">
        오류가 있으면 zip 안의 어떤 문제도 저장되지 않습니다.
      </p>
      <div class="groups">
        <section v-for="group in groups" :key="group.dir" class="group">
          <h4 v-if="group.dir" class="group-title">
            {{ group.dir }}{{ group.title ? ` · ${group.title}` : "" }}
          </h4>
          <div v-for="(item, index) in group.errors" :key="index" class="error">
            <div class="error-message">
              <span v-if="meta(item)" class="error-meta">{{ meta(item) }}</span>
              {{ item.message }}
            </div>
            <pre
              v-if="item.detail"
              class="error-code"
              v-text="item.detail"
            ></pre>
          </div>
        </section>
      </div>
      <span slot="footer">
        <el-button size="small" @click="copy">복사</el-button>
        <el-button size="small" type="primary" @click="visible = false"
          >닫기</el-button
        >
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: "ImportErrorReport",
  props: {
    error: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      visible: false,
    }
  },
  computed: {
    groups() {
      const groups = []
      for (const item of this.error.errors) {
        let group = groups.find((group) => group.dir === item.dir)
        if (!group) {
          group = { dir: item.dir, title: item.title, errors: [] }
          groups.push(group)
        }
        group.title = group.title || item.title
        group.errors.push(item)
      }
      return groups
    },
  },
  methods: {
    meta(item) {
      if (!item.dir) return ""
      const line = item.line ? `${item.line}번째 줄` : ""
      return [item.location, item.field, line].filter(Boolean).join(" · ")
    },
    reportText() {
      const lines = [this.error.message]
      for (const group of this.groups) {
        if (group.dir) {
          lines.push("", `${group.dir} ${group.title || ""}`.trim())
        }
        for (const item of group.errors) {
          const meta = this.meta(item)
          lines.push(`- ${meta ? `${meta}: ` : ""}${item.message}`)
          if (item.detail) {
            lines.push(...item.detail.split("\n").map((line) => `    ${line}`))
          }
        }
      }
      return lines.join("\n")
    },
    copy() {
      const text = this.reportText()
      const done = () => this.$success("복사했습니다")
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard
          .writeText(text)
          .then(done)
          .catch(() => this.$error("복사에 실패했습니다"))
        return
      }
      const textarea = document.createElement("textarea")
      textarea.value = text
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand("copy")
      document.body.removeChild(textarea)
      done()
    },
  },
}
</script>

<style scoped lang="less">
.import-error-report {
  margin-top: 12px;
}
.notice {
  margin: 0 0 16px;
  color: #909399;
}
.groups {
  max-height: 60vh;
  overflow-y: auto;
}
.group + .group {
  margin-top: 20px;
}
.group-title {
  margin: 0 0 8px;
  font-size: 14px;
}
.error {
  padding: 6px 0;
}
.error-message {
  line-height: 1.6;
  word-break: break-all;
}
.error-meta {
  margin-right: 6px;
  color: #909399;
}
.error-code {
  margin: 6px 0 0;
  padding: 8px 12px;
  overflow-x: auto;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
}
</style>
