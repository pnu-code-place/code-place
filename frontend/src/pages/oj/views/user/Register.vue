<template>
  <div>
    <Form ref="formRegister" :model="formRegister" :rules="ruleRegister">
      <div class="inputNameWithDescription">
        <span class="inputName">부산대학교 웹메일</span>
        <div>
          <Icon type="ios-information" size="13" color="#7a7a7a"></Icon>
          <span>부산대학교 웹메일이 없으신가요? <a href="https://zm911.mailplug.com/member/join" class="webMailSignUpLink">가입하기</a></span>
        </div>
      </div>
      <FormItem prop="pnuWebMail">
        <div class="email-form">
          <div class="email-input">
            <Input
              v-model="formRegister.email"
              :placeholder="$t('m.Email_Address')"
              size="large"
              @on-enter="handleRegister"
              class="emailAuthInput"
              :autofocus="true"
            >
            </Input>
            <span class="pusan-ac-kr">{{ this.pusanDomain }}</span>
          </div>
          <Button
            type="primary"
            class="emailAuthBtn"
            :disabled="this.emailAuthCodeInputState"
            @click="handleClickEmailAuthBtn"
          >인증
          </Button>
        </div>
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
        >인증완료
        </Button
        >
      </FormItem>
      <div class="inputNameWithDescription">
        <span class="inputName">닉네임</span>
        <div>
          <Icon type="ios-information" size="13" color="#7a7a7a"></Icon>
          <span>3글자 이상, 8글자 이하만 가능합니다.</span>
        </div>
      </div>
      <FormItem prop="nickname">
        <Input
          type="text"
          v-model="formRegister.username"
          :placeholder="$t('m.RegisterNickname')"
          size="large"
          maxlength="8"
          class="nicknameAuthInput"
          @on-enter="handleRegister"
        >
        </Input>
        <Button
          type="primary"
          class="nicknameAuthBtn"
          @click="handleClickNicknameAuthBtn"
        >중복체크
        </Button>
      </FormItem>
      <div class="inputName">
        학번
      </div>
      <FormItem prop="student_id">
        <Input
          type="text"
          v-model="formRegister.student_id"
          :placeholder="$t('m.RegisterStudentId')"
          size="large"
          @on-enter="handleRegister"
        >
        </Input>
      </FormItem>
      <div class="inputName">
        이름(실명)
      </div>
      <FormItem prop="real_name">
        <Input
          type="text"
          v-model="formRegister.real_name"
          :placeholder="$t('m.RegisterRealName')"
          size="large"
          @on-enter="handleRegister"
        >
        </Input>
      </FormItem>
      <div class="inputName">
        단과대학 선택
      </div>
      <CustomDropDown style="margin-bottom: 20px" :options="this.collegeList" nameKey="college_name" @dropdownChange="handleCollegeChange"/>
      <div class="inputName">
        학과선택
      </div>
      <CustomDropDown style="margin-bottom: 20px" :options="this.majorList" nameKey="department_name" @dropdownChange="handleMajorChange"/>
      <div class="inputNameWithDescription">
        <span class="inputName">비밀번호</span>
        <div>
          <Icon type="ios-information" size="13" color="#7a7a7a"></Icon>
          <span>8글자 이상, 영문, 숫자, 특수문자를 모두 사용해야 합니다.</span>
        </div>
      </div>
      <FormItem prop="password">
        <div class="password-input">
          <Input
            :type="passwordFieldType"
            v-model="formRegister.password"
            :placeholder="$t('m.RegisterPassword')"
            size="large"
            @on-enter="handleRegister"
          >
          </Input>
          <i
            :class="['fa', 'fa-lg', passwordFieldType === 'password' ? 'fa-eye' : 'fa-eye-slash']"
            @click="togglePasswordVisibility"
          ></i>
        </div>
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
import {mapGetters, mapActions} from "vuex";
import api from "@oj/api";
import {FormMixin} from "@oj/components/mixins";
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

    const CheckUsernameNotExist = (rule, value, callback) => {
      api.checkUsernameOrEmail(value, undefined).then(
        res => {
          if (res.data.data.username === true) {
            callback(new Error(this.$i18n.t("m.The_username_already_exists")));
          } else {
            callback();
          }
        },
        _ => callback()
      );
    };
    const CheckEmailNotExist = (rule, value, callback) => {
      api.checkUsernameOrEmail(undefined, value).then(
        res => {
          if (res.data.data.email === true) {
            callback(new Error(this.$i18n.t("m.The_email_already_exists")));
          } else {
            callback();
          }
        },
        _ => callback()
      );
    };

    const CheckAgainPassword = (rule, value, callback) => {
      if (value !== this.formRegister.password) {
        callback(new Error(this.$i18n.t("m.password_does_not_match")));
      }
      callback();
    };

    return {
      pusanDomain: "@pusan.ac.kr",
      btnRegisterLoading: false,
      passwordFieldType: 'password',
      nicknameVerifyCompletedState: false,
      emailAuthCodeInputState: false,
      emailAuthCodeVerifyCompletedState: false,
      pnuAuthCode: "",
      formRegister: {
        email: "",
        username: "",
        real_name: "",
        student_id: "",
        collegeId: "",
        departmentId: "",
        password: "",
        passwordAgain: "",
        captcha: ""
      },
      ruleRegister: {
        password: [
          {required: true, trigger: "blur", min: 8, max: 20},
          {validator: CheckPassword, trigger: "blur"}
        ],
        passwordAgain: [
          {required: true, validator: CheckAgainPassword, trigger: "change"}
        ],
      },
      collegeList: [],
      majorList: []
    };
  },
  methods: {
    ...mapActions(["changeModalStatus", "getProfile"]),
    handleClickEmailAuthBtn() {
      api.applyUserEmailValidCheck(this.pusanEmail)
        .then(res => {
          this.$success("인증 메일이 성공적으로 전송되었습니다.");
          this.emailAuthCodeInputState = true;
        })
        .catch(error => {
          if (error.response) {
            switch (error.response.status) {
              case 400:
                this.$error("중복된 이메일이 존재합니다. 다른 이메일을 이용해주세요.");
                break;
              default:
                this.$error("알 수 없는 오류가 발생하였습니다.");
            }
          }
        })
    },
    handleClickNicknameAuthBtn() {
      if(this.formRegister.username.length < 3 || this.formRegister.username.length > 8){
        this.$error("3글자 이상, 8글자 이하만 가능합니다.");
        return
      }
      api.nicknameValidCheck(this.formRegister.username)
        .then(res => {
          this.$success("사용 가능한 닉네임입니다.");
        })
        .catch(error => {
          if (error.response) {
            switch (error.response.status) {
              case 400:
                this.$error("중복된 닉네임이 존재합니다. 다른 닉네임을 이용해주세요.");
                break;
              default:
                this.$error("알 수 없는 오류가 발생하였습니다.");
            }
          }
        });
    },
    async handleClickAuthCodeVerificationBtn() {
      let res = await api.userEmailValidCheck(this.pusanEmail, this.pnuAuthCode)
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
    togglePasswordVisibility() {
      this.passwordFieldType = this.passwordFieldType === 'password' ? 'text' : 'password'
    },
    handleRegister() {
      if (!this.emailAuthCodeVerifyCompletedState) {
        this.$error("웹메일 인증이 완료되지 않았습니다.")
        return
      }
      this.validateForm("formRegister").then(valid => {
        let formData = Object.assign({}, this.formRegister);
        formData["email"] = this.pusanEmail
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
        ).catch(err => {
          this.$error(err.data)
        });
      });
    },
    handleCollegeChange(collegeId) {
      this.formRegister.collegeId = collegeId
      this.getMajorList(collegeId)
    },
    handleMajorChange(majorId) {
      this.formRegister.departmentId = majorId
    },
    async getCollegeList() {
      let res = await api.getCollegeList()
      this.collegeList = res.data.data
    },
    async getMajorList(collegeId) {
      let res = await api.getMajorList(collegeId)
      this.majorList = res.data.data
    }
  },
  computed: {
    pusanEmail() {
      return this.formRegister.email + this.pusanDomain;
    },
    ...mapGetters(["website", "modalStatus"])
  }
};
</script>

