import Vue from "vue";
import VueRouter from "vue-router";
// 引入 view 组件
import {
  Announcement,
  Conf,
  Contest,
  ContestList,
  ContestSubmission,
  Home,
  JudgeServer,
  Login,
  Problem,
  ProblemList,
  User,
  PruneTestCase,
  HomeBannerManagement,
  Dashboard,
  ProblemImportOrExport,
  AdminCatalog,
  PopupManagement,
} from "./views";
Vue.use(VueRouter);

export default new VueRouter({
  mode: "history",
  base: "/admin/",
  scrollBehavior: () => ({ y: 0 }),
  routes: [
    {
      path: "/login",
      name: "login",
      component: Login,
    },
    {
      path: "/",
      component: Home,
      children: [
        {
          path: "",
          name: "dashboard",
          component: Dashboard,
        },
        {
          path: "/announcement",
          name: "announcement",
          component: Announcement,
        },
        {
          path: "/user",
          name: "user",
          component: User,
        },
        {
          path: "/admin-catalog",
          name: "admin-catalog",
          component: AdminCatalog,
        },
        {
          path: "/conf",
          name: "conf",
          component: Conf,
        },
        {
          path: "/judge-server",
          name: "judge-server",
          component: JudgeServer,
        },
        {
          path: "/prune-test-case",
          name: "prune-test-case",
          component: PruneTestCase,
        },
        {
          path: "/home-banner-management",
          name: "home-banner-management",
          component: HomeBannerManagement,
        },
        {
          path: "/popup-management",
          name: "popup-management",
          component: PopupManagement,
        },
        {
          path: "/problems",
          name: "problem-list",
          component: ProblemList,
        },
        {
          path: "/problem/create",
          name: "create-problem",
          component: Problem,
        },
        {
          path: "/problem/edit/:problemId",
          name: "edit-problem",
          component: Problem,
        },
        {
          path: "/problem/batch_ops",
          name: "problem_batch_ops",
          component: ProblemImportOrExport,
        },
        {
          path: "/contest/create",
          name: "create-contest",
          component: Contest,
        },
        {
          path: "/contest",
          name: "contest-list",
          component: ContestList,
        },
        {
          path: "/contest/:contestId/submission",
          name: "contest-submission",
          component: ContestSubmission,
        },
        {
          path: "/contest/:contestId/edit",
          name: "edit-contest",
          component: Contest,
        },
        {
          path: "/contest/:contestId/announcement",
          name: "contest-announcement",
          component: Announcement,
        },
        {
          path: "/contest/:contestId/problems",
          name: "contest-problem-list",
          component: ProblemList,
        },
        {
          path: "/contest/:contestId/problem/create",
          name: "create-contest-problem",
          component: Problem,
        },
        {
          path: "/contest/:contestId/problem/:problemId/edit",
          name: "edit-contest-problem",
          component: Problem,
        },
      ],
    },
    {
      path: "*",
      redirect: "/login",
    },
  ],
});
