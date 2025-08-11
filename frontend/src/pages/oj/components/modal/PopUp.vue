<script>
export default {
  name: "pop-up",
  mounted() {
    this.position.x = this.$props.p_position.x
    this.position.y = this.$props.p_position.y
    window.addEventListener("mouseup", this.stopDrag)
  },
  props: {
    width: 0,
    p_position: {
      type: Object,
      default: {
        x: 100,
        y: 100,
      },
    },
    link: "",
    id: 0,
    isTopPopup: false,
  },
  data() {
    return {
      isFixed: false,
      isShow: true,
      position: {
        x: 0,
        y: 0,
      },
      offset: {
        x: 0,
        y: 0,
      },
      isDragging: false,
    }
  },
  computed: {
    popupClass() {
      return `pop-up ${this.isDragging ? "grab" : ""}`
    },
    popupStyle() {
      const width = this.$props.width === 0 ? "auto" : this.$props.width + "px"
      return {
        left: this.position.x + "px",
        top: this.position.y + "px",
        width: width,
        zIndex: this.isTopPopup ? 11 : 10,
      }
    },
    popupBodyClass() {
      return `pop-up__body ${this.isDragging ? "grab" : "pointer"}`
    },
  },
  methods: {
    closeForDayHandler() {
      this.$store.commit("removePopup", this.$props.id)
      this.closeHandler()
    },
    closeHandler() {
      this.isShow = false
    },
    startDrag(event) {
      this.$emit("selected", this.id)
      this.offset.x = event.clientX - this.position.x
      this.offset.y = event.clientY - this.position.y

      window.addEventListener("mousemove", this.drag)
      window.addEventListener("mouseup", this.stopDrag)
    },
    drag(event) {
      this.isDragging = true
      if (this.isDragging) {
        this.position.x = event.clientX - this.offset.x
        this.position.y = event.clientY - this.offset.y
      }
    },
    stopDrag() {
      setTimeout(() => {
        this.isDragging = false
      }, 10)
      window.removeEventListener("mousemove", this.drag)
      window.removeEventListener("mouseup", this.stopDrag)
    },
    goLink() {
      if (this.link !== "" && !this.isDragging) {
        window.open(this.link)
      }
    },
  },
}
</script>

<template>
  <div
    @mousedown="startDrag"
    :class="this.popupClass"
    :style="this.popupStyle"
    v-if="this.isShow"
  >
    <div :class="popupBodyClass" @click="goLink">
      <slot></slot>
    </div>
    <div class="pop-up__footer">
      <button class="close-button" @click="closeHandler">창 닫기 ×</button>
      <button class="close-button hide-for-day" @click="closeForDayHandler">
        더 이상 보지 않기
      </button>
    </div>
  </div>
</template>

<style scoped lang="less">
.pop-up {
  position: absolute;
  top: 100px;
  background-color: white;
  display: flex;
  flex-direction: column;
  border-radius: 15px;
  overflow: hidden;

  box-shadow:
    0 4px 8px 0 rgba(0, 0, 0, 0.2),
    0 6px 20px 0 rgba(0, 0, 0, 0.19);

  .pop-up__footer {
    color: var(--pale-point-color);
    font-size: 0.8rem;
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 0 10px 10px;
    border-top: 1px solid var(--pale-point-color);

    .close-button {
      padding: 0.2rem;
      cursor: pointer;
      background: none;
      border: none;
      color: var(--container-font-color);
      font-weight: bold;
      white-space: nowrap;
    }

    .hide-for-day {
      text-decoration: underline;
    }
  }

  img {
    object-fit: contain;
  }
}

.grab {
  cursor: grabbing;
}

.pointer {
  cursor: pointer;
}
</style>
