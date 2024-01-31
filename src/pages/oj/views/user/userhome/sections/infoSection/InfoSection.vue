<template>
  <section>
    <h1>회원 정보</h1>
    <ProfileSetting></ProfileSetting>
    <h2>{{ $t('m.ChangePassword') }}</h2>
    <AccountSetting></AccountSetting>
  </section>
</template>

<script>
import {defineComponent} from "vue";
import ProfileSetting from "../../../../setting/children/ProfileSetting.vue";
import AccountSetting from "../../../../setting/children/AccountSetting.vue";

export default defineComponent({
  components: {ProfileSetting, AccountSetting}
})
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
