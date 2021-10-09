import Vue from 'vue'
import rest from '../../api/rest'
import * as types from '../mutation-types'

// Contains basic store
const state = {
  token: null,
  user: '',
  isSuperuser: false,
  channel: '',
  loading: [],
  errors: [],
  loginSuccess: false,
  loginMessage: '',
  userMessages: [],
  conWorker: null,
  conRemote: null,
  permissions: [],
  showWelcome: true
}

const getters = {
  loginSuccess: state => state.loginSuccess,
  loginMessage: state => state.loginMessage,
  loading: state => state.loading.length > 0,
  error: state => state.errors.length > 0,
  errors: state => state.errors,
  token: state => state.token,
  user: state => state.user,
  isSuperuser: state => state.isSuperuser,
  channel: state => state.channel,
  userMessages: state => state.userMessages,
  conWorker: state => state.conWorker,
  conRemote: state => state.conRemote,
  permissions: state => state.permissions,
  showWelcome: state => state.showWelcome
}

const actions = {
  login ({commit, dispatch}, dat) {
    rest.login(dat)
      .then(response => {
        const token = response.data[0].key
        const username = dat.user
        const isSuperuser = response.data[0].is_superuser
        const channel = response.data[0].channel
        const permissions = response.data[0].permissions
        commit(types.LOGIN, { token, username, isSuperuser, channel, permissions })

        rest.setToken(token)

        dispatch('getAllProjects')
        if (permissions.includes('view_commits')) {
          dispatch('getAllVcs')
        }
        if (permissions.includes('view_issues')) {
          dispatch('getAllIssueSystems')
        }
        if (permissions.includes('view_messages')) {
          dispatch('getAllMailingLists')
        }
        if (permissions.includes('view_commits')) {
          dispatch('getAllVcsBranches')
        }
        if (permissions.includes('view_pull_requests')) {
          dispatch('getAllPullRequestSystems')
        }
      })
      .catch(error => {
        commit(types.LOGIN_ERROR, { error })
      })
  },
  sessionLogin ({commit, dispatch}, dat) {
    commit(types.SESSIONLOGIN, dat)
    rest.setToken(dat.token)
    dispatch('getAllProjects')
    if (dat.permissions.includes('view_commits')) {
      dispatch('getAllVcs')
    }
    if (dat.permissions.includes('view_issues')) {
      dispatch('getAllIssueSystems')
    }
    if (dat.permissions.includes('view_messages')) {
      dispatch('getAllMailingLists')
    }
    if (dat.permissions.includes('view_commits')) {
      dispatch('getAllVcsBranches')
    }
    if (dat.permissions.includes('view_pull_requests')) {
      dispatch('getAllPullRequestSystems')
    }
  },
  testConnectionWorker ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.testConnectionWorkerJob(dat)
      .then(() => {
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  testConnectionServershark ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.testConnectionServersharkJob(dat)
      .then(() => {
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  pushUserMessage ({commit}, message) {
    commit(types.PUSH_USER_MESSAGE, { message })
  },
  popUserMessage ({commit}, message) {
    commit(types.POP_USER_MESSAGE, { message })
  },
  logout ({commit}) {
    commit(types.LOGOUT)
  },
  pushLoading ({commit}) {
    commit(types.PUSH_LOADING)
  },
  popLoading ({commit}) {
    commit(types.POP_LOADING)
  },
  pushError ({commit}, error) {
    commit(types.PUSH_ERROR, { error })
  },
  popError ({commit}, id) {
    commit(types.POP_ERROR, { id })
  },
  setShowWelcome ({commit}, showWelcome) {
    commit(types.SET_WELCOME_MODAL, { showWelcome })
  },
}

const mutations = {
  [types.LOGIN] (state, { token, username, isSuperuser, channel, permissions }) {
    state.token = token
    state.user = username
    state.isSuperuser = isSuperuser
    state.channel = channel
    state.loginSuccess = true
    state.loginMessage = ''
    Vue.set(state, 'permissions', permissions)
  },
  [types.LOGOUT] (state) {
    state.loginSuccess = false
    state.loginMessage = ''
    state.token = null
    state.channel = ''
    state.isSuperuser = false
  },
  [types.SESSIONLOGIN] (state, { token, username, isSuperuser, channel, permissions }) {
    state.token = token
    state.user = username
    state.isSuperuser = isSuperuser
    state.channel = channel
    Vue.set(state, 'permissions', permissions)
  },
  [types.PUSH_LOADING] (state) {
    state.loading.push(true)
  },
  [types.POP_LOADING] (state) {
    state.loading.pop()
  },
  [types.LOGIN_ERROR] (state) {
    state.loginMessage = 'Login failed'
  },
  [types.PUSH_ERROR] (state, { error }) {
    // console.log('api error', error)
    let message = ''
    if (typeof error.response !== 'undefined') {
      message = error.response.statusText
    } else {
      message = error.message
    }
    const dat = {'message': message,
      'id': state.errors.length,
      'full_error': error}
    state.errors.push(dat)
  },
  [types.POP_ERROR] (state, { id }) {
    state.errors.splice(id, 1)
  },
  [types.PUSH_USER_MESSAGE] (state, { message }) {
    // todo: is there abetter way to do this?
    if (message.created === false && message.job_type === 'test_connection_servershark') {
      state.conRemote = message.success
    }
    if (message.created === false && message.job_type === 'test_connection_worker') {
      state.conWorker = message.success
    }

    // if everything is alright we can remove the job queued message
    if (message.created === false && message.success === true) {
      state.userMessages = state.userMessages.filter(item => item.job_id !== message.job_id)
    } else {
      state.userMessages.push(message)
    }
  },
  [types.SET_USER_MESSAGES] (state, { messages }) {
    state.userMessages = messages
  },
  [types.POP_USER_MESSAGE] (state, { message }) {
    state.userMessages = state.userMessages.filter(item => item !== message)
  },
  [types.SET_WELCOME_MODAL] (state, { showWelcome }) {
    state.showWelcome = showWelcome
  }
}

export default {
  state,
  getters,
  actions,
  mutations
}
