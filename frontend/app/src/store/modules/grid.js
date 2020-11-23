import rest from '../../api/rest'
import * as types from '../mutation-types'

// todo: there HAS to be a way to remove all this boilerplate code
const state = {
  gridCommits: {data: [], count: 0},
  gridFileActions: {data: [], count: 0},
  gridCodeEntityStates: {data: [], count: 0},
  gridTags: {data: [], count: 0},
  gridIssues: {data: [], count: 0},
  gridMessages: {data: [], count: 0},
  gridPeople: {data: [], count: 0},
  gridFiles: {data: [], count: 0},
  gridFileChanges: {data: [], count: 0},
  gridHunks: {data: [], count: 0},
  gridHotspots: {data: [], count: 0},
  gridFileHistory: {data: [], count: 0},
  gridDefectLinks: {data: [], count: 0},
  gridReleases: {data: [], count: 0},
  gridJobs: {data: [], count: 0},
  gridCorrections: {data: [], count: 0},
}

const getters = {
  gridIssues: state => state.gridIssues,
  gridPeople: state => state.gridPeople,
  gridMessages: state => state.gridMessages,
  gridCommits: state => state.gridCommits,
  gridTags: state => state.gridTags,
  gridFiles: state => state.gridFiles,
  gridHotspots: state => state.gridHotspots,
  gridFileActions: state => state.gridFileActions,
  gridHunks: state => state.gridHunks,
  gridCodeEntityStates: state => state.gridCodeEntityStates,
  gridFileChanges: state => state.gridFileChanges,
  gridFileHistory: state => state.gridFileHistory,
  gridDefectLinks: state => state.gridDefectLinks,
  gridReleases: state => state.gridReleases,
  gridJobs: state => state.gridJobs,
  gridCorrections: state => state.gridCorrections
}

const actions = {
  updateGridHunks ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getHunks(dat)
      .then(response => {
        commit(types.GRID_HUNKS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridCommits ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getCommits(dat)
      .then(response => {
        commit(types.GRID_COMMITS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridReleases ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getReleases(dat)
      .then(response => {
        commit(types.GRID_RELEASES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridJobs ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getJobs(dat)
      .then(response => {
        commit(types.GRID_JOBS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridFileActions ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getFileActions(dat)
      .then(response => {
        commit(types.GRID_FILE_ACTIONS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridCodeEntityStates ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getCodeEntityStates(dat)
      .then(response => {
        commit(types.GRID_CODE_ENTITY_STATES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridTags ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getTags(dat)
      .then(response => {
        commit(types.GRID_TAGS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridIssues ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getIssues(dat)
      .then(response => {
        commit(types.GRID_ISSUES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridPeople ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getPeople(dat)
      .then(response => {
        commit(types.GRID_PEOPLE, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridFiles ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getFiles(dat)
      .then(response => {
        commit(types.GRID_FILES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridMessages ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getMessages(dat)
      .then(response => {
        commit(types.GRID_MESSAGES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridFileChanges ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getFileChanges(dat)
      .then(response => {
        commit(types.GRID_FILE_CHANGES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridFileHistory ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getFileHistory(dat)
      .then(response => {
        commit(types.GRID_FILE_HISTORY, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateGridDefectLinks ({commit}, dat) {
    commit(types.PUSH_LOADING)
    commit(types.GRID_DEFECT_LINKS, { response: {data: {}} })
    rest.getDefectLinks(dat)
      .then(response => {
        commit(types.GRID_DEFECT_LINKS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateDashboardStats ({commit}) {
    commit(types.PUSH_LOADING)
    rest.getStats()
      .then(response => {
        commit(types.SET_DASHBOARD_STATS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  updateDashboardStatsHistory ({commit}) {
    commit(types.PUSH_LOADING)
    rest.getStatsHistory()
      .then(response => {
        commit(types.SET_DASHBOARD_STATS_HISTORY, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  clearGridHunks ({commit}) {
    commit(types.CLEAR_GRID_HUNKS)
  },
  clearGridFileActions ({commit}) {
    commit(types.CLEAR_GRID_FILE_ACTIONS)
  },
  updateGridCorrections ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getCorrections(dat)
      .then(response => {
        commit(types.GRID_CORRECTIONS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  }
}

const mutations = {
  [types.CLEAR_GRID_HUNKS] (state) {
    state.gridHunks = {data: [], count: 0}
  },
  [types.CLEAR_GRID_FILE_ACTIONS] (state) {
    state.gridFileActions = {data: [], count: 0}
  },
  [types.GRID_HUNKS] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridHunks = {data: response.data, count: response.data.length}
    } else {
      state.gridHunks = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_COMMITS] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridCommits = {data: response.data, count: response.data.length}
    } else {
      state.gridCommits = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_RELEASES] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridReleases = {data: response.data, count: response.data.length}
    } else {
      state.gridReleases = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_FILE_ACTIONS] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridFileActions = {data: response.data, count: response.data.length}
    } else {
      state.gridFileActions = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_CODE_ENTITY_STATES] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridCodeEntityStates = {data: response.data, count: response.data.length}
    } else {
      state.gridCodeEntityStates = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_TAGS] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridTags = {data: response.data, count: response.data.length}
    } else {
      state.gridTags = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_PEOPLE] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridPeople = {data: response.data, count: response.data.length}
    } else {
      state.gridPeople = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_MESSAGES] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridMessages = {data: response.data, count: response.data.length}
    } else {
      state.gridMessages = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_ISSUES] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridIssues = {data: response.data, count: response.data.length}
    } else {
      state.gridIssues = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_MESSAGES] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridMessages = {data: response.data, count: response.data.length}
    } else {
      state.gridMessages = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_FILES] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridFiles = {data: response.data, count: response.data.length}
    } else {
      state.gridFiles = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_FILE_CHANGES] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridFileChanges = {data: response.data, count: response.data.length}
    } else {
      state.gridFileChanges = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_FILE_HISTORY] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridFileHistory = {data: response.data, count: response.data.length}
    } else {
      state.gridFileHistory = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_DEFECT_LINKS] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridDefectLinks = {data: response.data, count: response.data.length}
    } else {
      state.gridDefectLinks = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_JOBS] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridJobs = {data: response.data, count: response.data.length}
    } else {
      state.gridJobs = {data: response.data.results, count: response.data.count}
    }
  },
  [types.GRID_CORRECTIONS] (state, { response }) {
    if (typeof response.data.results === 'undefined') {
      state.gridCorrections = {data: response.data, count: response.data.length}
    } else {
      state.gridCorrections = {data: response.data.results, count: response.data.count}
    }
  }
}

export default {
  state,
  getters,
  actions,
  mutations
}
