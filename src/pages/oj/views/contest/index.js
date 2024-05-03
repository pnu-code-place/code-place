const ContestList = () => import(/* webpackChunkName: "contest" */ './ContestList.vue')
const ContestDetails = () => import(/* webpackChunkName: "contest" */ './ContestDetail.vue')
const ContestProblemList = () => import(/* webpackChunkName: "contest" */ './children/ContestProblemList.vue')
const ContestRank = () => import(/* webpackChunkName: "contest" */ './children/ContestRank.vue')
const SubmissionList = () => import(/* webpackChunkName: "submission" */ './children/SubmissionList.vue')
const Announcements = () => import(/* webpackChunkName: "submission" */ './children/Announcements.vue')
const Overview = () => import(/* webpackChunkName: "submission" */ './children/Overview.vue')

export {ContestDetails, ContestList, ContestProblemList, ContestRank, SubmissionList, Announcements, Overview}
