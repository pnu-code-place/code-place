<template>
  <div class="submissionBtnWrapper" @click="onClick">
    <svg class="icon" viewBox="0 0 24 24">
      <path
        d="m20 24h-16c-.553 0-1-.447-1-1 0-3.309 2.691-6 6-6h6c3.309 0 6 2.691 6 6 0 .553-.447 1-1 1zm-10.013-14.6h1.067l-.519-2.494zm10.513-3.4h-.551c-.252-2.244-2.139-4-4.449-4h-2.5v-1c0-.552-.447-1-1-1s-1 .448-1 1v1h-2.5c-2.31 0-4.197 1.756-4.449 4h-.551c-.827 0-1.5.673-1.5 1.5v2c0 .827.673 1.5 1.5 1.5h.551c.252 2.244 2.139 4 4.449 4h7c2.31 0 4.197-1.756 4.449-4h.551c.827 0 1.5-.673 1.5-1.5v-2c0-.827-.673-1.5-1.5-1.5zm-8.227 6c-.385.017-.73-.246-.808-.625l-.078-.375h-1.751l-.084.383c-.079.36-.398.617-.767.617-.499 0-.872-.46-.768-.948l.993-4.668c.146-.755.76-1.383 1.523-1.383h.002c.782.004 1.368.603 1.534 1.423l.973 4.63c.102.488-.27.946-.768.946zm3.727-.8c0 .442-.358.8-.8.8s-.8-.358-.8-.8v-5.399c0-.442.358-.8.8-.8s.8.358.8.8z"
      />
    </svg>
    <span>AI조교</span>
  </div>
</template>

<script>
import { defineComponent } from "vue"

export default defineComponent({
  emits: ["open-ai"],
  methods: {
    onClick() {
      this.$emit("open-ai")
    },
  },
})
</script>

<style scoped lang="less">
.submissionBtnWrapper {
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  border-radius: 10px;
  padding: 6px 12px;
  cursor: pointer;
  transition: width 0.3s;
  background-color: #f0f1ff;
  color: #000478;
  i {
    font-size: smaller;
  }
}

.submissionBtnWrapper:hover {
  background-color: #000478;
  color: #f0f1ff;
}

.submissionBtnWrapper:hover .icon {
  fill: #f0f1ff;
}

.icon {
  width: 18px;
  height: 18px;
  margin-right: 6px;
  fill: #000478;
}
</style>
