import Vue from "vue"
import store from "@/store"
import axios from "axios"

Vue.prototype.$http = axios
axios.defaults.baseURL = "/api"
axios.defaults.xsrfHeaderName = "X-CSRFToken"
axios.defaults.xsrfCookieName = "csrftoken"

export default {
  getPopup() {
    return ajax("popup", "get")
  },
  getStatistics() {
    return ajax("home_statistics", "get")
  },
  getWebsiteConf(params) {
    return ajax("website", "get", {
      params,
    })
  },
  getAnnouncementList(offset, limit) {
    let params = {
      offset: offset,
      limit: limit,
    }
    return ajax("announcement", "get", {
      params,
    })
  },
  getSWCenterList() {
    return ajax("sw_center_notice", "get")
  },
  login(data) {
    return ajax("login", "post", {
      data,
    })
  },
  checkUsernameOrEmail(username, email) {
    return ajax("check_username_or_email", "post", {
      data: {
        username,
        email,
      },
    })
  },
  applyUserEmailValidCheck(email) {
    return ajax("apply_user_email_valid_check", "post", {
      data: {
        email,
      },
    })
  },
  nicknameValidCheck(nickname) {
    return ajax("nickname_valid_check", "get", {
      params: {
        nickname: nickname,
      },
    })
  },
  userEmailValidCheck(email, code) {
    console.log("applyUserEmailValidCheck email: ", email, code)
    return ajax("user_email_valid_check", "post", {
      data: {
        email,
        code,
      },
    })
  },
  getCollegeList() {
    return ajax("college_list", "get")
  },
  getMajorList(collegeID) {
    return ajax("department_list", "get", {
      params: {
        college_id: collegeID,
      },
    })
  },
  // 注册
  register(data) {
    return ajax("register", "post", {
      data,
    })
  },
  logout() {
    return ajax("logout", "get")
  },
  getCaptcha() {
    return ajax("captcha", "get")
  },
  getUserInfo(username = undefined) {
    return ajax("profile", "get", {
      params: {
        username,
      },
    })
  },
  getDashboardInfo(username) {
    return ajax("profile/dashboard", "get", {
      params: {
        username,
      },
    })
  },
  getUserProblemInfo(username, query) {
    return ajax("profile/problem", "get", {
      params: {
        username,
        ...query,
      },
    })
  },
  getPersonalRecommendProblem() {
    return ajax("recommend_problem", "get")
  },

  updateProfile(profile) {
    return ajax("profile", "put", {
      data: profile,
    })
  },
  getHomeRealTimeRanking() {
    return ajax("home_ranking", "get")
  },
  getHomeBonusProblem() {
    return ajax("problem/bonus", "get")
  },
  getMostDifficultProblem() {
    return ajax("problem/most_difficult_problem", "get")
  },
  freshDisplayID(userID) {
    return ajax("profile/fresh_display_id", "get", {
      params: {
        user_id: userID,
      },
    })
  },
  twoFactorAuth(method, data) {
    return ajax("two_factor_auth", method, {
      data,
    })
  },
  tfaRequiredCheck(email) {
    return ajax("tfa_required", "post", {
      data: {
        email,
      },
    })
  },
  getSessions() {
    return ajax("sessions", "get")
  },
  deleteSession(sessionKey) {
    return ajax("sessions", "delete", {
      params: {
        session_key: sessionKey,
      },
    })
  },
  applyResetPassword(data) {
    return ajax("apply_reset_password", "post", {
      data,
    })
  },
  resetPassword(data) {
    return ajax("reset_password", "post", {
      data,
    })
  },
  changePassword(data) {
    return ajax("change_password", "post", {
      data,
    })
  },
  changeEmail(data) {
    return ajax("change_email", "post", {
      data,
    })
  },
  getLanguages() {
    return ajax("languages", "get")
  },
  getProblemTagList() {
    return ajax("problem/tags", "get")
  },
  getProblemList(offset, limit, searchParams) {
    let params = {
      paging: true,
      offset,
      limit,
    }
    Object.keys(searchParams).forEach((element) => {
      if (searchParams[element]) {
        params[element] = searchParams[element]
      }
    })
    return ajax("problem", "get", {
      params: params,
    })
  },
  pickone() {
    return ajax("pickone", "get")
  },
  getProblem(problemID) {
    return ajax("problem", "get", {
      params: {
        problem_id: problemID,
      },
    })
  },
  getContestList(offset, limit, searchParams) {
    let params = {
      offset,
      limit,
    }
    if (searchParams !== undefined) {
      Object.keys(searchParams).forEach((element) => {
        if (searchParams[element]) {
          params[element] = searchParams[element]
        }
      })
    }
    return ajax("contests", "get", {
      params,
    })
  },
  getUnderwayContestList(searchParams) {
    let params = {}
    if (searchParams !== undefined) {
      Object.keys(searchParams).forEach((element) => {
        if (searchParams[element]) {
          params[element] = searchParams[element]
        }
      })
    }
    return ajax("contest_underway", "get", { params })
  },
  getNotStartedContestList() {
    return ajax("contest_not_started", "get")
  },
  getContestHistoryList(offset, limit, searchParams) {
    let params = {
      offset,
      limit,
    }
    if (searchParams !== undefined) {
      Object.keys(searchParams).forEach((element) => {
        if (searchParams[element]) {
          params[element] = searchParams[element]
        }
      })
    }
    return ajax("contest_history", "get", {
      params,
    })
  },
  getContest(id) {
    return ajax("contest", "get", {
      params: {
        id,
      },
    })
  },
  getContestAccess(contestID) {
    return ajax("contest/access", "get", {
      params: {
        contest_id: contestID,
      },
    })
  },
  checkContestPassword(contestID, password) {
    return ajax("contest/password", "post", {
      data: {
        contest_id: contestID,
        password,
      },
    })
  },
  getContestAnnouncementList(contestId) {
    return ajax("contest/announcement", "get", {
      params: {
        contest_id: contestId,
      },
    })
  },
  getAnnouncement(announcementId) {
    return ajax("announcement", "get", {
      params: {
        id: announcementId,
      },
    })
  },
  getContestProblemList(contestId, query) {
    const params = { contest_id: contestId }
    if (query) params.query = query
    return ajax("contest/problem", "get", {
      params: params,
    })
  },
  getContestProblem(problemID, contestID) {
    return ajax("contest/problem", "get", {
      params: {
        contest_id: contestID,
        problem_id: problemID,
      },
    })
  },
  submitCode(data) {
    return ajax("submission", "post", {
      data,
    })
  },
  getSubmissionList(offset, limit, params) {
    params.limit = limit
    params.offset = offset
    return ajax("submissions", "get", {
      params,
    })
  },
  getSubmission(id) {
    return ajax("submission", "get", {
      params: {
        id,
      },
    })
  },
  getSubmissionRank(id) {
    const params = { submission_id: id }
    return ajax("submission_rank", "get", {
      params: params,
    })
  },
  submissionExists(problemID) {
    return ajax("submission_exists", "get", {
      params: {
        problem_id: problemID,
      },
    })
  },
  submissionRejudge(id) {
    return ajax("admin/submission/rejudge", "get", {
      params: {
        id,
      },
    })
  },
  updateSubmission(data) {
    return ajax("submission", "put", {
      data,
    })
  },
  getUserRank(offset, limit, rule = "ACM") {
    let params = {
      offset,
      limit,
      rule,
    }
    return ajax("user_rank", "get", {
      params,
    })
  },
  getSurgeUsers(offset, limit) {
    const params = {
      offset,
      limit,
    }
    return ajax("surge_user_rank", "get", {
      params,
    })
  },
  getMajorRankList(offset, limit) {
    const params = {
      offset,
      limit,
    }
    return ajax("major_rank", "get", { params })
  },
  getContestRank(params) {
    return ajax("contest_rank", "get", {
      params,
    })
  },
  getBanners() {
    return ajax("banner", "get")
  },

  getCommunityPostList(offset, limit) {
    const params = {
      offset,
      limit,
    }

    return ajax("community/posts", "get", {
      params,
    })
  },

  getCommunityPostDetail(postId) {
    /*
     {
        "error": null,
        "data": {
            "id": 6,
            "title": "일반 게시글 2번입니다.",
            "content": "취업이 고민입니다... 저는 어떤 회사에 갈 수 있을까요? 선배님들의 조언이 궁금합니다.",
            "author": 1,
            "author_name": "root",
            "author_avatar": "/public/avatar/default.png",
            "community_type": "GENERAL",
            "post_type": "ARTICLE",
            "question_status": null,
            "created_at": "2025-10-13T13:05:19.570215+09:00",
            "updated_at": "2025-10-13T13:05:19.570239+09:00",
            "problem": null,
            "contest": null,
            "comments": [
                {
                    "id": 1,
                    "post": 6,
                    "author": 1,
                    "author_name": "root",
                    "author_avatar": "/public/avatar/default.png",
                    "content": "일반 게시글 2번에 대한 질문이 있습니다",
                    "parent_comment": null,
                    "created_at": "2025-10-16T15:06:08.192757+09:00",
                    "updated_at": "2025-10-16T15:06:08.192811+09:00",
                    "replies": [
                        {
                            "id": 2,
                            "author": 1,
                            "author_name": "root",
                            "author_avatar": "/public/avatar/default.png",
                            "content": "일반 게시글 2번에 대한 질문에 대한 댓글입니다.",
                            "parent_comment": 1,
                            "created_at": "2025-10-16T15:07:04.941115+09:00",
                            "updated_at": "2025-10-16T15:07:04.941122+09:00"
                        }
                    ]
                }
            ]
        }
    }
     */
    return ajax(`community/posts/${postId}`, "get")
  },
}

/**
 * @param url
 * @param method get|post|put|delete...
 * @param options // {params: {}, data: {}} // params for get, data for post
 * @returns {Promise}
 */
function ajax(url, method, options) {
  if (options !== undefined) {
    var { params = {}, data = {} } = options
  } else {
    params = data = {}
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
          Vue.prototype.$error(res.data.data)
          reject(res)
          // 若后端返回为登录，则为session失效，应退出当前登录用户
          if (res.data.data.startsWith("Please login")) {
            store.dispatch("changeModalStatus", {
              mode: "login",
              visible: true,
            })
          }
        } else {
          resolve(res)
          // if (method !== 'get') {
          //   Vue.prototype.$success('Succeeded')
          // }
        }
      },
      (res) => {
        // API请求异常，一般为Server error 或 network error
        reject(res)
        Vue.prototype.$error(res.data.data)
      },
    )
  })
}
