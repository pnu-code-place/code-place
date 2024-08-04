<template>
  <div class="setting-main">
    <h2>{{ $t('m.Avatar_Setting') }}</h2>
    <template v-if="!avatarOption.imgSrc">
      <Upload type="drag"
              class="mini-container"
              accept=".jpg,.jpeg,.png,.bmp,.gif"
              action=""
              :before-upload="handleSelectFile">
        <div style="padding: 30px 0">
          <Icon type="ios-cloud-upload" size="52" style="color: #3399ff"></Icon>
          <p>{{ $t('m.Upload_Image') }}</p>
        </div>
      </Upload>
    </template>
    <template v-else>
      <div class="flex-container">
        <div class="cropper-wrapper">
          <div class="cropper-main inline">
            <vueCropper
              ref="cropper"
              autoCrop
              fixed
              :autoCropWidth="200"
              :autoCropHeight="200"
              :img="avatarOption.imgSrc"
              :outputSize="avatarOption.size"
              :outputType="avatarOption.outputType"
              :info="true"
              @realTime="realTime">
            </vueCropper>
          </div>
          <ButtonGroup vertical class="cropper-btn">
            <Button @click="rotate('left')">
              <Icon type="arrow-return-left" size="20"></Icon>
            </Button>
            <Button @click="rotate('right')">
              <Icon type="arrow-return-right" size="20"></Icon>
            </Button>
            <Button @click="reselect">
              <Icon type="refresh" size="20"></Icon>
            </Button>
          </ButtonGroup>
        </div>
        <div class="preview-wrapper">
          <div class="cropper-preview" :style="previewStyle">
            <div :style=" preview.div">
              <img :src="avatarOption.imgSrc" :style="preview.img">
            </div>
          </div>
        </div>
        <button @click="finishCrop">{{$t('m.Save')}}</button>
      </div>
    </template>
    <Modal v-model="uploadModalVisible"
           title="Upload the avatar"
           :styles="{zIndex: 2000}"
    >
      <div class="upload-modal">
        <p class="notice">{{ $t('m.Avatar_Preview') }}</p>
        <img :src="uploadImgSrc"/>
      </div>
      <div slot="footer">
        <Button @click="uploadAvatar" :loading="loadingUploadBtn" type="primary">{{ $t('m.Confirm') }}</Button>
      </div>
    </Modal>
  </div>
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
  emits: ['finishCrop'],
  data() {
    return {
      loadingSaveBtn: false,
      loadingUploadBtn: false,
      uploadModalVisible: false,
      preview: {},
      uploadImgSrc: '',
      avatarOption: {
        imgSrc: '',
        size: 0.8,
        outputType: 'png'
      },
      languages: languages,
    }
  },
  methods: {
    checkFileType(file) {
      if (!/\.(gif|jpg|jpeg|png|bmp|GIF|JPG|PNG)$/.test(file.name)) {
        this.$Notice.warning({
          title: 'File type not support',
          desc: 'The format of ' + file.name + ' is incorrect ，please choose image only.'
        })
        return false
      }
      return true
    },
    checkFileSize(file) {
      // max size is 2MB
      if (file.size > 2 * 1024 * 1024) {
        this.$Notice.warning({
          title: 'Exceed max size limit',
          desc: 'File ' + file.name + ' is too big, you can upload a image up to 2MB in size'
        })
        return false
      }
      return true
    },
    handleSelectFile(file) {
      let isOk = this.checkFileType(file) && this.checkFileSize(file)
      if (!isOk) {
        return false
      }
      let reader = new window.FileReader()
      reader.onload = (e) => {
        this.avatarOption.imgSrc = e.target.result
      }
      reader.readAsDataURL(file)
      return false
    },
    realTime(data) {
      this.preview = data
    },
    rotate(direction) {
      if (direction === 'left') {
        this.$refs.cropper.rotateLeft()
      } else {
        this.$refs.cropper.rotateRight()
      }
    },
    reselect() {
      this.$Modal.confirm({
        content: 'Are you sure to discard the changes?',
        onOk: () => {
          this.avatarOption.imgSrc = ''
        }
      })
    },
    finishCrop() {
      this.$refs.cropper.getCropData(data => {
        this.uploadImgSrc = data
        this.uploadModalVisible = true
      })
      this.$emit('finishCrop')
    },
    uploadAvatar() {
      this.$refs.cropper.getCropBlob(blob => {
        let form = new window.FormData()
        let file = new window.File([blob], 'avatar.' + this.avatarOption.outputType)
        form.append('image', file)
        this.loadingUploadBtn = true
        this.$http({
          method: 'post',
          url: 'upload_avatar',
          data: form,
          headers: {'content-type': 'multipart/form-data'}
        }).then(res => {
          this.loadingUploadBtn = false
          this.$success('Successfully set new avatar')
          this.uploadModalVisible = false
          this.avatarOption.imgSrc = ''
          this.$store.dispatch('getProfile')
        }, () => {
          this.loadingUploadBtn = false
        })
      })
    },
    updateProfile() {
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
  computed: {
    previewStyle() {
      return {
        'width': this.preview.w + 'px',
        'height': this.preview.h + 'px',
        'overflow': 'hidden'
      }
    }
  }
}
</script>

<style lang="less" scoped>

h2 {
  font-size: 20px;
}

.setting-main {
  background-color: var(--bg-color);
}

label {
  font-size: 13px;
  font-weight: bold;
  margin-bottom: 5px;
  margin-left: 1px;
  text-align: left;
}

.inline {
  display: inline-block;
}

.copper-img {
  width: 100%;
  height: 250px;
}

.flex-container {
  flex-wrap: wrap;
  align-items: center;
  display: flex;
  flex-direction: column;
  gap:10px;


  .cropper-wrapper {
    width: 100%;
    position: relative;

    .cropper-main {
      flex: none;
      .copper-img;
    }

    .cropper-btn {
      position: absolute;
      right: 0;
      flex: none;
      vertical-align: top;
    }
  }

  .preview-wrapper {
    min-height: 250px;
    width: 100%;
    align-items: center;
    display: flex;
    flex-direction: column;

    .cropper-preview {
      flex: none;
      box-shadow: 0 0 1px 0;
      .copper-img;
    }
  }

  button {
    background-color: var(--point-color);
    text-align: center;
    width: 80px;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 5px 10px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 700;
  }
}

.upload-modal {
  .notice {
    font-size: 16px;
    display: inline-block;
    vertical-align: top;
    padding: 10px;
    padding-right: 15px;
  }

  img {
    box-shadow: 0 0 1px 0;
    border-radius: 50%;
  }
}
</style>
