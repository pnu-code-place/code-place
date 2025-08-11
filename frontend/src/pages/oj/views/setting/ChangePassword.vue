<script>
import api from "@oj/api"

export default {
  name: "PasswordReset",
  data() {
    return {
      formResetPassword: {
        old_password: "",
        new_password: "",
        newPasswordAgain: "",
        token: "",
      },
      formError: {
        old_password: "",
        new_password: "",
        newPasswordAgain: "",
      },
      pwReq: {
        maxLength: 20,
        minLength: 8,
        regex: /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,20}$/,
      },
      btnLoading: false,
      resetSuccess: false,
      logoutTrigger: false,
    }
  },
  mounted() {
    this.formResetPassword.token = this.$route.params.token
  },
  methods: {
    clearErrorSign(input) {
      this.formError[input] = ""
    },
    handleResetPassword(e) {
      e.preventDefault()
      this.changePassword()
    },
    validatePassword(password) {
      if (
        password.length < this.pwReq.minLength ||
        password.length > this.pwReq.maxLength
      ) {
        return false
      }
      return this.pwReq.regex.test(password)
    },
    validateForm() {
      if (this.formResetPassword.old_password === "") {
        this.formError.old_password = this.$t("m.Please_Input_Current_Password")
        return false
      }
      if (this.formResetPassword.new_password === "") {
        this.formError.new_password = this.$t("m.Please_Input_New_Password")
        return false
      }
      if (this.formResetPassword.newPasswordAgain === "") {
        this.formError.newPasswordAgain = this.$t(
          "m.Please_Input_New_Password_Again",
        )
        return false
      }
      if (
        this.formResetPassword.new_password !==
        this.formResetPassword.newPasswordAgain
      ) {
        this.formError.newPasswordAgain = this.$t("m.password_does_not_match")
        return false
      }
      if (
        this.formResetPassword.new_password ===
        this.formResetPassword.old_password
      ) {
        this.formError.new_password = this.$t(
          "m.New_Password_Cannot_Be_The_Same_As_The_Current_Password",
        )
        return false
      }
      if (!this.validatePassword(this.formResetPassword.new_password)) {
        this.formError.new_password = this.$t("m.Invalid_Password_Format")
        return false
      }
      return true
    },
    changePassword() {
      if (this.validateForm()) {
        this.btnLoading = true
        api.changePassword(this.formResetPassword).then(
          (res) => {
            this.btnLoading = false
            this.resetSuccess = true
            this.$success(this.$t("m.Change_Password_Success"))
            setTimeout(() => {
              this.$router.push({ name: "logout" })
            }, 5000)
          },
          (res) => {
            this.btnLoading = false
            this.$error(res.data.data)
          },
        )
      }
    },
  },
  computed: {
    submitClass() {
      if (this.btnLoading) {
        return "button-loading"
      } else {
        return "submit-button"
      }
    },
    submitText() {
      if (this.btnLoading) {
        return this.$t("m.Submitting")
      }
      return this.$t("m.Submit_Password")
    },
    willLogout() {
      return this.$t("m.You_Will_Be_Logged_Out_In_5_Seconds")
    },
  },
}
</script>

<template>
  <div class="change-password">
    {{ this.formResetPassword.token }}
    <h1>
      {{ $t("m.ChangePassword") }}
    </h1>
    <form class="change-password-form">
      <div>
        <label class="label" for="current-password">
          {{ $t("m.Current_Password") }}
        </label>
        <input
          type="password"
          id="current-password"
          v-model="formResetPassword.old_password"
          @focusout="clearErrorSign('currentPassword')"
        />
        <span class="form-error">{{ this.formError.old_password }}</span>
      </div>
      <div>
        <div class="input-header">
          <label class="label" for="new-password">{{
            $t("m.New_Password")
          }}</label>
          <div>
            <Icon type="ios-information" size="13" color="#7a7a7a"></Icon>
            <span
              >8글자 이상, 영문, 숫자, 특수문자를 모두 사용해야 합니다.</span
            >
          </div>
        </div>
        <input
          type="password"
          id="new-password"
          v-model="formResetPassword.new_password"
          @focusout="clearErrorSign('newPassword')"
        />
        <span class="form-error">{{ this.formError.new_password }}</span>
      </div>
      <div>
        <label class="label" for="password-again">{{
          $t("m.Password_Again")
        }}</label>
        <input
          type="password"
          id="password-again"
          v-model="formResetPassword.newPasswordAgain"
          @focusout="clearErrorSign('newPasswordAgain')"
        />
        <span class="form-error">{{ this.formError.newPasswordAgain }}</span>
      </div>
      <div v-if="this.logoutTrigger" class="logout-notice">
        {{ $t("m.You_Will_Be_Logged_Out_In_5_Seconds") }}
      </div>
      <button :class="submitClass" @click="handleResetPassword">
        {{ this.submitText }}
      </button>
    </form>
  </div>
</template>

<style scoped lang="less">
.change-password {
  display: flex;
  flex-direction: column;
  width: 50%;
  gap: 20px;

  form {
    display: flex;
    flex-direction: column;
    gap: 20px;

    .input-header {
      display: flex;
      justify-content: space-between;
    }

    .form-error {
      color: red;
      font-size: 12px;
      height: 14px;
    }

    input {
      width: 100%;
      padding: 5px;
      border: 1px solid var(--border-color);
      border-radius: 5px;
      font-size: 14px;
      margin-top: 5px;
    }
  }
}

.submit-button {
  background-color: var(--point-color);
  text-align: center;
  width: 140px;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 5px 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
}

.button-loading {
  background-color: var(--pale-point-color);
  text-align: center;
  width: 80px;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 5px 10px;
  cursor: not-allowed;
  font-size: 14px;
  font-weight: 700;
}

.logout-notice {
  background-color: var(--pale-point-color);
  font-weight: 600;
  color: var(--point-color);
  padding: 10px;
}

.label {
  font-size: 18px;
  font-weight: 700;
}
</style>
