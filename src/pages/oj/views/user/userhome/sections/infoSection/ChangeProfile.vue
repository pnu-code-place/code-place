<template>
  <Form ref="formProfile" :model="formProfile">
    <Row type="flex" :gutter="30" justify="space-around">
      <Col :span="11">
        <FormItem label="Real Name">
          <Input v-model="formProfile.real_name"/>
        </FormItem>
        <Form-item label="School">
          <Input v-model="formProfile.school"/>
        </Form-item>
        <Form-item label="Major">
          <Input v-model="formProfile.major"/>
        </Form-item>
        <FormItem label="Language">
          <Select v-model="formProfile.language">
            <Option v-for="lang in languages" :key="lang.value" :value="lang.value">{{ lang.label }}</Option>
          </Select>
        </FormItem>
        <Form-item>
          <Button type="primary" @click="updateProfile" :loading="loadingSaveBtn">Save All</Button>
        </Form-item>
      </Col>

      <Col :span="11">
        <Form-item label="Mood">
          <Input v-model="formProfile.mood"/>
        </Form-item>
        <Form-item label="Blog">
          <Input v-model="formProfile.blog"/>
        </Form-item>
        <Form-item label="Github">
          <Input v-model="formProfile.github"/>
        </Form-item>
      </Col>
    </Row>
  </Form>
</template>

<script>
import api from '@oj/api'
import utils from '@/utils/utils'
import {VueCropper} from 'vue-cropper'
import {types} from '@/store'
import {languages} from '@/i18n'

export default {
  components: {
    VueCropper
  },
  data () {
    return {
      loadingSaveBtn: false,
      loadingUploadBtn: false,
      uploadModalVisible: false,
      languages: languages,
      formProfile: {
        real_name: '',
        mood: '',
        major: '',
        blog: '',
        school: '',
        github: '',
        language: ''
      }
    }
  },
  mounted () {
    let profile = this.$store.state.user.profile
    Object.keys(this.formProfile).forEach(element => {
      if (profile[element] !== undefined) {
        this.formProfile[element] = profile[element]
      }
    })
  },
  methods: {
    updateProfile () {
      this.loadingSaveBtn = true
      let updateData = utils.filterEmptyValue(Object.assign({}, this.formProfile))
      api.updateProfile(updateData).then(res => {
        this.$success('Success')
        this.$store.commit(types.CHANGE_PROFILE, {profile: res.data.data})
        this.loadingSaveBtn = false
      }, _ => {
        this.loadingSaveBtn = false
      })
    }
  },
}
</script>


<style scoped lang="less">

</style>
