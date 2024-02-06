<script>
import ShineWrapper from "../../../../../components/ShineWrapper.vue";

export default {
  components: {ShineWrapper},
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    },
    image: {
      type: String,
      required: true
    },
    date: {
      type: String,
      required: true
    },
    disabled: {
      type: Boolean,
      default() {
        return false
      }
    }
  },
  data() {
    return {
      displayImage: this.image
    }
  },
  computed: {
    fallbackMedal() {
      return require("@/assets/challenges/errorMedal.png")
    }
  },
  methods: {
    onMedalError(e) {
      e.target.src = this.fallbackMedal;
    }
  }
}
</script>

<template>
  <Tooltip placement="bottom" class="tooltip" :disabled="this.disabled">
    <shine-wrapper class="image">
      <img :src="image" alt="badge" @error="onMedalError"/>
    </shine-wrapper>
    <template #content>
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
      <div>{{$t('m.Date')}} : {{ date }}</div>
    </template>
  </Tooltip>
</template>

<style scoped lang="less">
.tooltip {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;

  h3 {
    text-align: center;
  }

  p {
    text-align: center;
  }

  div {
    text-align: center;
  }
}

img {
  width: 100%;
  height: auto;
}

.image:hover {
  transform: scale(1.1);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
</style>
