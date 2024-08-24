const ContestList = () => import("./ContestList.vue");
const ContestHistory = () => import("./ContestHistory.vue");
const ContestDetails = () => import("./ContestDetail.vue");
const ContestProblemList = () => import("./children/ContestProblemList.vue");
const ContestRank = () => import("./children/ContestRank.vue");
const SubmissionList = () => import("./children/SubmissionList.vue");
const Announcements = () => import("./children/Announcements.vue");
const Overview = () => import("./children/Overview.vue");

export {
  ContestDetails,
  ContestHistory,
  ContestList,
  ContestProblemList,
  ContestRank,
  SubmissionList,
  Announcements,
  Overview,
};
