<script>
export default {
  name: 'ErrorSign',
  data() {
    return {
      errorStatus: {
        code: 0,
        description: '',
        solution: ''
      },
      errorInfo: {
        404: {
          code: '404',
          description: this.$t('m.No_Response'),
          solution: this.$t('m.Reload_Page')
        },
        500: {
          code: '500',
          description: this.$t('m.Server_Error'),
          solution: this.$t('m.Try_Again_Later')
        },
        504: {
          code: '504',
          description: this.$t('m.Gateway_Timeout'),
          solution: this.$t('m.Try_Again_Later')
        }
      }
    }
  },
  props: {
    code: {
      type: Number,
      default: 404
    },
    description: {
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
        if (this.description) {
          this.errorStatus.description = this.description;
        } else {
          this.errorStatus.description = this.errorInfo[this.code].description;
        }
        if (this.solution) {
          this.errorStatus.solution = this.solution;
        } else {
          this.errorStatus.solution = this.errorInfo[this.code].solution;
        }
      } else {
        this.errorStatus.code = this.code;
        this.errorStatus.description = this.description;
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
    <p class="error-message">{{ this.errorStatus.description }}</p>
    <p class="error-solution">{{ this.errorStatus.solution }}</p>
  </div>
</template>

<style scoped lang="less">
.error-sign {
  padding: 2rem 2rem 4rem;
  text-align: center;
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
