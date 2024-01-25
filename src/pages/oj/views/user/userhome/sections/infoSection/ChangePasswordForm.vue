<template>
  <Form class="setting-content" ref="formPassword" :model="formPassword" :rules="rulePassword">
    <div class="inputName">
      {{ $t('m.Current_Password') }}
    </div>
    <FormItem prop="old_password">
      <Input v-model="formPassword.old_password" type="password"/>
    </FormItem>
    <div class="inputName">
      {{ $t('m.New_Password') }}
    </div>
    <FormItem prop="new_password">
      <Input v-model="formPassword.new_password" type="password"/>
    </FormItem>
    <div class="inputName">
      {{ $t('m.Confirm_Password') }}
    </div>
    <FormItem prop="again_password">
      <Input v-model="formPassword.again_password" type="password"/>
    </FormItem>
    <FormItem v-if="visible.tfaRequired" label="Two Factor Auth" prop="tfa_code">
      <Input v-model="formPassword.tfa_code"/>
    </FormItem>
    <FormItem v-if="visible.passwordAlert">
      <Alert type="success">잠시 후 로그인해 주세요</Alert>
    </FormItem>
    <Button type="primary" @click="changePassword">{{ $t('m.Update_Password') }}</Button>
  </Form>
</template>

<script>
import api from '@oj/api'
import {FormMixin} from '@oj/components/mixins'

export default {
  mixins: [FormMixin],
  data() {
    const oldPasswordCheck = [{required: true, trigger: 'blur', min: 6, max: 20}]
    const tfaCheck = [{required: true, trigger: 'change'}]
    const CheckAgainPassword = (rule, value, callback) => {
      if (value !== this.formPassword.new_password) {
        callback(new Error('password does not match'))
      }
      callback()
    }
    const CheckNewPassword = (rule, value, callback) => {
      if (this.formPassword.old_password !== '') {
        if (this.formPassword.old_password === this.formPassword.new_password) {
          callback(new Error('The new password doesn\'t change'))
        } else {
          // 对第二个密码框再次验证
          this.$refs.formPassword.validateField('again_password')
        }
      }
      callback()
    }
    return {
      loading: {
        btnPassword: false,
        btnEmail: false
      },
      visible: {
        passwordAlert: false,
        emailAlert: false,
        tfaRequired: false
      },
      formPassword: {
        tfa_code: '',
        old_password: '',
        new_password: '',
        again_password: ''
      },
      formEmail: {
        tfa_code: '',
        password: '',
        old_email: '',
        new_email: ''
      },
      rulePassword: {
        old_password: oldPasswordCheck,
        new_password: [
          {required: true, trigger: 'blur', min: 6, max: 20},
          {validator: CheckNewPassword, trigger: 'blur'}
        ],
        again_password: [
          {required: true, validator: CheckAgainPassword, trigger: 'change'}
        ],
        tfa_code: tfaCheck
      },
      ruleEmail: {
        password: oldPasswordCheck,
        new_email: [{required: true, type: 'email', trigger: 'change'}],
        tfa_code: tfaCheck
      }
    }
  },
  mounted() {
    this.formEmail.old_email = this.$store.getters.user.email || ''
  },
  methods: {
    changePassword() {
      this.validateForm('formPassword').then(valid => {
        this.loading.btnPassword = true
        let data = Object.assign({}, this.formPassword)
        delete data.again_password
        if (!this.visible.tfaRequired) {
          delete data.tfa_code
        }
        api.changePassword(data).then(res => {
          this.loading.btnPassword = false
          this.visible.passwordAlert = true
          this.$success('Update password successfully')
          setTimeout(() => {
            this.visible.passwordAlert = false
            this.$router.push({name: 'logout'})
          }, 5000)
        }, res => {
          if (res.data.data === 'tfa_required') {
            this.visible.tfaRequired = true
          }
          this.loading.btnPassword = false
        })
      })
    },
    changeEmail() {
      this.validateForm('formEmail').then(valid => {
        this.loading.btnEmail = true
        let data = Object.assign({}, this.formEmail)
        if (!this.visible.tfaRequired) {
          delete data.tfa_code
        }
        api.changeEmail(data).then(res => {
          this.loading.btnEmail = false
          this.visible.emailAlert = true
          this.$success('Change email successfully')
          this.$refs.formEmail.resetFields()
        }, res => {
          if (res.data.data === 'tfa_required') {
            this.visible.tfaRequired = true
          }
        })
      })
    }
  }
}
</script>

<style lang="less" scoped>
section {
  border: 1px solid #dedede;
  border-radius: 7px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 20px;

  h1 {
    text-align: left;
    margin-bottom: 10px;
  }

  h2 {
    text-align: left;
    margin-bottom: 10px;
  }
}

#captcha {
  display: flex;
  flex-wrap: nowrap;
  justify-content: space-between;
  width: 100%;
  height: 36px;

  #captchaCode {
    flex: auto;
  }

  #captchaImg {
    margin-left: 10px;
    padding: 3px;
    flex: initial;
  }
}

.btn {
  margin-top: 18px;
  text-align: center;
}

.inputName {
  font-size: small;
  font-weight: 800;
  margin-bottom: 5px;
  margin-left: 1px;
  text-align: left;
}
</style>
