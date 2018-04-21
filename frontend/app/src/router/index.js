import Vue from 'vue'
import Router from 'vue-router'

import store from '../store'

// Containers
import Full from '@/containers/Full'

// Views
import Dashboard from '@/views/Dashboard'
import Commits from '@/views/Commits'
import Issues from '@/views/Issues'
import People from '@/views/People'
import Login from '@/views/Login'
import Files from '@/views/Files'
import Messages from '@/views/Messages'

import Analytics from '@/views/Analytics'
import CommitGraph from '@/views/CommitGraph'
import ProductInformation from '@/views/ProductInformation'
import Prediction from '@/views/Prediction'
import ReleaseFinder from '@/views/ReleaseFinder'
import TopicModel from '@/views/TopicModel'

import System from '@/views/System'
import Jobs from '@/views/Jobs'
import SystemInfo from '@/views/SystemInfo'

// import FileChanges from '@/views/FileChanges'

Vue.use(Router)

const router = new Router({
  mode: 'hash',
  linkActiveClass: 'open active',
  scrollBehavior: () => ({ y: 0 }),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
      name: 'Home',
      component: Full,
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: Dashboard
        },
        {
          path: 'issues',
          name: 'Issues',
          component: Issues,
          props: true,
          children: [
            {
              path: ':id',
              name: 'Issue'
            }
          ]
        },
        {
          path: 'commits',
          name: 'Commits',
          component: Commits,
          props: true,
          children: [
            {
              path: ':id',
              name: 'Commit'
            }
          ]
        },
        {
          path: 'people',
          name: 'People',
          component: People,
          props: true,
          children: [
            {
              path: ':id',
              name: 'Person'
            }
          ]
        },
        {
          path: 'messages',
          name: 'Messages',
          component: Messages,
          props: true,
          children: [
            {
              path: ':id',
              name: 'Message'
            }
          ]
        },
        {
          path: 'files',
          name: 'Files',
          component: Files,
          props: true
        },
        {
          path: 'analytics',
          name: 'Analytics',
          component: Analytics,
          props: true,
          children: [
            {
              path: 'cgraph',
              name: 'Commit Graph',
              component: CommitGraph
            },
            {
              path: 'productinformation',
              name: 'Product Information',
              component: ProductInformation
            },
            {
              path: 'prediction',
              name: 'Prediction',
              component: Prediction
            },
            {
              path: 'release',
              name: 'Release Finder',
              component: ReleaseFinder
            },
            {
              path: 'topicModels',
              name: 'TopicModels',
              props: true,
              component: TopicModel,
              children: [
                {
                  path: ':id',
                  name: 'TopicModel'
                }
              ]
            }
          ]
        },
        {
          path: 'system',
          name: 'System',
          component: System,
          props: true,
          children: [
            {
              path: 'jobs',
              name: 'Jobs',
              component: Jobs,
              props: true,
              children: [
                {
                  path: ':id',
                  name: 'Job'
                }
              ]
            },
            {
              path: 'info',
              name: 'Info',
              component: SystemInfo,
              props: true
            }
          ]
        }
      ]
    },
    {
      path: '/login',
      component: Login
    },
    {
      path: '/logout',
      component: Login,
      props: {logout: true}
    }
  ]
})

router.beforeEach((to, from, next) => {
  let a = store.getters.token
  // console.log('toknav', a)
  // login is always possible
  if (to.path === '/login') {
    next()
  }

  // everything else needs a valid token
  if (typeof a !== 'undefined' && a !== false && a !== null && a !== 'null' && a !== '') {
    next()
  } else {
    next('/login')
  }
})

export default router
