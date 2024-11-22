import Vue from "vue";
import router from "./router";
import axios from "axios";
import utils from "@/utils/utils";

Vue.prototype.$http = axios;
axios.defaults.baseURL = "/api";
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";

export default {
  // 登录
  login(username, password) {
    return ajax("login", "post", {
      data: {
        username,
        password,
      },
    });
  },
  logout() {
    return ajax("logout", "get");
  },
  getProfile() {
    return ajax("profile", "get");
  },
  getCollegeList() {
    return ajax("college_list", "get");
  },
  getMajorList(collegeID) {
    return ajax("department_list", "get", {
      params: {
        college_id: collegeID,
      },
    });
  },
  // 获取公告列表
  getAnnouncementList(offset, limit) {
    return ajax("admin/announcement", "get", {
      params: {
        paging: true,
        offset,
        limit,
      },
    });
  },
  // 删除公告
  deleteAnnouncement(id) {
    return ajax("admin/announcement", "delete", {
      params: {
        id,
      },
    });
  },
  // 修改公告
  updateAnnouncement(data) {
    return ajax("admin/announcement", "put", {
      data,
    });
  },
  // 添加公告
  createAnnouncement(data) {
    return ajax("admin/announcement", "post", {
      data,
    });
  },
  getStats() {
    return ajax("admin/stat", "get");
  },
  getUserList(offset, limit, query) {
    let params = { paging: true, offset, limit };
    let { keyword, college, department } = query;
    if (keyword) {
      params.keyword = keyword;
    }
    if (college !== "-1") {
      params.college = college;
    }
    if (department !== "-1") {
      params.department = department;
    }
    params.admin_type = "Regular";
    return ajax("admin/user", "get", {
      params: params,
    });
  },
  getAdminList(offset, limit, query) {
    let params = { paging: true, offset, limit };
    let { keyword, college, department } = query;
    if (keyword) {
      params.keyword = keyword;
    }
    if (college !== "-1") {
      params.college = college;
    }
    if (department !== "-1") {
      params.department = department;
    }
    params.admin_type = "Admin";
    return ajax("admin/user", "get", {
      params: params,
    });
  },
  // 获取单个用户信息
  getUser(id) {
    return ajax("admin/user", "get", {
      params: {
        id,
      },
    });
  },
  // 编辑用户
  editUser(data) {
    return ajax("admin/user", "put", {
      data,
    });
  },
  deleteUsers(id) {
    return ajax("admin/user", "delete", {
      params: {
        id,
      },
    });
  },
  importUsers(users) {
    return ajax("admin/user", "post", {
      data: {
        users,
      },
    });
  },
  generateUser(data) {
    return ajax("admin/generate_user", "post", {
      data,
    });
  },
  getLanguages() {
    return ajax("languages", "get");
  },
  getSMTPConfig() {
    return ajax("admin/smtp", "get");
  },
  createSMTPConfig(data) {
    return ajax("admin/smtp", "post", {
      data,
    });
  },
  editSMTPConfig(data) {
    return ajax("admin/smtp", "put", {
      data,
    });
  },
  testSMTPConfig(email) {
    return ajax("admin/smtp_test", "post", {
      data: {
        email,
      },
    });
  },
  getWebsiteConfig() {
    return ajax("admin/website", "get");
  },
  editWebsiteConfig(data) {
    return ajax("admin/website", "post", {
      data,
    });
  },
  getJudgeServer() {
    return ajax("admin/judge_server", "get");
  },
  deleteJudgeServer(hostname) {
    return ajax("admin/judge_server", "delete", {
      params: {
        hostname: hostname,
      },
    });
  },
  updateJudgeServer(data) {
    return ajax("admin/judge_server", "put", {
      data,
    });
  },
  getInvalidTestCaseList() {
    return ajax("admin/prune_test_case", "get");
  },
  pruneTestCase(id) {
    return ajax("admin/prune_test_case", "delete", {
      params: {
        id,
      },
    });
  },
  createContest(data) {
    return ajax("admin/contest", "post", {
      data,
    });
  },
  getContest(id) {
    return ajax("admin/contest", "get", {
      params: {
        id,
      },
    });
  },
  editContest(data) {
    return ajax("admin/contest", "put", {
      data,
    });
  },
  deleteContest(id) {
    return ajax("admin/contest", "delete", {
      params: {
        id,
      },
    });
  },
  getContestList(offset, limit, keyword) {
    let params = { paging: true, offset, limit };
    if (keyword) {
      params.keyword = keyword;
    }
    return ajax("admin/contest", "get", {
      params: params,
    });
  },
  getContestAnnouncementList(contestID) {
    return ajax("admin/contest/announcement", "get", {
      params: {
        contest_id: contestID,
      },
    });
  },
  createContestAnnouncement(data) {
    return ajax("admin/contest/announcement", "post", {
      data,
    });
  },
  deleteContestAnnouncement(id) {
    return ajax("admin/contest/announcement", "delete", {
      params: {
        id,
      },
    });
  },
  updateContestAnnouncement(data) {
    return ajax("admin/contest/announcement", "put", {
      data,
    });
  },
  getContestSubmissionList(offset, limit, params) {
    params.limit = limit;
    params.offset = offset;
    return ajax("admin/contest_submissions", "get", {
      params,
    });
  },
  getContestParticipantList(contest_id) {
    return ajax("admin/contest_participants", "get", {
      params: { contest_id: contest_id },
    });
  },
  getProblemTagList(params) {
    return ajax("problem/tags", "get", {
      params,
    });
  },
  compileSPJ(data) {
    return ajax("admin/compile_spj", "post", {
      data,
    });
  },
  checkDuplicateProblemId(data) {
    return ajax("admin/problem/check_duplicate_id", "post", {
      data,
    });
  },
  createProblem(data) {
    return ajax("admin/problem", "post", {
      data,
    });
  },
  editProblem(data) {
    return ajax("admin/problem", "put", {
      data,
    });
  },
  deleteProblem(id) {
    return ajax("admin/problem", "delete", {
      params: {
        id,
      },
    });
  },
  getProblem(id) {
    return ajax("admin/problem", "get", {
      params: {
        id,
      },
    });
  },
  getProblemList(params) {
    params = utils.filterEmptyValue(params);
    return ajax("admin/problem", "get", {
      params,
    });
  },
  getContestProblemList(params) {
    params = utils.filterEmptyValue(params);
    return ajax("admin/contest/problem", "get", {
      params,
    });
  },
  getContestProblem(id) {
    return ajax("admin/contest/problem", "get", {
      params: {
        id,
      },
    });
  },
  createContestProblem(data) {
    return ajax("admin/contest/problem", "post", {
      data,
    });
  },
  editContestProblem(data) {
    return ajax("admin/contest/problem", "put", {
      data,
    });
  },
  deleteContestProblem(id) {
    return ajax("admin/contest/problem", "delete", {
      params: {
        id,
      },
    });
  },
  makeContestProblemPublic(data) {
    return ajax("admin/contest_problem/make_public", "post", {
      data,
    });
  },
  addProblemFromPublic(data) {
    return ajax("admin/contest/add_problem_from_public", "post", {
      data,
    });
  },
  getReleaseNotes() {
    return ajax("admin/versions", "get");
  },
  getDashboardInfo() {
    return ajax("admin/dashboard_info", "get");
  },
  getSessions() {
    return ajax("sessions", "get");
  },
  exportProblems(data) {
    return ajax("export_problem", "post", {
      data,
    });
  },
  // HomeBannerManagement.vue
  getBanners() {
    return ajax("admin/banner", "get");
  },
  addBanner(data) {
    return ajax("admin/banner", "post", { data });
  },
  deleteBanner(id) {
    return ajax("admin/banner", "delete", {
      params: { id },
    });
  },
  modifyBanner(id, data) {
    return ajax("admin/banner/edit", "post", {
      params: { id },
      data,
    });
  },
  modifyPopup(id, data) {
    return ajax("admin/popup/edit", "post", {
      params: { id },
      data,
    })
  },
  reorderBanner(data) {
    return ajax("admin/banner/reorder", "post", {
      data,
    });
  },
  editEnableBanner(id, data) {
    return ajax("admin/banner/edit", "put", {
      params: { id },
      data,
    });
  },
  getPopups() {
    return ajax("admin/popup", "get");
  },
  addPopup(data) {
    return ajax("admin/popup", "post", { data });
  },
  deletePopup(id) {
    return ajax("admin/popup", "delete", {
      params: { id },
    });
  },
  reorderPopup(data) {
    return ajax("admin/popup/reorder", "post", {
      data,
    });
  },
  editEnablePopup(id, data) {
    return ajax("admin/popup/edit", "put", {
      params: { id },
      data,
    });
  },
};

/**
 * @param url
 * @param method get|post|put|delete...
 * @param params like queryString. if a url is index?a=1&b=2, params = {a: '1', b: '2'}
 * @param data post data, use for method put|post
 * @returns {Promise}
 */
function ajax(url, method, options) {
  if (options !== undefined) {
    var { params = {}, data = {} } = options;
  } else {
    params = data = {};
  }
  return new Promise((resolve, reject) => {
    axios({
      url,
      method,
      params,
      data,
    }).then(
      (res) => {
        // API正常返回(status=20x), 是否错误通过有无error判断
        if (res.data.error !== null) {
          Vue.prototype.$error(res.data.data);
          reject(res);
          // // 若后端返回为登录，则为session失效，应退出当前登录用户
          if (res.data.data.startsWith("Please login")) {
            router.push({ name: "login" });
          }
        } else {
          resolve(res);
          if (method !== "get") {
            Vue.prototype.$success("Succeeded");
          }
        }
      },
      (res) => {
        // API请求异常，一般为Server error 或 network error
        reject(res);
        Vue.prototype.$error(res.data.data);
      }
    );
  });
}
