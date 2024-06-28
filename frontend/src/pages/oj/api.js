import Vue from "vue";
import store from "@/store";
import axios from "axios";
import {
  AchievementSectionProp,
  DashboardSectionProp,
  MajorRankListProp,
  ProblemSectionProp,
  SurgeUserProps,
  UserRankListProp,
} from "../../prop";

Vue.prototype.$http = axios;
axios.defaults.baseURL = "/api";
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";

export default {
  getWebsiteConf(params) {
    return ajax("website", "get", {
      params,
    });
  },
  getAnnouncementList(offset, limit) {
    let params = {
      offset: offset,
      limit: limit,
    };
    return ajax("announcement", "get", {
      params,
    });
  },
  login(data) {
    return ajax("login", "post", {
      data,
    });
  },
  checkUsernameOrEmail(username, email) {
    return ajax("check_username_or_email", "post", {
      data: {
        username,
        email,
      },
    });
  },
  applyUserEmailValidCheck(email) {
    return ajax("apply_user_email_valid_check", "post", {
      data: {
        email,
      },
    });
  },
  userEmailValidCheck(email, code) {
    console.log("applyUserEmailValidCheck email: ", email, code);
    return ajax("user_email_valid_check", "post", {
      data: {
        email,
        code,
      },
    });
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
  // 注册
  register(data) {
    return ajax("register", "post", {
      data,
    });
  },
  logout() {
    return ajax("logout", "get");
  },
  getCaptcha() {
    return ajax("captcha", "get");
  },
  getUserInfo(username = undefined) {
    return ajax("profile", "get", {
      params: {
        username,
      },
    });
  },
  getDashboardInfo(username) {
    return ajax("profile/dashboard", "get", {
      params: {
        username,
      },
    });
    // return new Promise((resolve) => {
    //   setTimeout(() => {
    //     resolve({data: {data: DashboardSectionProp}})
    //   }, 300)
    // })
  },
  getUserProblemInfo(username, query) {
    return ajax("profile/problem", "get", {
      params: {
        username,
        ...query,
      },
    });
    // return new Promise((resolve) => {
    //   setTimeout(() => {
    //     resolve({data: {data: ProblemSectionProp}})
    //   }, 900)
    // })
  },
  getPersonalRecommendProblem() {
    return ajax("recommend_problem", "get");
  },
  // getUserAchievement(username) {
  //   return ajax("profile/achievement", "get", {
  //     params: {
  //       username
  //     }
  //   });
  //   return new Promise((resolve) => {
  //     setTimeout(() => {
  //       resolve({data: {data: AchievementSectionProp}})
  //     }, 1000)
  //   })
  // },

  updateProfile(profile) {
    return ajax("profile", "put", {
      data: profile,
    });
  },
  getHomeRealTimeRanking() {
    return ajax("home_ranking", "get");
  },
  getHomeBonusProblem() {
    return ajax("problem/bonus", "get");
  },
  getMostDifficultProblem() {
    return ajax("problem/most_difficult_problem", "get");
  },
  freshDisplayID(userID) {
    return ajax("profile/fresh_display_id", "get", {
      params: {
        user_id: userID,
      },
    });
  },
  twoFactorAuth(method, data) {
    return ajax("two_factor_auth", method, {
      data,
    });
  },
  tfaRequiredCheck(email) {
    return ajax("tfa_required", "post", {
      data: {
        email,
      },
    });
  },
  getSessions() {
    return ajax("sessions", "get");
  },
  deleteSession(sessionKey) {
    return ajax("sessions", "delete", {
      params: {
        session_key: sessionKey,
      },
    });
  },
  applyResetPassword(data) {
    return ajax("apply_reset_password", "post", {
      data,
    });
  },
  resetPassword(data) {
    return ajax("reset_password", "post", {
      data,
    });
  },
  changePassword(data) {
    return ajax("change_password", "post", {
      data,
    });
  },
  changeEmail(data) {
    return ajax("change_email", "post", {
      data,
    });
  },
  getLanguages() {
    return ajax("languages", "get");
  },
  getProblemTagList() {
    return ajax("problem/tags", "get");
  },
  getProblemList(offset, limit, searchParams) {
    let params = {
      paging: true,
      offset,
      limit,
    };
    Object.keys(searchParams).forEach((element) => {
      if (searchParams[element]) {
        params[element] = searchParams[element];
      }
    });
    return ajax("problem", "get", {
      params: params,
    });
  },
  pickone() {
    return ajax("pickone", "get");
  },
  getProblem(problemID) {
    return ajax("problem", "get", {
      params: {
        problem_id: problemID,
      },
    });
  },
  getUnderwayContestList() {
    return ajax("contest_underway", "get");
  },
  getNotStartedContestList() {
    return ajax("contest_not_started", "get");
  },
  getContestHistoryList(offset, limit, searchParams) {
    let params = {
      offset,
      limit,
    };
    if (searchParams !== undefined) {
      Object.keys(searchParams).forEach((element) => {
        if (searchParams[element]) {
          params[element] = searchParams[element];
        }
      });
    }
    return ajax("contest_history", "get", {
      params,
    });
  },
  getContestList(offset, limit, searchParams) {
    let params = {
      offset,
      limit,
    };
    if (searchParams !== undefined) {
      Object.keys(searchParams).forEach((element) => {
        if (searchParams[element]) {
          params[element] = searchParams[element];
        }
      });
    }
    return ajax("contests", "get", {
      params,
    });
  },
  getContest(id) {
    return ajax("contest", "get", {
      params: {
        id,
      },
    });
  },
  getContestAccess(contestID) {
    return ajax("contest/access", "get", {
      params: {
        contest_id: contestID,
      },
    });
  },
  checkContestPassword(contestID, password) {
    return ajax("contest/password", "post", {
      data: {
        contest_id: contestID,
        password,
      },
    });
  },
  getContestAnnouncementList(contestId) {
    return ajax("contest/announcement", "get", {
      params: {
        contest_id: contestId,
      },
    });
  },
  getContestProblemList(contestId) {
    return ajax("contest/problem", "get", {
      params: {
        contest_id: contestId,
      },
    });
  },
  getContestProblem(problemID, contestID) {
    return ajax("contest/problem", "get", {
      params: {
        contest_id: contestID,
        problem_id: problemID,
      },
    });
  },
  submitCode(data) {
    return ajax("submission", "post", {
      data,
    });
  },
  getSubmissionList(offset, limit, params) {
    params.limit = limit;
    params.offset = offset;
    return ajax("submissions", "get", {
      params,
    });
  },
  getContestSubmissionList(offset, limit, params) {
    params.limit = limit;
    params.offset = offset;
    return ajax("contest_submissions", "get", {
      params,
    });
  },
  getSubmission(id) {
    return ajax("submission", "get", {
      params: {
        id,
      },
    });
  },
  submissionExists(problemID) {
    return ajax("submission_exists", "get", {
      params: {
        problem_id: problemID,
      },
    });
  },
  submissionRejudge(id) {
    return ajax("admin/submission/rejudge", "get", {
      params: {
        id,
      },
    });
  },
  updateSubmission(data) {
    return ajax("submission", "put", {
      data,
    });
  },
  getUserRank(offset, limit, rule = "ACM") {
    let params = {
      offset,
      limit,
      rule,
    };
    // return new Promise((resolve) => {
    //   setTimeout(() => {
    //     if (limit === 1) {
    //       resolve({data: {data: {results: [UserRankListProp.results[offset]], total: UserRankListProp.total}}})
    //     }
    //     resolve({data: {data: {results: UserRankListProp.results.slice(3, 13), total: UserRankListProp.total}}})
    //   }, 500)
    // });
    return ajax("user_rank", "get", {
      params,
    });
  },
  getSurgeUsers(offset, limit) {
    const params = {
      offset,
      limit,
    };
    // return new Promise((resolve) => {
    //   setTimeout(() => {
    //     resolve({data: {data: SurgeUserProps}})
    //   }, 500)
    // });
    return ajax("surge_user_rank", "get", {
      params,
    });
  },
  getMajorRankList(offset, limit) {
    const params = {
      offset,
      limit,
    };
    return ajax("major_rank", "get", { params });
  },
  getContestRank(params) {
    return ajax("contest_rank", "get", {
      params,
    });
  },
};

/**
 * @param url
 * @param method get|post|put|delete...
 * @param options // {params: {}, data: {}} // params for get, data for post
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
          // 若后端返回为登录，则为session失效，应退出当前登录用户
          if (res.data.data.startsWith("Please login")) {
            store.dispatch("changeModalStatus", {
              mode: "login",
              visible: true,
            });
          }
        } else {
          resolve(res);
          // if (method !== 'get') {
          //   Vue.prototype.$success('Succeeded')
          // }
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
