// all routes here.
import {
  About,
  ACMRank,
  ApplyResetPassword,
  FAQ,
  Home,
  Logout,
  NotFound,
  OIRank,
  Problem,
  ProblemList,
  ResetPassword,
  SubmissionDetails,
  SubmissionList,
  UserHome
} from '../views'

import * as Contest from '@oj/views/contest'
import * as Setting from '@oj/views/setting'
import Notice from "../views/notice/Notice.vue"
import DashboardSection from "../views/user/userhome/sections/dashboardSection/DashboardSection.vue";
import ProblemSection from "../views/user/userhome/sections/problemSection/ProblemSection.vue";
import communitySection from "../views/user/userhome/sections/communitySection/CommunitySection.vue";
import AchievementSection from "../views/user/userhome/sections/achievementSection/AchievementSection.vue";
import SoaringRank from "../views/rank/SurgeRank.vue";
import MajorRank from "../views/rank/majorRank/MajorRank.vue";
import UserRank from "../views/rank/UserRank.vue";

export default [
  {
    name: 'home',
    path: '/',
    meta: {title: 'Home'},
    component: Home
  },
  {
    name: 'notice',
    path: '/notice',
    meta: {title: 'notice'},
    component: Notice
  },
  {
    name: 'logout',
    path: '/logout',
    meta: {title: 'Logout'},
    component: Logout
  },
  {
    name: 'apply-reset-password',
    path: '/apply-reset-password',
    meta: {title: 'Apply Reset Password'},
    component: ApplyResetPassword
  },
  {
    name: 'reset-password',
    path: '/reset-password/:token',
    meta: {title: 'Reset Password'},
    component: ResetPassword
  },
  {
    name: 'problem-list',
    path: '/problem',
    meta: {title: 'Problem List'},
    component: ProblemList
  },
  {
    name: 'problem-details',
    path: '/problem/:problemID',
    meta: {title: 'Problem Details'},
    component: Problem
  },
  {
    name: 'submission-list',
    path: '/status',
    meta: {title: 'Submission List'},
    component: SubmissionList
  },
  {
    name: 'submission-details',
    path: '/status/:id/',
    meta: {title: 'Submission Details'},
    component: SubmissionDetails
  },
  {
    name: 'contest-list',
    path: '/contest',
    meta: {title: 'Contest List'},
    component: Contest.ContestList
  },
  {
    name: 'contest-details',
    path: '/contest/:contestID',
    component: Contest.ContestDetails,
    meta: {title: 'Contest Details'},
    children: [
      {
        name: 'contest-overview',
        path: 'overview',
        component: Contest.Overview
      },
      {
        name: 'contest-submission-list',
        path: 'submissions',
        component: Contest.SubmissionList
      },
      {
        name: 'contest-problem-list',
        path: 'problems',
        component: Contest.ContestProblemList
      },
      {
        name: 'contest-problem-details',
        path: 'problem/:problemID/',
        component: Problem
      },
      {
        name: 'contest-announcement-list',
        path: 'announcements',
        component: Contest.Announcements
      },
      {
        name: 'contest-rank',
        path: 'rank',
        component: Contest.ContestRank
      },
    ]
  },
  {
    name: 'acm-rank',
    path: '/acm-rank',
    redirect: {name: 'user-rank'},
    meta: {title: 'ACM Rankings'},
    component: ACMRank,
    children: [
      {
        name: 'user-rank',
        path: 'user-rank',
        meta: {title: 'User Rank'},
        component : UserRank
      },
      {
        name: 'surge-rank',
        path: 'surge-rank',
        meta: {title: 'Surge-Rank'},
        component : SoaringRank
      },
      {
        name: 'major-rank',
        path: 'major-rank',
        meta: {title: 'Major Rank'},
        component : MajorRank
      }
    ]
  },
  {
    name: 'oi-rank',
    path: '/oi-rank',
    meta: {title: 'OI Rankings'},
    component: OIRank
  },
  {
    path: '/user-home',
    name: 'user-home',
    redirect: {name: 'user-dashboard'},
    component: UserHome,
    meta: {title: 'User Home'},
    children: [
      {
        name: 'user-dashboard',
        path: 'dashboard/:username?',
        component: DashboardSection,
        meta: {title: 'Main'}
      },
      {
        name: 'user-problems',
        path: 'problems/:username?',
        component: ProblemSection,
        meta: {title: 'User Problems'}
      },
      {
        name: 'user-community',
        path: 'community/:username?',
        component: communitySection,
        meta: {title: 'Community'},
      },
      {
        name: 'user-achievements',
        path: 'achievements/:username?',
        props: true,
        component: AchievementSection,
        meta: {title: 'Challenges'},
      }
    ]
  },
  {
    path: '/setting',
    component: Setting.Settings,
    redirect: {name: 'profile-setting'},
    children: [
      {
        name: 'default-setting',
        path: '',
        meta: {requiresAuth: true, title: 'Default Settings'},
        component: Setting.ProfileSetting
      },
      {
        name: 'profile-setting',
        path: 'profile',
        meta: {requiresAuth: true, title: 'Profile Settings'},
        component: Setting.ProfileSetting
      },
      {
        name: 'account-setting',
        path: 'account',
        meta: {requiresAuth: true, title: 'Account Settings'},
        component: Setting.AccountSetting
      },
      {
        name: 'security-setting',
        path: 'security',
        meta: {requiresAuth: true, title: 'Security Settings'},
        component: Setting.SecuritySetting
      }
    ]
  },
  {
    path: '/about',
    name: 'about',
    meta: {title: 'About'},
    component: About
  },
  {
    path: '/faq',
    name: 'faq',
    meta: {title: 'FAQ'},
    component: FAQ
  },
  {
    path: '*',
    meta: {title: '404'},
    component: NotFound
  }
]
