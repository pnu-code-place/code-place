<template>
  <textarea ref="editor"></textarea>
</template>

<script>
import Simditor from "tar-simditor"
import "tar-simditor/styles/simditor.css"
import "tar-simditor-markdown"
import "tar-simditor-markdown/styles/simditor-markdown.css"
import "./simditor-file-upload"

const IMAGE_SUFFIXES = ["gif", "jpg", "jpeg", "bmp", "png"]
const MAX_IMAGE_SIZE = 200 * 1024 * 1024

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
  },
  data() {
    return {
      editor: null,
      currentValue: this.value,
      pendingImages: {},
      uploadedPaths: {},
      uploadingPromise: null,
    }
  },
  mounted() {
    Simditor.locale = "en-US" // 한국어는 지원하지 않으므로 영어로 설정합니다.

    this.editor = new Simditor({
      textarea: this.$refs.editor,
      toolbar: this.toolbar,
      pasteImage: true,
      markdown: false,
      codeLanguages: [
        { name: "C", value: "c" },
        { name: "C++", value: "cpp" },
        { name: "Golang", value: "go" },
        { name: "Java", value: "java" },
        { name: "JavaScript", value: "javascript" },
        { name: "Python3", value: "python" },
      ],
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
    const uploader = this.editor.uploader
    uploader._xhrUpload = (file) => {
      const suffix = (file.name || "").split(".").pop().toLowerCase()
      const error = !IMAGE_SUFFIXES.includes(suffix)
        ? "지원하지 않는 이미지 형식입니다 (gif, jpg, jpeg, bmp, png)"
        : file.size >= MAX_IMAGE_SIZE
          ? "이미지 용량은 200MB 미만이어야 합니다"
          : null
      if (error) {
        setTimeout(() => {
          uploader.trigger("uploaderror", [
            file,
            { statusText: "error", responseText: "" },
          ])
          if (file.img) {
            const mask = file.img.data("mask")
            if (mask) mask.remove()
            file.img.removeClass("uploading loading").remove()
            this.editor.trigger("valuechanged")
          }
          uploader.trigger("uploadcomplete", [file, ""])
          this.$error(`${file.name || "이미지"}: ${error}`)
        })
        return
      }
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
    async uploadImage(file) {
      try {
        const form = new FormData()
        form.append("image", file)
        let res
        try {
          res = await fetch("/api/admin/upload_image/", {
            method: "POST",
            body: form,
            credentials: "same-origin",
          })
        } catch (e) {
          throw new Error("서버에 연결하지 못했습니다", { cause: e })
        }
        if (!res.ok) {
          throw new Error(
            res.status === 413
              ? "이미지 용량이 너무 큽니다"
              : `이미지 업로드 서버 오류 (${res.status})`,
          )
        }
        let data
        try {
          data = await res.json()
        } catch (e) {
          throw new Error("서버에서 올바르지 않은 응답을 받았습니다", {
            cause: e,
          })
        }
        if (!data || !data.success || !data.file_path) {
          throw new Error(
            (data && data.msg) || "이미지를 업로드하지 못했습니다",
          )
        }
        return data.file_path
      } catch (e) {
        throw new Error(`${file.name || "이미지"}: ${e.message}`, { cause: e })
      }
    },
    uploadPendingImages() {
      if (!this.uploadingPromise) {
        this.uploadingPromise = this.uploadImagesInBody().finally(() => {
          this.uploadingPromise = null
        })
      }
      return this.uploadingPromise
    },
    async uploadImagesInBody() {
      const done = new Set()
      let blobUrls
      while (
        (blobUrls = Object.keys(this.pendingImages).filter(
          (url) => !done.has(url) && this.editor.getValue().includes(url),
        )).length
      ) {
        for (const blobUrl of blobUrls) {
          if (!this.uploadedPaths[blobUrl]) {
            this.uploadedPaths[blobUrl] = await this.uploadImage(
              this.pendingImages[blobUrl],
            )
          }
          this.editor.body
            .find("img")
            .filter((_, img) => img.getAttribute("src") === blobUrl)
            .attr("src", this.uploadedPaths[blobUrl])
          done.add(blobUrl)
          this.currentValue = this.editor.getValue()
        }
      }
      return this.editor.getValue()
    },
    revokeAll() {
      Object.keys(this.pendingImages).forEach(URL.revokeObjectURL)
      this.pendingImages = {}
      this.uploadedPaths = {}
    },
  },
  beforeDestroy() {
    this.revokeAll()
  },
}
</script>

<style lang="less" scoped></style>

<style lang="less">
.simditor .simditor-body img {
  max-width: calc(100% - 10px);
  height: auto;
}
</style>
