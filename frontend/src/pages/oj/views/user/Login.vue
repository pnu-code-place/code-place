<template>
  <div class="login-panel">
    <Form ref="formLogin" class="login-form" :model="formLogin" :rules="ruleLogin">
      <FormItem prop="username">
        <div class="login-email-field">
          <Input
            type="text"
            class="customLoginInput login-id-input"
            v-model="formLogin.username"
            placeholder="아이디"
            size="large"
            :autofocus="true"
            @on-enter="handleLogin"
          >
          </Input>
          <span class="login-email-domain">@pusan.ac.kr</span>
        </div>
      </FormItem>
      <FormItem prop="password">
        <Input
          type="password"
          class="customLoginInput"
          v-model="formLogin.password"
          :placeholder="$t('m.LoginPassword')"
          size="large"
          @on-enter="handleLogin"
        >
        </Input>
      </FormItem>
      <FormItem prop="tfa_code" v-if="tfaRequired">
        <Input v-model="formLogin.tfa_code" :placeholder="$t('m.TFA_Code')">
          <Icon type="ios-lightbulb-outline" slot="prepend"></Icon>
        </Input>
      </FormItem>
    </Form>
    <div class="footer-modal">
      <Button
        type="primary"
        @click="handleLogin"
        class="btn"
        long
        :loading="btnLoginLoading"
      >
        {{ $t("m.UserLogin") }}
      </Button>
      <div class="login-links">
        <a
          class="redirect"
          v-if="website.allow_register"
          @click.stop="handleBtnClick('register')"
          >{{ $t("m.No_Account") }}</a
        >
        <span v-if="website.allow_register" class="login-link-divider"></span>
        <a class="redirect" @click.stop="goResetPassword">{{
          $t("m.Forget_Password")
        }}</a>
      </div>
    </div>
  </div>
</template>

<script>
/*eslint-disable*/
import { mapGetters, mapActions } from "vuex"
import api from "@oj/api"
import { FormMixin } from "@oj/components/mixins"

export default {
  name: "OjLoginPage",
  mixins: [FormMixin],
  data() {
    const CheckRequiredTFA = (rule, value, callback) => {
      if (value !== "") {
        api.tfaRequiredCheck(this.normalizeLoginUsername(value)).then((res) => {
          this.tfaRequired = res.data.data.result
        })
      }
      callback()
    }

    return {
      tfaRequired: false,
      btnLoginLoading: false,
      formLogin: {
        username: "",
        password: "",
        tfa_code: "",
      },
      ruleLogin: {
        username: [
          { required: true, message: "아이디를 입력해주세요.", trigger: "blur" },
          { validator: CheckRequiredTFA, trigger: "blur" },
        ],
        password: [
          {
            required: true,
            message: "비밀번호를 입력해주세요.",
            trigger: "change",
            min: 6,
            max: 20,
          },
        ],
      },
    }
  },
  methods: {
    ...mapActions(["changeModalStatus", "getProfile"]),
    handleBtnClick(mode) {
      this.changeModalStatus({
        mode,
        visible: true,
      })
    },
    handleLogin() {
      this.$refs.formLogin.validate((valid) => {
        if (!valid) {
          this.$error("입력값을 확인해주세요.")
          return
        }
        this.btnLoginLoading = true
        let formData = Object.assign({}, this.formLogin)
        formData.username = this.normalizeLoginUsername(formData.username)
        if (!this.tfaRequired) {
          delete formData["tfa_code"]
        }
        api.login(formData).then(
          (res) => {
            this.btnLoginLoading = false
            this.changeModalStatus({ visible: false })
            this.getProfile()
            this.$success(this.$i18n.t("m.Welcome_back"))
          },
          (_) => {
            this.btnLoginLoading = false
          },
        )
      })
    },
    goResetPassword() {
      this.changeModalStatus({ visible: false })
      this.$router.push({ name: "apply-reset-password" })
    },
    normalizeLoginUsername(username) {
      const value = (username || "").trim()
      if (!value) {
        return value
      }
      const loginId = value.split("@")[0].trim()
      return `${loginId}@pusan.ac.kr`
    },
  },
  computed: {
    ...mapGetters(["website", "modalStatus"]),
    visible: {
      get() {
        return this.modalStatus.visible
      },
      set(value) {
        this.changeModalStatus({ visible: value })
      },
    },
  },
}
</script>

