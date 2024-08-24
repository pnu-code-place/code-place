<script>
export default {
  name: 'LanguageIcon',
  data() {
    return {}
  },
  props: {
    language: {
      type: String,
      default: 'language'
    },
    image: {
      type: String,
      default: 'image'
    },
    description: {
      type: String,
      default: 'description'
    },
    lecture: {
      type: Array,
      default: () => []
    },
    openIndex: {
      type: Number,
      default: -1
    },
    index: {
      type: Number,
      default: 0
    },
    extended: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    openDetail() {
      this.$emit('extend', this.index)
    }
  },
  computed: {
    selected() {
      return this.openIndex === this.index
    },
    selectedClass() {
      return this.selected ? 'selected' : ''
    },
    extendedClass() {
      return this.extended ? 'extended' : ''
    }
  }
}

// TODO : 애니메이션 기획 및 구현
</script>
<template>
  <div :class="`language-info ${selectedClass}`" @mouseenter="openDetail">
    <img :src="image" alt="language" :class="extendedClass"/>
  </div>
</template>

<style scoped lang="less">


.language-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  img {
    cursor: pointer;
    transform: translateY(10%);
    width: 35px;
    object-fit: cover;
    transition: all 0.5s ease-in-out;

    &.extended {
      width: 80px;
    }
  }

  &.selected {
    img {
      animation: hover 1.6s infinite;
      filter: drop-shadow(0 2px 2px rgba(0, 0, 0, 0.25));
    }
  }
}


@keyframes hover {
  0% {
    transform: translateY(7%)
  }
  50% {
    transform: translateY(-7%)
  }
  100% {
    transform: translateY(7%)
  }
}
</style>
