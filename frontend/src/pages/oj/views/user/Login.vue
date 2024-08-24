<template>
  <div>
    <Form ref="formLogin" :model="formLogin" :rules="ruleLogin">
      <FormItem prop="username">
        <Input
          type="text"
          class="customLoginInput"
          v-model="formLogin.username"
          :placeholder="$t('m.LoginUsername')"
          size="large"
          :autofocus="true"
          @on-enter="handleLogin"
        >
        </Input>
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
      <a class="redirect" @click.stop="goResetPassword" style="">{{
        $t("m.Forget_Password")
      }}</a>
      <a
        class="redirect"
        v-if="website.allow_register"
        @click.stop="handleBtnClick('register')"
        >{{ $t("m.No_Account") }}</a
      >
    </div>
  </div>
</template>

<script>
/*eslint-disable*/
import { mapGetters, mapActions } from "vuex";
import api from "@oj/api";
import { FormMixin } from "@oj/components/mixins";

export default {
  mixins: [FormMixin],
  data() {
    const CheckRequiredTFA = (rule, value, callback) => {
      console.log(value)
      if (value !== "") {
        api.tfaRequiredCheck(value).then(res => {
          this.tfaRequired = res.data.data.result;
        });
      }
      callback();
    };

    return {
      tfaRequired: false,
      btnLoginLoading: false,
      formLogin: {
        username: "",
        password: "",
        tfa_code: ""
      },
      ruleLogin: {
        username: [
          { required: true, trigger: "blur" },
          { validator: CheckRequiredTFA, trigger: "blur" }
        ],
        password: [{ required: true, trigger: "change", min: 6, max: 20 }]
      }
    };
  },
  methods: {
    ...mapActions(["changeModalStatus", "getProfile"]),
    handleBtnClick(mode) {
      this.changeModalStatus({
        mode,
        visible: true
      });
    },
    handleLogin() {
      this.validateForm("formLogin").then(valid => {
        this.btnLoginLoading = true;
        let formData = Object.assign({}, this.formLogin);
        console.log(formData)
        if (!this.tfaRequired) {
          delete formData["tfa_code"];
        }
        api.login(formData).then(
          res => {
            this.btnLoginLoading = false;
            this.changeModalStatus({ visible: false });
            this.getProfile();
            this.$success(this.$i18n.t("m.Welcome_back"));
          },
          _ => {
            this.btnLoginLoading = false;
          }
        );
      });
    },
    goResetPassword() {
      this.changeModalStatus({ visible: false });
      this.$router.push({ name: "apply-reset-password" });
    }
  },
  computed: {
    ...mapGetters(["website", "modalStatus"]),
    visible: {
      get() {
        return this.modalStatus.visible;
      },
      set(value) {
        this.changeModalStatus({ visible: value });
      }
    }
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
  border: none;
  background-color: #32306b;
  font-weight: 600;
  font-size: 14px;
  border-radius: 8px;
}
.customLoginInput {
  //outline: 2px solid #255aa4 !important;
}
.redirect {
  color: #7a7a7a;
  float: right;
  margin-right: 10px;
}
</style>
