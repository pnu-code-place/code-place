<script>

export default {
  name: "pop-up",
  mounted() {
    this.position.x = this.$props.p_position.x
    this.position.y = this.$props.p_position.y
    window.addEventListener('mouseup', this.stopDrag)
  },
  props: {
    width: 0,
    p_position: {
      type: Object,
      default: {
        x: 100,
        y: 100
      }
    },
    link: '',
    id: 0
  },
  data() {
    return {
      isFixed: false,
      isShow: true,
      position: {
        x: 0,
        y: 0
      },
      offset: {
        x: 0,
        y: 0
      },
      isDragging: false
    }
  },
  computed: {
    popupClass() {
      return `pop-up ${this.isDragging ? 'grab' : ''}`;
    },
    popupStyle() {
      const width = this.$props.width === 0 ? "auto" : this.$props.width + "px"
      return {
        left: this.position.x + 'px',
        top: this.position.y + 'px',
        width: width
      }
    },
    popupBodyClass() {
      return `pop-up__body ${this.isDragging ? 'grab' : 'pointer'}`
    },

  },
  methods: {
    closeForDayHandler() {
      this.$store.commit('removePopup', this.$props.id)
      this.closeHandler()
    },
    closeHandler() {
      this.isShow = false;
    },
    startDrag(event) {
      this.offset.x = event.clientX - this.position.x;
      this.offset.y = event.clientY - this.position.y;

      window.addEventListener('mousemove', this.drag);
      window.addEventListener('mouseup', this.stopDrag);
    },
    drag(event) {
      this.isDragging = true;
      if (this.isDragging) {
        this.position.x = event.clientX - this.offset.x;
        this.position.y = event.clientY - this.offset.y;
      }
    },
    stopDrag() {
      setTimeout(() => {
        this.isDragging = false;
      }, 10)
      window.removeEventListener('mousemove', this.drag);
      window.removeEventListener('mouseup', this.stopDrag);
    },
    goLink() {
      if (this.link !== '' && !this.isDragging) {
        console.log(!this.isDragging)
        window.open(this.link)
      }
    }
  }
}
</script>

<template>
  <div @mousedown="startDrag" :class="this.popupClass" :style="this.popupStyle" v-if="this.isShow">
    <div :class="popupBodyClass" @click="goLink">
      <slot></slot>
    </div>
    <div class="pop-up__footer">
      <button class="close-button" @click="closeHandler">
        창 닫기 ×
      </button>
      <button class="close-button hide-for-day" @click="closeForDayHandler">
        오늘 하루 보지 않기
      </button>
    </div>
  </div>
</template>

<style scoped lang="less">
.pop-up {
  position: absolute;
  top: 100px;
  background-color: white;
  border: 1px solid var(--point-color);
  z-index: 10;
  display: flex;
  flex-direction: column;

  .pop-up__footer {
    color: var(--pale-point-color);
    font-size: 1rem;
    width: 100%;
    background-color: #736d6d;
    display: flex;
    justify-content: space-between;

    .close-button {
      padding: 0.4rem;
      cursor: pointer;
      background: none;
      border: none;
      color: var(--pale-point-color);
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