<style scoped lang="less">
.footer-modal {
  overflow: auto;
  margin-top: 20px;
  margin-bottom: -20px;
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
  margin-left: 1px;
}

.inputNameWithDescription {
  display: flex;
  justify-content: space-between;
}

.emailAuthBtn {
  height: 36px;
  background-color: #32306b;
  border: none;
  font-weight: 600;
  font-size: 14px;
  border-radius: 8px;
  width: 94px;
}

.emailAuthInput {
  display: flex;

}

button:disabled {
  background-color: #f5f5f5;
}

.nicknameAuthInput {
  width: 280px;
}

.password-input {
  display: flex;
  align-items: center;
  width: 100%;
  position: relative;

  i {
    position: absolute;
    font-size: 15px;
    right: 10px;
  }
}

.passwordAuthInput {
  width: 320px;
}

.nicknameAuthBtn {
  height: 36px;
  background-color: #32306b;
  border: none;
  font-weight: 600;
  font-size: 14px;
  border-radius: 8px;
  width: 78px;
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
  width: 78px;
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

.webMailSignUpLink {
  color: var(--point-color);
  text-decoration: none;

  &:hover {
    color: lighten(#32306b, 10%);
  }
}

.email-form {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap : 5px;

  .email-input {
    display: flex;
    align-items: center;
    width: 100%;
    position: relative;

    .pusan-ac-kr {
      position: absolute;
      font-size: 15px;
      right: 10px;
      color: var(--point-color);
    }
  }
}
</style>