<style scoped lang="less">
.login-panel {
  width: 100%;
}

.footer-modal {
  overflow: visible;
  margin-top: 20px;
  margin-bottom: -15px;
  text-align: center;
  .btn {
    margin: 0;
    &:last-child {
      margin: 0;
    }
  }
}
.btn {
  height: 45px;
  border: none;
  background-color: #5b64ed;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(74, 83, 212, 0.12);
  transition: background-color 0.18s ease, box-shadow 0.18s ease,
    transform 0.18s ease;

  &:hover,
  &:focus {
    border: none;
    background-color: #6971ff;
    color: #fff;
    box-shadow: 0 5px 12px rgba(91, 100, 237, 0.16);
  }

  &:active {
    background-color: #5159df;
    color: #fff;
    box-shadow: 0 3px 8px rgba(74, 83, 212, 0.12);
    transform: translateY(1px);
  }
}
.customLoginInput {
  //outline: 2px solid #255aa4 !important;
}
.login-form {
  @login-input-height: 44px;

  /deep/ .ivu-form-item {
    margin-bottom: 16px;
  }

  /deep/ .ivu-form-item-error {
    margin-bottom: 26px;
  }

  /deep/ .ivu-form-item-error-tip {
    padding-top: 4px;
    color: #e23b2e;
    font-size: 12px;
    line-height: 16px;
  }

  /deep/ .ivu-input {
    height: @login-input-height;
    border-color: #d8dbe4;
    border-radius: 8px;
    color: #31364a;
    font-size: 14px;
    font-weight: 500;
    padding-left: 14px;
    padding-right: 14px;
  }

  /deep/ .ivu-input::placeholder {
    color: #9aa0ad;
    font-weight: 500;
  }

  /deep/ .ivu-input:focus {
    border-color: #6b72ee;
    box-shadow: 0 0 0 2px rgba(91, 100, 237, 0.1);
  }
}
.login-email-field {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  column-gap: 10px;
  width: 100%;
  align-items: stretch;
}
.login-id-input {
  min-width: 0;

  /deep/ .ivu-input-wrapper {
    width: 100%;
  }

  /deep/ .ivu-input {
    height: 44px;
    border: 1px solid #d8dbe4;
    border-radius: 8px;
    background: #fff;
    padding-right: 12px;
  }

  /deep/ .ivu-input:focus {
    border-color: #6b72ee;
    box-shadow: 0 0 0 2px rgba(91, 100, 237, 0.1);
  }
}
.login-email-domain {
  min-width: 132px;
  height: 44px;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d8dbe4;
  border-radius: 8px;
  color: #565d70;
  background: #fafbfe;
  font-size: 14px;
  font-weight: 500;
  line-height: 1;
  padding: 0 12px;
  white-space: nowrap;
  pointer-events: none;
}
.login-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 18px;
}

.login-link-divider {
  display: inline-block;
  width: 1px;
  height: 18px;
  background-color: #d7dbe5;
}

.redirect {
  color: #565d70;
  float: none;
  margin-right: 0;
  font-size: 13px;
  font-weight: 500;
  line-height: 1;
  cursor: pointer;

  &:hover {
    color: #5b64ed;
  }
}

@media screen and (max-width: 640px) {
  .footer-modal {
    margin-top: 20px;
  }

  .btn {
    height: 45px;
    font-size: 14px;
  }

  .login-form {
    /deep/ .ivu-form-item {
      margin-bottom: 16px;
    }

    /deep/ .ivu-form-item-error {
      margin-bottom: 26px;
    }

    /deep/ .ivu-input {
      height: 42px;
      font-size: 14px;
    }
  }

  .login-email-field {
    grid-template-columns: minmax(0, 1fr) auto;
    column-gap: 8px;
  }

  .login-email-domain {
    height: 42px;
    font-size: 13px;
    min-width: 118px;
    padding: 0 10px;
  }

  .login-links {
    gap: 16px;
    margin-top: 22px;
  }

  .redirect {
    font-size: 13px;
  }

}
</style>
