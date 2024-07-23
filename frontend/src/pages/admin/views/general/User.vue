<template>
  <div class="view">
    <Panel :title="$t('m.User_Statistic')">

    </Panel>

    <Panel :title="$t('m.User_User')">
      <div slot="header">
        <el-row type="flex">
          <el-col :span="8">
            <el-button v-show="selectedUsers.length"
                       type="warning" icon="el-icon-fa-trash"
                       @click="deleteUsers(selectedUserIDs)">{{$t('m.Icon_Delete')}}
            </el-button>
          </el-col>
          <el-col style="margin-right: 15px">
              <el-select v-model="query.college" :placeholder="$t('m.User_Placeholder_College')">
                <template v-for="(item, index) in collegeList">
                  <el-option :label="item.college_name" :value="item.id"></el-option>
                </template>
              </el-select>
          </el-col>
          <el-col style="margin-right: 15px">
            <el-select v-model="query.department" :placeholder="$t('m.User_Placeholder_Department')">
              <template v-for="(item, index) in filteredDepartmentListForQuery">
                <el-option :label="item.department_name" :value="item.id"></el-option>
              </template>
            </el-select>
          </el-col>
          <el-col :span="selectedUsers.length ? 16: 24">
            <el-input v-model="query.keyword" prefix-icon="el-icon-search" placeholder="Keywords"></el-input>
          </el-col>
        </el-row>
      </div>
      <el-table
        v-loading="loadingTable"
        element-loading-text="loading"
        @selection-change="handleSelectionChange"
        ref="table"
        :data="userList"
        style="width: 100%;">
        <el-table-column type="selection" width="55"></el-table-column>

        <el-table-column prop="id" width="55" :label="$t('m.User_Table_ID')"></el-table-column>

        <el-table-column width="60" :label="$t('m.User_Table_User_Avatar')">
          <template slot-scope="scope">
            <img class="avatar" :src="scope.row.avatar"/>
          </template>
        </el-table-column>

        <el-table-column prop="username" width="100" :label="$t('m.User_Table_Username')"></el-table-column>

        <el-table-column prop="email" :label="$t('m.User_Table_Email')"></el-table-column>

        <el-table-column prop="real_name" width="80" :label="$t('m.User_Table_Real_Name')"></el-table-column>

        <el-table-column prop="student_id" width="100" :label="$t('m.User_Table_Student_Id')"></el-table-column>

        <el-table-column width="100"  :label="$t('m.User_Table_User_College')">
          <template slot-scope="scope">
            {{ scope.row.college }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('m.User_Table_User_Department')">
          <template slot-scope="scope">
            {{ scope.row.department }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('m.User_Table_Create_Time')">
          <template slot-scope="scope">
            {{scope.row.create_time | localtime }}
            <br>
            <span style="color: #2d8cf0">{{scope.row.last_login | localtime }}</span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" :label="$t('m.User_Table_Option')" width="120">
          <template slot-scope="{row}">
            <icon-btn :name="$t('m.Icon_Edit')" icon="edit" @click.native="openUserDialog(row.id)"></icon-btn>
            <icon-btn :name="$t('m.Icon_Delete')" icon="trash" @click.native="deleteUsers([row.id])"></icon-btn>
          </template>
        </el-table-column>
      </el-table>
      <div class="panel-options">
        <el-pagination
          class="page"
          layout="prev, pager, next"
          @current-change="currentChange"
          :page-size="pageSize"
          :total="total">
        </el-pagination>
      </div>
    </Panel>

<!--    <Panel>-->
<!--      <span slot="title">{{$t('m.Import_User')}}-->
<!--        <el-popover placement="right" trigger="hover">-->
<!--          <i slot="reference" class="el-icon-fa-question-circle import-user-icon"></i>-->
<!--          <p>{{$t('m.User_Import_Tooltip_Content')}}</p>-->
<!--          <p>{{$t('m.User_Import_Tooltip_Reference')}}: <a href="http://docs.onlinejudge.me/#/onlinejudge/guide/import_users" target="_blank">-->
<!--            http://docs.onlinejudge.me/#/onlinejudge/guide/import_users</a>-->
<!--          </p>-->
<!--        </el-popover>-->
<!--      </span>-->
<!--      <el-upload v-if="!uploadUsers.length"-->
<!--                 action=""-->
<!--                 :show-file-list="false"-->
<!--                 accept=".csv"-->
<!--                 :before-upload="handleUsersCSV">-->
<!--        <el-button size="small" icon="el-icon-fa-upload" type="primary">{{$t('m.Button_Choose_File')}}</el-button>-->
<!--      </el-upload>-->
<!--      <template v-else>-->
<!--        <el-table :data="uploadUsersPage">-->
<!--          <el-table-column :label="$t('m.Import_User_Table_Username')">-->
<!--            <template slot-scope="{row}">-->
<!--              {{row[0]}}-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column :label="$t('m.Import_User_Table_Password')">-->
<!--            <template slot-scope="{row}">-->
<!--              {{row[1]}}-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column :label="$t('m.Import_User_Table_Email')">-->
<!--            <template slot-scope="{row}">-->
<!--              {{row[2]}}-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column :label="$t('m.Import_User_Table_RealName')">-->
<!--            <template slot-scope="{row}">-->
<!--              {{row[3]}}-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--        <div class="panel-options">-->
<!--          <el-button type="primary" size="small"-->
<!--                     icon="el-icon-fa-upload"-->
<!--                     @click="handleUsersUpload">{{$t('m.Button_Import_All')}}-->
<!--          </el-button>-->
<!--          <el-button type="warning" size="small"-->
<!--                     icon="el-icon-fa-undo"-->
<!--                     @click="handleResetData">{{$t('m.Button_Reset_Data')}}-->
<!--          </el-button>-->
<!--          <el-pagination-->
<!--            class="page"-->
<!--            layout="prev, pager, next"-->
<!--            :page-size="uploadUsersPageSize"-->
<!--            :current-page.sync="uploadUsersCurrentPage"-->
<!--            :total="uploadUsers.length">-->
<!--          </el-pagination>-->
<!--        </div>-->
<!--      </template>-->
<!--    </Panel>-->

    <Panel :title="$t('m.Generate_User')">
      <el-form :model="formGenerateUser" ref="formGenerateUser">
        <el-row style="margin-bottom: 10px">
          <span style="color: #5c6773; font-weight: 800; font-size: medium">{{ $t('m.Create_User_Table_Option_School') }}</span>
        </el-row>
        <el-row type="flex">
          <el-col :span="4" style="margin-right: 15px">
            <el-form-item :label="$t('m.Create_User_Table_College')">
              <el-select v-model="formGenerateUser.college" :placeholder="$t('m.User_Placeholder_College')">
                <template v-for="(item, index) in collegeList">
                  <el-option :label="item.college_name" :value="item.id"></el-option>
                </template>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4" style="margin-right: 15px">
            <el-form-item :label="$t('m.Create_User_Table_Department')">
              <el-select v-model="formGenerateUser.department" :placeholder="$t('m.User_Placeholder_Department')">
                <template v-for="(item, index) in filteredDepartmentListForDummy">
                  <el-option :label="item.department_name" :value="item.id"></el-option>
                </template>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row style="margin-bottom: 10px">
          <span style="color: #5c6773; font-weight: 800; font-size: medium">{{ $t('m.Create_User_Table_Option_Account') }}</span>
        </el-row>
        <el-row type="flex">
          <el-col :span="4" style="margin-right: 15px">
            <el-form-item :label="$t('m.Create_User_Table_Prefix')" prop="prefix" required>
              <el-input v-model="formGenerateUser.prefix" :placeholder="$t('m.Create_User_Table_Prefix')"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="4" style="margin-right: 15px">
            <el-form-item :label="$t('m.Create_User_Table_Number_Of_Mock')" required>
              <el-input-number v-model="formGenerateUser.num_of_mock" style="width: 100%"></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row style="margin-bottom: 10px">
          <span style="color: #6d88b6"> {{$t('m.Create_User_Table_Notice')}} </span>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="generateUser" icon="el-icon-fa-users" :loading="loadingGenerate">{{$t('m.Button_Generate_Export')}}
          </el-button>
        </el-form-item>
      </el-form>
    </Panel>
    <el-dialog :title="$t('m.User_Info')" :visible.sync="showUserDialog" :close-on-click-modal="false">
      <el-form :model="user" label-width="120px" label-position="left">
        <el-col style="margin-bottom: 20px">
          <span style="font-weight: bold;font-size: medium">계정 정보</span>
        </el-col>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="$t('m.User_Email')">
              <el-input v-model="user.email" :disabled="true"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.User_Username')">
              <el-input v-model="user.username"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.User_Real_Name')">
              <el-input v-model="user.real_name"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.User_New_Password')">
              <input class="user-password-input" v-model="user.password"></input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.User_Type')">
              <el-select v-model="user.admin_type">
                <el-option label="Regular User" value="Regular User"></el-option>
                <el-option label="Admin" value="Admin"></el-option>
                <el-option label="Super Admin" value="Super Admin"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.Problem_Permission')">
              <el-select v-model="user.problem_permission" :disabled="user.admin_type!=='Admin'">
                <el-option label="None" value="None"></el-option>
                <el-option label="Own" value="Own"></el-option>
                <el-option label="All" value="All"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col style="margin-bottom: 20px; margin-top: 20px">
           <span style="font-weight: bold;font-size: medium">학과 정보</span>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.Create_User_Table_College')">
              <el-select v-model="user.college" :placeholder="$t('m.User_Placeholder_College')">
                <template v-for="(item, index) in collegeList">
                  <el-option :label="item.college_name" :value="item.id"></el-option>
                </template>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.Create_User_Table_Department')">
              <el-select v-model="user.department" :placeholder="$t('m.User_Placeholder_Department')">
                <template v-for="(item, index) in filteredDepartmentListForEdit">
                  <el-option :label="item.department_name" :value="item.id"></el-option>
                </template>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.Create_User_Table_Student_Id')">
              <el-input v-model="user.student_id"></el-input>
            </el-form-item>
          </el-col>
          <el-col style="margin-bottom: 20px; margin-top: 10px">
            <span style="font-weight: bold;font-size: medium">기타 정보</span>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('m.Two_Factor_Auth')">
              <el-switch
                v-model="user.two_factor_auth"
                :disabled="!user.real_tfa"
                active-color="#13ce66"
                inactive-color="#ff4949">
              </el-switch>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Open Api">
              <el-switch
                v-model="user.open_api"
                active-color="#13ce66"
                inactive-color="#ff4949">
              </el-switch>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('m.Is_Disabled')">
              <el-switch
                v-model="user.is_disabled">
              </el-switch>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <cancel @click.native="showUserDialog = false">Cancel</cancel>
        <save @click.native="saveUser()"></save>
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import papa from 'papaparse'
  import api from '../../api.js'
  import utils from '@/utils/utils'

  export default {
    name: 'User',
    data () {
      return {
        pageSize: 10,
        total: 0,
        userList: [],
        uploadUsers: [],
        uploadUsersPage: [],
        uploadUsersCurrentPage: 1,
        uploadUsersPageSize: 15,
        query:{
          keyword: '',
          college: '',
          department: '',
          active: true
        },
        showUserDialog: false,
        user: {},
        loadingTable: false,
        loadingGenerate: false,
        currentPage: 0,
        selectedUsers: [],
        formGenerateUser: {
          prefix: '',
          num_of_mock: 0,
          college: '',
          department: ''
        },
        collegeList: [],
        departmentList: [],
        departmentItems: []
      }
    },
    mounted () {
      this.getUserList(1)
      this.getCollegeList()
      this.getDepartmentList()
    },
    methods: {
      currentChange (page) {
        this.currentPage = page
        this.getUserList(page)
      },
      saveUser () {
        console.log(this.user)
        api.editUser(this.user).then(res => {
          this.getUserList(this.currentPage)
        }).then(() => {
          this.showUserDialog = false
        }).catch(() => {
        })
      },
      openUserDialog (id) {
        this.showUserDialog = true
        api.getUser(id).then(res => {
          this.user = res.data.data
          this.user.password = ''
          this.user.real_tfa = this.user.two_factor_auth
          this.user.college = null
          this.user.department = null
        })
      },
      async getCollegeList() {
        let res = await api.getCollegeList()
        this.collegeList = [
          {
            id: "-1",
            college_name: "전체"
          },
          ...res.data.data
        ];
      },
      async getDepartmentList() {
        let res = await api.getMajorList()
        this.departmentList = [
          {
            id: "-1",
            department_name: "전체"
          },
          ...res.data.data
        ];
      },
      getUserList (page) {
        this.loadingTable = true
        api.getUserList((page - 1) * this.pageSize, this.pageSize, this.query).then(res => {
          this.loadingTable = false
          this.total = res.data.data.total
          this.userList = res.data.data.results
        }, res => {
          this.loadingTable = false
        })
      },
      deleteUsers (ids) {
        this.$confirm(this.$t('m.Delete_User_Modal_Content'), this.$t('m.Delete_User_Modal_Title'), {
          type: 'warning'
        }).then(() => {
          api.deleteUsers(ids.join(',')).then(res => {
            this.getUserList(this.currentPage)
          }).catch(() => {
            this.getUserList(this.currentPage)
          })
        }, () => {
        })
      },
      handleSelectionChange (val) {
        this.selectedUsers = val
      },
      generateUser () {
        this.$refs['formGenerateUser'].validate((valid) => {
          if (!valid) {
            this.$error('Please validate the error fields')
            return
          }
          if (this.formGenerateUser.num_of_mock === 0){
            this.$error('Please validate the Num of Mock User fields')
            return
          }
          this.loadingGenerate = true
          let data = Object.assign({}, this.formGenerateUser)
          api.generateUser(data).then(res => {
            this.loadingGenerate = false
            let url = '/admin/generate_user?file_id=' + res.data.data.file_id
            utils.downloadFile(url).then(() => {
              this.$alert(this.$t('m.Create_User_Modal_Content'), this.$t('m.Create_User_Modal_Title'))
            })
            this.getUserList(1)
          }).catch(() => {
            this.loadingGenerate = false
          })
        })
      },
      handleUsersCSV (file) {
        papa.parse(file, {
          complete: (results) => {
            let data = results.data.filter(user => {
              return user[0] && user[1] && user[2] && user[3]
            })
            let delta = results.data.length - data.length
            if (delta > 0) {
              this.$warning(delta + ' users have been filtered due to empty value')
            }
            this.uploadUsersCurrentPage = 1
            this.uploadUsers = data
            this.uploadUsersPage = data.slice(0, this.uploadUsersPageSize)
          },
          error: (error) => {
            this.$error(error)
          }
        })
      },
      handleUsersUpload () {
        api.importUsers(this.uploadUsers).then(res => {
          this.getUserList(1)
          this.handleResetData()
        }).catch(() => {
        })
      },
      handleResetData () {
        this.uploadUsers = []
      }
    },
    computed: {
      selectedUserIDs () {
        let ids = []
        for (let user of this.selectedUsers) {
          ids.push(user.id)
        }
        return ids
      },
      filteredDepartmentListForQuery() {
        if(this.query.college === "-1"){
          return []
        }
        return this.departmentList.filter(item => item.college_id === this.query.college);
      },
      filteredDepartmentListForDummy() {
        if(this.formGenerateUser.college === "-1"){
          return []
        }
        return this.departmentList.filter(item => item.college_id === this.formGenerateUser.college);
      },
      filteredDepartmentListForEdit() {
        if(this.user.college === "-1"){
          return []
        }
        return this.departmentList.filter(item => item.college_id === this.user.college);
      }
    },
    watch: {
      query: {
        handler() {
          this.currentChange(1);
        },
        deep: true,
        immediate: false
      },
      'formGenerateUser.college' (){
        this.formGenerateUser.department = ''
      },
      'query.college' (){
        this.query.department = ''
      },
      'user.college' (){
        this.user.department = null
      },
      'user.admin_type' () {
        if (this.user.admin_type === 'Super Admin') {
          this.user.problem_permission = 'All'
        } else if (this.user.admin_type === 'Regular User') {
          this.user.problem_permission = 'None'
        }
      },
      'uploadUsersCurrentPage' (page) {
        this.uploadUsersPage = this.uploadUsers.slice((page - 1) * this.uploadUsersPageSize, page * this.uploadUsersPageSize)
      }
    }
  }
</script>

<style scoped lang="less">
  .user-password-input {
    -webkit-appearance: none;
    background-color: #fff;
    background-image: none;
    border-radius: 4px;
    border: 1px solid #dcdfe6;
    box-sizing: border-box;
    color: #606266;
    display: inline-block;
    height: 40px;
    line-height: 40px;
    outline: 0;
    padding: 0 15px;
    -webkit-transition: border-color .2s cubic-bezier(.645,.045,.355,1);
    transition: border-color .2s cubic-bezier(.645,.045,.355,1);
    width: 100%;
  }

  .import-user-icon {
    color: #555555;
    margin-left: 4px;
  }

  .userPreview {
    padding-left: 10px;
  }

  .notification {
    p {
      margin: 0;
      text-align: left;
    }
  }

  @avatar-radius: 50%;

  .avatar {
    width: 30px;
    border-radius: @avatar-radius;
    box-shadow: 0px 0px 1px 0px;
  }
</style>
