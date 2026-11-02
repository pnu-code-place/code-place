<template>
  <textarea ref="editor"></textarea>
</template>

<script>
import Simditor from "tar-simditor"
import "tar-simditor/styles/simditor.css"
import "tar-simditor-markdown"
import "tar-simditor-markdown/styles/simditor-markdown.css"
import "./simditor-file-upload"

export default {
  name: "AdminSimditor",
  props: {
    toolbar: {
      type: Array,
      default: () => [
        "title",
        "bold",
        "italic",
        "underline",
        "fontScale",
        "color",
        "ol",
        "ul",
        "|",
        "blockquote",
        "code",
        "link",
        "table",
        "image",
        "uploadfile",
        "hr",
        "|",
        "indent",
        "outdent",
        "alignment",
        "|",
        "markdown",
      ],
    },
    value: {
      type: String,
      default: "",
    },
    deferUpload: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      editor: null,
      currentValue: this.value,
      pendingImages: {},
    }
  },
  mounted() {
    Simditor.locale = "en-US" // 한국어는 지원하지 않으므로 영어로 설정합니다.

    this.editor = new Simditor({
      textarea: this.$refs.editor,
      toolbar: this.toolbar,
      pasteImage: true,
      markdown: false,
      upload: {
        url: "/api/admin/upload_image/",
        params: null,
        fileKey: "image",
        connectionCount: 3,
        leaveConfirm: this.$i18n.t("m.Uploading_is_in_progress"),
      },
      allowedStyles: {
        // span: ['color']
      },
    })
    if (this.deferUpload) {
      const uploader = this.editor.uploader
      uploader._xhrUpload = (file) => {
        const blobUrl = URL.createObjectURL(file.obj)
        this.pendingImages[blobUrl] = file.obj
        setTimeout(() => {
          uploader.trigger("uploadprogress", [file, file.size, file.size])
          uploader.trigger("uploadsuccess", [
            file,
            { success: true, file_path: blobUrl },
          ])
          uploader.trigger("uploadcomplete", [file, ""])
        })
      }
    }
    this.editor.on("valuechanged", (e, src) => {
      this.currentValue = this.editor.getValue()
    })
    this.editor.on("decorate", (e, src) => {
      this.currentValue = this.editor.getValue()
    })

    this.editor.setValue(this.value)
  },
  watch: {
    value(val) {
      if (this.currentValue !== val) {
        this.currentValue = val
        this.editor.setValue(val)
      }
    },
    currentValue(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.$emit("change", newVal)
        this.$emit("input", newVal)
      }
    },
  },
  methods: {
    async uploadPendingImages() {
      let html = this.editor.getValue()
      for (const [blobUrl, file] of Object.entries(this.pendingImages)) {
        if (!html.includes(blobUrl)) continue
        const form = new FormData()
        form.append("image", file)
        const res = await fetch("/api/admin/upload_image/", {
          method: "POST",
          body: form,
          credentials: "same-origin",
        })
        const data = await res.json()
        if (!data.success) throw new Error(data.msg)
        html = html.split(blobUrl).join(data.file_path)
      }
      this.revokeAll()
      this.editor.setValue(html)
      this.currentValue = html
      return html
    },
    revokeAll() {
      Object.keys(this.pendingImages).forEach(URL.revokeObjectURL)
      this.pendingImages = {}
    },
  },
  beforeDestroy() {
    this.revokeAll()
  },
}
</script>

<style lang="less" scoped></style>
