<script>
export default {
  name: 'ErrorSign',
  data() {
    return {
      errorStatus: {
        code: 0,
        message: '',
        solution: ''
      },
      errorInfo: {
        404: {
          code: '404',
          description: '서버가 응답하지 않습니다.',
          solution: '현재 페이지를 다시 로드하거나, 나중에 다시 시도해 주세요.'
        },
        500: {
          code: '500',
          description: '서버가 응답하지 않습니다.',
          solution: '잠시 후 다시 시도해 주세요.'
        },
        504: {
          code: '504',
          description: '서버가 응답하지 않습니다.',
          solution: '잠시 후 다시 시도해 주세요.'
        }
      }
    }
  },
  props: {
    code: {
      type: Number,
      default: 404
    },
    message: {
      type: String,
      default: ''
    },
    solution: {
      type: String,
      default: ''
    }
  },
  methods: {
    init() {
      if (Object.keys(this.errorInfo).includes(this.code.toString())) {
        this.errorStatus.code = this.code;
        if (this.message) {
          this.errorStatus.message = this.message;
        } else {
          this.errorStatus.message = this.errorInfo[this.code].description;
        }
        if (this.solution) {
          this.errorStatus.solution = this.solution;
        } else {
          this.errorStatus.solution = this.errorInfo[this.code].solution;
        }
      } else {
        this.errorStatus.code = this.code;
        this.errorStatus.message = this.message;
        this.errorStatus.solution = this.solution;
      }
    }
  },
  mounted() {
    this.init();
  },
}
</script>

<template>
  <div class="error-sign">
    <h1>{{ this.errorStatus.code }}</h1>
    <p class="error-message">{{ this.errorStatus.message }}</p>
    <p class="error-solution">{{ this.errorStatus.solution }}</p>
  </div>
</template>

<style scoped lang="less">
.error-sign {
  padding: 2rem 2rem 4rem;
}

h1 {
  font-size: 4rem;
  font-weight: 700;
}

.error-message {
  font-size: 1.5rem;
  color: #666;
}

.error-solution {
  font-size: 1.2rem;
  color: #999;
}
</style>
