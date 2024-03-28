<template>
  <div>
    <Form ref="formRegister" :model="formRegister" :rules="ruleRegister">
      <div class="inputName">
        부산대학교 웹메일
      </div>
      <FormItem prop="pnuWebMail">
        <Input
          v-model="formRegister.email"
          :placeholder="$t('m.Email_Address')"
          size="large"
          @on-enter="handleRegister"
          class="emailAuthInput"
          :autofocus="true"
        >
        </Input>
        <Button
          type="primary"
          class="emailAuthBtn"
          :disabled="this.emailAuthCodeInputState"
          @click="handleClickEmailAuthBtn"
          >인증</Button
        >
      </FormItem>
      <FormItem prop="emailAuthCode" v-if="emailAuthCodeInputState">
        <Input
          v-model="pnuAuthCode"
          :placeholder="$t('m.Email_Auth_Code')"
          size="large"
          @on-enter="handleRegister"
          class="emailCodeInput"
        >
        </Input>
        <Button type="primary"
                class="emailAuthBtn emailCodeBtn"
                @click="handleClickAuthCodeVerificationBtn"
                :disabled="emailAuthCodeVerifyCompletedState"
          >인증완료</Button
        >
      </FormItem>
      <div class="inputName">
        닉네임
      </div>
      <FormItem prop="nickname">
        <Input
          type="text"
          v-model="formRegister.username"
          :placeholder="$t('m.RegisterNickname')"
          size="large"
          @on-enter="handleRegister"
        >
        </Input>
      </FormItem>
      <div class="inputName">
        단과대학 선택
      </div>
      <CustomDropDown :options="this.collegeList" nameKey="college_name" @dropdownChange="handleCollegeChange"/>
      <div class="inputName">
        학과선택
      </div>
      <CustomDropDown :options="this.majorList" nameKey="department_name" @dropdownChange="handleMajorChange"/>
      <div class="inputName">
        비밀번호
      </div>
      <FormItem prop="password">
        <Input
          type="password"
          v-model="formRegister.password"
          :placeholder="$t('m.RegisterPassword')"
          size="large"
          @on-enter="handleRegister"
        >
        </Input>
      </FormItem>
      <div class="inputName">
        비밀번호 확인
      </div>
      <FormItem prop="passwordAgain">
        <Input
          type="password"
          v-model="formRegister.passwordAgain"
          :placeholder="$t('m.Password_Again')"
          size="large"
          @on-enter="handleRegister"
        >
        </Input>
      </FormItem>
    </Form>
    <div class="footer-modal">
      <Button
        type="primary"
        @click="handleRegister"
        class="btn"
        long
        :loading="btnRegisterLoading"
      >
        {{ $t("m.UserRegister") }}
      </Button>
      <div style="text-align: center">
        <a class="redirectLogin" @click.stop="switchMode('login')">{{
          $t("m.UserLogin")
        }}</a>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import api from "@oj/api";
import { FormMixin } from "@oj/components/mixins";
import CustomDropDown from "../../components/dropdown/CustomDropdown.vue";

export default {
  mixins: [FormMixin],
  components: {
    CustomDropDown
  },
  mounted() {
    this.getCollegeList();
    this.getCaptchaSrc();
  },
  data() {
    const CheckPassword = (rule, value, callback) => {
      if (this.formRegister.password !== "") {
        this.$refs.formRegister.validateField("passwordAgain");
      }
      callback();
    };

    const CheckAgainPassword = (rule, value, callback) => {
      if (value !== this.formRegister.password) {
        callback(new Error(this.$i18n.t("m.password_does_not_match")));
      }
      callback();
    };

    return {
      btnRegisterLoading: false,
      emailAuthCodeInputState: false,
      emailAuthCodeVerifyCompletedState: false,
      pnuAuthCode: "",
      formRegister: {
        email: "",
        username: "",
        collegeId: "",
        departmentId: "",
        password: "",
        passwordAgain: "",
        captcha: ""
      },
      ruleRegister: {
        password: [
          { required: true, trigger: "blur", min: 6, max: 20 },
          { validator: CheckPassword, trigger: "blur" }
        ],
        passwordAgain: [
          { required: true, validator: CheckAgainPassword, trigger: "change" }
        ],
      },
      collegeList : [],
      majorList : []
    };
  },
  methods: {
    ...mapActions(["changeModalStatus", "getProfile"]),
    handleClickEmailAuthBtn() {
      api.applyUserEmailValidCheck(this.formRegister.email);
      this.$success("인증 메일이 성공적으로 전송되었습니다.");
      this.emailAuthCodeInputState = true;
    },
    async handleClickAuthCodeVerificationBtn() {
      let res = await api.userEmailValidCheck(this.formRegister.email, this.pnuAuthCode)
      if (res.status === 200) {
        this.emailAuthCodeVerifyCompletedState = true
        this.$success("인증 완료되었습니다.");
      }
      console.log(res)
    },
    switchMode(mode) {
      this.changeModalStatus({
        mode,
        visible: true
      });
    },
    handleRegister() {
      if(!this.emailAuthCodeVerifyCompletedState){
        this.$error("웹메일 인증이 완료되지 않았습니다.")
        return
      }
      this.validateForm("formRegister").then(valid => {
        let formData = Object.assign({}, this.formRegister);
        delete formData["passwordAgain"];
        this.btnRegisterLoading = true;
        api.register(formData).then(
          res => {
            this.$success(this.$i18n.t("m.Thanks_for_registering"));
            this.switchMode("login");
            this.btnRegisterLoading = false;
          },
          _ => {
            this.btnRegisterLoading = false;
          }
        );
      });
    },
    handleCollegeChange(collegeId){
      this.formRegister.collegeId = collegeId
      this.getMajorList(collegeId)
    },
    handleMajorChange(majorId){
      this.formRegister.departmentId = majorId
    },
    async getCollegeList(){
      let res = await api.getCollegeList()
      this.collegeList = res.data.data
    },
    async getMajorList(collegeId){
      let res = await api.getMajorList(collegeId)
      this.majorList = res.data.data
    }
  },
  computed: {
    ...mapGetters(["website", "modalStatus"])
  }
};
</script>

<style scoped lang="less">
.footer-modal {
  overflow: auto;
  margin-top: 20px;
  margin-bottom: -15px;
  text-align: left;
  .btn {
    margin: 0 0 15px 0;
    &:last-child {
      margin: 0;
    }
  }
}
.btn {
  height: 45px;
  background-color: #32306b;
  border: none;
  font-weight: 600;
  font-size: 14px;
  border-radius: 8px;
}
.inputName {
  font-size: small;
  font-weight: 800;
  margin-bottom: 5px;
  margin-left: 1px;
}
.emailAuthBtn {
  height: 36px;
  background-color: #32306b;
  border: none;
  font-weight: 600;
  font-size: 14px;
  border-radius: 8px;
}
.emailAuthInput {
  width: 303px;
}
.emailCodeInput {
  width: 280px;
  animation: fadeIn;
  animation-duration: 0.5s;
  animation-timing-function: ease-in-out;
}
.emailCodeBtn {
  animation: fadeIn;
  animation-duration: 0.5s;
  animation-timing-function: ease-in-out;
}
.redirectLogin {
  color: #7a7a7a;
  text-decoration-line: underline;
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}
</style>
