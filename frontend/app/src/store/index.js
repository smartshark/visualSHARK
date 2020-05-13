import Vue from 'vue'
import Vuex from 'vuex'
import projects from './modules/projects'
import base from './modules/base'
import grid from './modules/grid'

import l from '../api/local'

Vue.use(Vuex)

const persist = (store) => {
  let token = l.getSession('ab')
  const username = l.getLocal('cd')
  const isSuperuser = l.getLocal('superuser') === 'true'
  const channel = l.getLocal('re')
  const permissions = l.getLocal('permissions')

  const projects = l.getLocal('projects')
  const vcs = l.getLocal('vcs')
  const is = l.getLocal('is')
  const ml = l.getLocal('ml')
  const currentProject = l.getLocal('currentProject')
  const currentVcs = l.getLocal('currentVcs')
  const currentIts = l.getLocal('currentIts')
  const currentMl = l.getLocal('currentMl')

  const sw = l.getLocal('showWelcome')

  let msgs = l.getLocal('userMessages')
  if (typeof msgs === 'undefined' || msgs === null) {
    msgs = []
  }

  // if we have lost our session we also need to reset everything
  // otherwise we would be in an inconsistent state with some information in the local store and
  // missing information in a clean vuex store
  if (typeof token === 'undefined' || token === null) {
    store.commit('LOGOUT')
  }

  // if we have an active session but empty local store, we clear the token to perform a new login
  if (typeof token !== 'undefined' && token !== null && store.getters.token === null && permissions === null) {
    token = null
    store.dispatch('logout')
  }

  // we have an active session but an empty store
  if (typeof token !== 'undefined' && token !== null && store.getters.token === null) {
    l.removeLocal('projects')
    l.removeLocal('vcs')
    l.removeLocal('is')
    l.removeLocal('ml')
    //l.removeLocal('currentProject')
    //l.removeLocal('currentVcs')
    //l.removeLocal('currentIts')
    //l.removeLocal('currentMl')
    store.dispatch('sessionLogin', {token, username, isSuperuser, channel, permissions})
  }

  if (typeof msgs !== 'undefined' && msgs !== null) {
    try {
      msgs = JSON.parse(msgs) // otherwise it will be an object list
      let tmp = []
      msgs.forEach(item => {
        tmp.push(item)
      })
      store.commit('SET_USER_MESSAGES', { messages: tmp })
      // console.log('setting user messages from persist', tmp)
    } catch (e) {
      msgs = []
      // console.log('error loading user messages from persist', e)
    }
  }
  if (typeof projects !== 'undefined' && projects !== null) {
    try {
      let response = {
        data: {
          results: JSON.parse(projects)
        }
      }
      // console.log('setting projects from persist', response)
      store.commit('RECEIVE_PROJECTS', { response })
    } catch (e) {
      console.log(e)
    }
  }
  if (typeof vcs !== 'undefined' && vcs !== null) {
    try {
      let response = {
        data: {
          results: JSON.parse(vcs)
        }
      }
      // console.log('setting vcs from persist', response)
      store.commit('RECEIVE_VCS', { response })
    } catch (e) {
      console.log(e)
    }
  }
  if (typeof is !== 'undefined' && is !== null) {
    try {
      let response = {
        data: {
          results: JSON.parse(is)
        }
      }
      // console.log('setting is from persist', response)
      store.commit('RECEIVE_IS', { response })
    } catch (e) {
      console.log(e)
    }
  }
  if (typeof ml !== 'undefined' && ml !== null) {
    try {
      let response = {
        data: {
          results: JSON.parse(ml)
        }
      }
      // console.log('setting ml from persist', response)
      store.commit('RECEIVE_ML', { response })
    } catch (e) {
      console.log(e)
    }
  }
  if (typeof currentProject !== 'undefined' && currentProject !== null) {
    try {
      let project = JSON.parse(currentProject)
      // console.log('setting currentProject from persist', project)
      store.commit('SET_PROJECT', { project })
    } catch (e) {
      console.log(e)
    }
  }
  if (typeof currentVcs !== 'undefined' && currentVcs !== null) {
    try {
      let vcs = JSON.parse(currentVcs)
      // console.log('setting currentVcs from persist', vcs)
      store.commit('SET_VCS', { vcs })
    } catch (e) {
      console.log(e)
    }
  }
  if (typeof currentIts !== 'undefined' && currentIts !== null) {
    try {
      let its = JSON.parse(currentIts)
      // console.log('setting currentIts from persist', its)
      store.commit('SET_ITS', { its })
    } catch (e) {
      console.log(e)
    }
  }
  if (typeof currentMl !== 'undefined' && currentMl !== null) {
    try {
      let ml = JSON.parse(currentMl)
      // console.log('setting currentMl from persist', ml)
      store.commit('SET_ML', { ml })
    } catch (e) {
      console.log(e)
    }
  }
  if (typeof sw !== 'undefined' && sw !== null) {
    try {
      let showWelcome = JSON.parse(sw)
      // console.log('setting currentMl from persist', ml)
      store.commit('SET_WELCOME_MODAL', { showWelcome })
    } catch (e) {
      console.log(e)
    }
  }
  store.subscribe((mutation, state) => {
    const type = mutation.type
    if (type === 'SESSIONLOGIN') {
      Vue.discoChannel()
      Vue.connectChannel()
    }
    if (type === 'LOGIN') {
      // console.log('initial login', mutation.payload.token, mutation.payload.username)
      l.setSession('ab', mutation.payload.token)
      l.setLocal('cd', mutation.payload.username)
      l.setLocal('superuser', mutation.payload.isSuperuser)
      l.setLocal('re', mutation.payload.channel)
      l.setLocal('permissions', mutation.payload.permissions)
      // connect websocket after login
      Vue.connectChannel()
    }
    if (type === 'LOGOUT') {
      l.setSession('ab', null)
      l.removeLocal('cd')
      l.removeLocal('is')
      l.removeLocal('re')
      l.removeLocal('permissions')
      l.removeLocal('superuser')

      l.removeLocal('projects')
      l.removeLocal('vcs')
      l.removeLocal('is')
      l.removeLocal('ml')
      l.removeLocal('currentProject')
      l.removeLocal('currentVcs')
      l.removeLocal('currentIts')
      l.removeLocal('currentMl')

      // clearing vuex store
      // TODO!

      // disconnect websocket after logout
      Vue.discoChannel()

      // clear user messages on logout
      l.setLocal('userMessages', JSON.stringify([]))
    }
    if (type === 'PUSH_USER_MESSAGE') {
      // console.log('adding to user messages in persistent store')
      msgs.push(mutation.payload.message)
      l.setLocal('userMessages', JSON.stringify(msgs))
    }
    if (type === 'POP_USER_MESSAGE') {
      // let msgs = JSON.parse(l.getLocal('userMessages'))
      msgs = msgs.filter(item => item !== mutation.payload.message)
      // console.log('setting after pop', msgs)
      l.setLocal('userMessages', JSON.stringify(msgs))
    }
    // persist other data that is loaded on login
    if (type === 'RECEIVE_PROJECTS') {
      // console.log('updating persistent store with projects', mutation.payload.response)
      l.setLocal('projects', JSON.stringify(mutation.payload.response.data.results))
    }
    if (type === 'RECEIVE_VCS') {
      // console.log('updating persistent store with vcs', mutation.payload.response)
      l.setLocal('vcs', JSON.stringify(mutation.payload.response.data.results))
    }
    if (type === 'RECEIVE_IS') {
      // console.log('updating persistent store with is', mutation.payload.response)
      l.setLocal('is', JSON.stringify(mutation.payload.response.data.results))
    }
    if (type === 'RECEIVE_ML') {
      // console.log('updating persistent store with ml', mutation.payload.response)
      l.setLocal('ml', JSON.stringify(mutation.payload.response.data.results))
    }
    if (type === 'SET_PROJECT') {
      // console.log('updating persistent store with current Project', mutation.payload.project)
      l.setLocal('currentProject', JSON.stringify(mutation.payload.project))
    }
    if (type === 'SET_VCS') {
      // console.log('updating persistent store with current VCS', mutation.payload.vcs)
      l.setLocal('currentVcs', JSON.stringify(mutation.payload.vcs))
    }
    if (type === 'SET_ITS') {
      // console.log('updating persistent store with current ITS', mutation.payload.its)
      l.setLocal('currentIts', JSON.stringify(mutation.payload.its))
    }
    if (type === 'SET_ML') {
      // console.log('updating persistent store with current ML', mutation.payload.ml)
      l.setLocal('currentMl', JSON.stringify(mutation.payload.ml))
    }
    if (type === 'SET_WELCOME_MODAL') {
      // console.log('updating persistent store with current ML', mutation.payload.ml)
      l.setLocal('showWelcome', JSON.stringify(mutation.payload.showWelcome))
    }
  })
}

export default new Vuex.Store({
  modules: {
    base,
    projects,
    grid
  },
  strict: true,
  plugins: [persist]
})
