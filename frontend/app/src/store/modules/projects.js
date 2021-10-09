import rest from '../../api/rest'
import * as types from '../mutation-types'

// initial
const state = {
  projects: [],
  currentProject: null,
  currentVcs: null,
  currentIts: null,
  currentMl: null,
  currentPrs: null,
  currentJob: null,
  vcs: [],
  its: [],
  ml: [],
  prs: [],
  allVcsBranches: [],
  currentVcsBranches: [],
  dashboardStats: {num_projects: 0, num_commits: 0, num_issues: 0, num_emails: 0, num_files: 0, num_people: 0, num_pulls: 0, projects: {}},
  dashboardStatsHistory: [],
  currentCommit: {},
  currentPullRequest: {},
  currentCommitAnalytics: {},
  currentIssue: {},
  currentPerson: {},
  currentCommitGraph: {},
  currentMessage: {},
  possiblePaths: [],
  possiblePathsReleases: [],
  releaseApproaches: [],
  defectLinkApproaches: [],
  bugFixingNodes: [],
  markNodes: {},
  articulationPoints: [],
  commitLabelFields: [],
  products: {data: [], count: 0},
  productPaths: []
}

const getters = {
  dashboardStats: state => state.dashboardStats,
  dashboardStatsHistory: state => state.dashboardStatsHistory,
  allProjects: state => state.projects,
  allVcs: state => state.vcs,
  allIS: state => state.its,
  allML: state => state.ml,
  allPR: state => state.prs,
  allVcsBranches: state => state.allVcsBranches,
  currentProject: state => state.currentProject,
  currentVcs: state => state.currentVcs,
  currentIts: state => state.currentIts,
  currentMl: state => state.currentMl,
  currentPrs: state => state.currentPrs,
  currentVcsBranches: state => {
    return state.allVcsBranches.filter(item => state.currentVcs !== null && item.vcs_system_id === state.currentVcs.id)
  },
  currentMessage: state => state.currentMessage,
  currentIssue: state => state.currentIssue,
  currentPerson: state => state.currentPerson,
  currentCommitGraph: state => state.currentCommitGraph,
  projectsVcs: state => {
    let pvcs = []
    state.vcs.forEach(item => {
      if (state.currentProject !== null && item.project_id === state.currentProject.id) {
        pvcs.push(item)
      }
    })
    return pvcs
  },
  projectsIts: state => {
    let pvcs = []
    state.its.forEach(item => {
      if (state.currentProject !== null && item.project_id === state.currentProject.id) {
        pvcs.push(item)
      }
    })
    return pvcs
  },
  projectsMls: state => {
    let pvcs = []
    state.ml.forEach(item => {
      if (state.currentProject !== null && item.project_id === state.currentProject.id) {
        pvcs.push(item)
      }
    })
    return pvcs
  },
  projectsPrs: state => {
    let pvcs = []
    state.prs.forEach(item => {
      if (state.currentProject !== null && item.project_id === state.currentProject.id) {
        pvcs.push(item)
      }
    })
    return pvcs
  },
  allProjectData: state => {
    let pwvcs = []
    state.projects.forEach(item => {
      let vcs = state.vcs.filter(vcs => vcs.project_id === item.id)
      let its = state.its.filter(its => its.project_id === item.id)
      let ml = state.ml.filter(ml => ml.project_id === item.id)
      let pr = state.prs.filter(pr => pr.project_id === item.id)

      let vcsId = null
      let itsId = null
      let mlId = null
      let prId = null
      if (vcs.length > 0) {
        vcsId = vcs[0].id
      }
      if (its.length > 0) {
        itsId = its[0].id
      }
      if (ml.length > 0) {
        mlId = ml[0].id
      }
      if (pr.length > 0) {
        prId = pr[0].id
      }
      pwvcs.push({vcs: vcs, its: its, ml: ml, prs: pr, id: item.id, name: item.name, vcs_id: vcsId, its_id: itsId, ml_id: mlId, pr_id: prId})
    })

    return pwvcs
  },
  currentPullRequest: state => state.currentPullRequest,
  currentCommit: state => state.currentCommit,
  currentCommitAnalytics: state => state.currentCommitAnalytics,
  possiblePaths: state => state.possiblePaths,
  possiblePathsReleases: state => state.possiblePathsReleases,
  releaseApproaches: state => state.releaseApproaches,
  defectLinkApproaches: state => state.defectLinkApproaches,
  bugFixingNodes: state => state.bugFixingNodes,
  markNodes: state => state.markNodes,
  articulationPoints: state => state.articulationPoints,
  commitLabelFields: state => state.commitLabelFields,
  products: state => state.products,
  productPaths: state => state.productPaths,
  currentJob: state => state.currentJob
}

const actions = {
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
  getCommit ({commit}, params) {
    commit(types.PUSH_LOADING)
    commit(types.SET_COMMIT, { response: {data: {}} })
    rest.getCommit(params.vcsSystemId, params.revisionHash)
      .then(response => {
        commit(types.SET_COMMIT, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getPullRequest ({commit}, id) {
    commit(types.PUSH_LOADING)
    commit(types.SET_PULL_REQUEST, { response: {data: {}} })
    rest.getPullRequest(id)
      .then(response => {
        commit(types.SET_PULL_REQUEST, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getJob ({commit}, id) {
    commit(types.PUSH_LOADING)
    commit(types.SET_JOB, { response: {data: {}} })
    rest.getJob(id)
      .then(response => {
        commit(types.SET_JOB, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getMessage ({commit}, id) {
    commit(types.PUSH_LOADING)
    commit(types.SET_MESSAGE, { response: {data: {}} })
    rest.getMessage(id)
      .then(response => {
        commit(types.SET_MESSAGE, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getIssue ({commit}, id) {
    commit(types.PUSH_LOADING)
    commit(types.SET_ISSUE, { response: {data: {}} })
    rest.getIssue(id)
      .then(response => {
        commit(types.SET_ISSUE, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getPerson ({commit}, id) {
    commit(types.PUSH_LOADING)
    commit(types.SET_PERSON, { response: {data: {}} })
    rest.getPerson(id)
      .then(response => {
        commit(types.SET_PERSON, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getProducts ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getProducts(dat)
      .then(response => {
        commit(types.SET_PRODUCTS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getProductPaths ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getProductPaths(dat)
      .then(response => {
        commit(types.SET_PRODUCT_PATHS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getReleasePaths ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getReleasePaths(dat)
      .then(response => {
        commit(types.SET_POSSIBLE_PATHS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  clearProductPaths ({commit}) {
    commit(types.SET_PRODUCT_PATHS, { response: {data: {paths: [], products: []}} })
  },
  getCommitGraph ({commit}, id) {
    commit(types.PUSH_LOADING)
    commit(types.SET_COMMIT_GRAPH, { response: {data: {}} })
    rest.getCommitGraph(id)
      .then(response => {
        commit(types.SET_COMMIT_GRAPH, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getPossiblePaths ({commit}, dat) {
    commit(types.PUSH_LOADING)
    commit(types.SET_POSSIBLE_PATHS, { response: {data: {}} })
    rest.getPossiblePaths(dat)
      .then(response => {
        commit(types.SET_POSSIBLE_PATHS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getReleaseApproaches ({commit}) {
    commit(types.PUSH_LOADING)
    commit(types.SET_RELEASE_APPROACHES, { response: {data: {}} })
    rest.getReleaseApproaches()
      .then(response => {
        commit(types.SET_RELEASE_APPROACHES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  clearPaths ({commit}) {
    commit(types.SET_POSSIBLE_PATHS, { response: { data: { paths: [] } } })
  },
  getDefectLinkApproaches ({commit}) {
    commit(types.PUSH_LOADING)
    commit(types.SET_DEFECT_LINK_APPROACHES, { response: {data: {}} })
    rest.getDefectLinkApproaches()
      .then(response => {
        commit(types.SET_DEFECT_LINK_APPROACHES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  clearBugFixingNodes ({commit}) {
    commit(types.SET_BUG_FIXING_NODES, { response: {data: {results: []}} })
  },
  getBugFixingNodes ({commit}, dat) {
    commit(types.PUSH_LOADING)
    commit(types.SET_BUG_FIXING_NODES, { response: {data: {results: []}} })
    rest.getBugFixingNodes(dat)
      .then(response => {
        commit(types.SET_BUG_FIXING_NODES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  getMarkNodes ({commit}, dat) {
    commit(types.PUSH_LOADING)
    rest.getMarkNodes(dat)
      .then(response => {
        commit(types.SET_MARK_NODES, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  clearMarkNodes ({commit}) {
    commit(types.SET_MARK_NODES, { response: { data: { results: [] } } })
  },
  getArticulationPoints ({commit}, dat) {
    commit(types.PUSH_LOADING)
    // commit(types.SET_ARTICULATION_POINTS, { response: {data: {results: []}} })
    rest.getArticulationPoints(dat)
      .then(response => {
        commit(types.SET_ARTICULATION_POINTS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  clearArticulationPoints ({commit}) {
    commit(types.SET_ARTICULATION_POINTS, { response: { data: { results: [] } } })
  },
  getAllProjects ({commit}) {
    rest.getAllProjects()
      .then(response => {
        commit(types.RECEIVE_PROJECTS, { response })
      })
      .catch(error => {
        commit(types.PUSH_ERROR, { error })
      })
  },
  getAllVcs ({commit}) {
    rest.getAllVcs()
      .then(response => {
        commit(types.RECEIVE_VCS, { response })
      })
      .catch(error => {
        commit(types.PUSH_ERROR, { error })
      })
  },
  getAllVcsBranches ({commit}) {
    rest.getAllVcsBranches()
      .then(response => {
        commit(types.SET_VCS_BRANCHES, { response })
      })
      .catch(error => {
        commit(types.PUSH_ERROR, { error })
      })
  },
  getAllIssueSystems ({commit}) {
    rest.getAllIssueSystems()
      .then(response => {
        commit(types.RECEIVE_IS, { response })
      })
      .catch(error => {
        commit(types.PUSH_ERROR, { error })
      })
  },
  getAllMailingLists ({commit}) {
    rest.getAllMailingLists()
      .then(response => {
        commit(types.RECEIVE_ML, { response })
      })
      .catch(error => {
        commit(types.PUSH_ERROR, { error })
      })
  },
  getAllPullRequestSystems ({commit}) {
    rest.getAllPullRequestSystems()
      .then(response => {
        commit(types.RECEIVE_PRS, { response })
      })
      .catch(error => {
        commit(types.PUSH_ERROR, { error })
      })
  },
  setProject ({commit, getters}, project) {
    // on changing the project we also set the projects VCS and ITS if there is only one.
    commit(types.SET_PROJECT, { project })
    let vcs = null
    let its = null
    let ml = null
    let pr = null
    if (getters.projectsVcs.length === 1) {
      vcs = getters.projectsVcs[0]
    }
    if (getters.projectsIts.length === 1) {
      its = getters.projectsIts[0]
    }
    if (getters.projectsMls.length === 1) {
      ml = getters.projectsMls[0]
    }
    if (getters.projectsPrs.length === 1) {
      pr = getters.projectsPrs[0]
    }
    commit(types.SET_VCS, { vcs })
    commit(types.SET_ITS, { its })
    commit(types.SET_ML, { ml })
    commit(types.SET_PRS, { pr })
  },
  setVcs ({commit}, vcs) {
    commit(types.SET_VCS, { vcs })
  },
  setIts ({commit}, its) {
    commit(types.SET_ITS, { its })
  },
  setMl ({commit}, ml) {
    commit(types.SET_ML, { ml })
  },
  setPrs ({commit}, prs) {
    commit(types.SET_PRS, { prs })
  },
  getCommitAnalytics ({commit}, id) {
    commit(types.PUSH_LOADING)
    commit(types.SET_COMMIT_ANALYTICS, { response: {data: {}} })
    rest.getCommitAnalytics(id)
      .then(response => {
        commit(types.SET_COMMIT_ANALYTICS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        console.log(error)
        commit(types.POP_LOADING)
        commit(types.SET_COMMIT_ANALYTICS, { })
      })
  },
  getCommitLabelFields ({commit}, dat) {
    commit(types.PUSH_LOADING)
    commit(types.SET_COMMIT_LABEL_FIELDS, { response: {data: {results: []}} })
    rest.getCommitLabelFields(dat)
      .then(response => {
        commit(types.SET_COMMIT_LABEL_FIELDS, { response })
        commit(types.POP_LOADING)
      })
      .catch(error => {
        commit(types.POP_LOADING)
        commit(types.PUSH_ERROR, { error })
      })
  },
  clearCurrentCommit ({commit}) {
    commit(types.SET_PRODUCT_PATHS, { response: {data: {paths: [], products: []}} })
  }
}

const mutations = {
  [types.CLEAR_CURRENT_COMMIT] (state) {
    state.currentCommit = {}
  },
  [types.SET_DASHBOARD_STATS] (state, { response }) {
    state.dashboardStats = response.data
  },
  [types.SET_DASHBOARD_STATS_HISTORY] (state, { response }) {
    state.dashboardStatsHistory = response.data
  },
  [types.SET_DASHBOARD_PROJECTS] (state, { count }) {
    state.dashboard.projects = count
  },
  [types.SET_DASHBOARD_COMMITS] (state, { count }) {
    state.dashboard.commits = count
  },
  [types.SET_DASHBOARD_ISSUES] (state, { count }) {
    state.dashboard.issues = count
  },
  [types.SET_DASHBOARD_FILES] (state, { count }) {
    state.dashboard.files = count
  },
  [types.SET_DASHBOARD_EMAILS] (state, { count }) {
    state.dashboard.emails = count
  },
  [types.SET_DASHBOARD_PEOPLE] (state, { count }) {
    state.dashboard.people = count
  },
  [types.SET_COMMIT] (state, { response }) {
    state.currentCommit = response.data
  },
  [types.SET_PULL_REQUEST] (state, { response }) {
    state.currentPullRequest = response.data
  },
  [types.SET_JOB] (state, { response }) {
    state.currentJob = response.data
  },
  [types.SET_MESSAGE] (state, { response }) {
    state.currentMessage = response.data
  },
  [types.SET_COMMIT_ANALYTICS] (state, { response }) {
    if (typeof response !== 'undefined') {
      state.currentCommitAnalytics = response.data
    } else {
      state.currentCommitAnalytics = {}
    }
  },
  [types.SET_COMMIT_GRAPH] (state, { response }) {
    state.currentCommitGraph = response.data
  },
  [types.SET_PRODUCTS] (state, { response }) {
    state.products = {data: response.data.results, count: response.data.length}
  },
  [types.SET_PRODUCT_PATHS] (state, { response }) {
    if (typeof response.data.products !== 'undefined') {
      state.productPaths = response.data
    } else {
      state.productPaths = []
    }
  },
  [types.SET_ISSUE] (state, { response }) {
    state.currentIssue = response.data
  },
  [types.SET_PERSON] (state, { response }) {
    state.currentPerson = response.data
  },
  [types.SET_POSSIBLE_PATHS] (state, { response }) {
    state.possiblePaths = response.data
  },
  [types.SET_BUG_FIXING_NODES] (state, { response }) {
    state.bugFixingNodes = response.data.results
  },
  [types.SET_MARK_NODES] (state, { response }) {
    state.markNodes = response.data.results
  },
  [types.SET_ARTICULATION_POINTS] (state, { response }) {
    state.articulationPoints = response.data.results
  },
  [types.SET_RELEASE_APPROACHES] (state, { response }) {
    state.releaseApproaches = response.data.results
  },
  [types.SET_DEFECT_LINK_APPROACHES] (state, { response }) {
    state.defectLinkApproaches = response.data.results
  },
  [types.SET_COMMIT_LABEL_FIELDS] (state, { response }) {
    state.commitLabelFields = response.data.results
  },
  [types.RECEIVE_PROJECTS] (state, { response }) {
    state.projects = response.data.results
  },
  [types.SET_PROJECT] (state, { project }) {
    state.currentProject = project
  },
  [types.SET_VCS] (state, { vcs }) {
    state.currentVcs = vcs
  },
  [types.SET_ITS] (state, { its }) {
    state.currentIts = its
  },
  [types.SET_ML] (state, { ml }) {
    state.currentMl = ml
  },
  [types.SET_PRS] (state, { prs }) {
    state.currentPrs = prs
  },
  [types.RECEIVE_VCS] (state, { response }) {
    state.vcs = response.data.results
  },
  [types.RECEIVE_IS] (state, { response }) {
    state.its = response.data.results
  },
  [types.RECEIVE_ML] (state, { response }) {
    state.ml = response.data.results
  },
  [types.RECEIVE_PRS] (state, { response }) {
    state.prs = response.data.results
  },
  [types.SET_VCS_BRANCHES] (state, { response }) {
    state.allVcsBranches = response.data.results
  }
}

export default {
  state,
  getters,
  actions,
  mutations
}
