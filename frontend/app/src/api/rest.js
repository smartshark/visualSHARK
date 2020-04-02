import axios from 'axios'

export default {
  token: null,
  getUrl (base) {
    return process.env.VUE_APP_API_URL + base
  },
  getFilterUrl (base, dat) {
    let req = this.getUrl(base + '?')
    if (typeof dat === 'undefined') {
      dat = {limit: 0, offset: 0, filter: '', order: '', search: ''}
    } else {
      if (typeof dat.filter === 'undefined') {
        dat.filter = ''
      }
      if (typeof dat.order === 'undefined') {
        dat.order = ''
      }
      if (typeof dat.search === 'undefined') {
        dat.search = ''
      }
    }
    if (dat.limit > 0) {
      req = req + '&limit=' + dat.limit
    }
    if (dat.offset > 0) {
      req = req + '&offset=' + dat.offset
    }
    if (dat.order !== '') {
      req = req + '&ordering=' + dat.order
    }
    if (dat.filter !== '') {
      req = req + dat.filter
    }
    if (dat.search !== '') {
      req = req + '&search=' + dat.search
    }
    return req
  },
  setToken (token) {
    this.token = token
  },
  login (dat) {
    let req = this.getUrl('auth/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'X-User': dat.user,
      'X-PASS': dat.pass
    }})
  },
  getAllProjects () {
    let req = this.getUrl('project/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getAllVcs () {
    let req = this.getUrl('vcs/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getAllVcsBranches () {
    let req = this.getUrl('branch/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getAllIssueSystems () {
    let req = this.getUrl('is/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getAllMailingLists () {
    let req = this.getUrl('ml/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getProjects (dat) {
    let req = this.getFilterUrl('project/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getCommits (dat) {
    let req = this.getFilterUrl('commit/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getReleases (dat) {
    let req = this.getFilterUrl('analytics/release/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getCommit (vcsSystemId, id) {
    let req = this.getUrl('commit/' + id + '/' + '?vcs_system_id=' + vcsSystemId)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getIssue (id) {
    let req = this.getUrl('issue/' + id + '/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getIssueRandom (dat) {
    let req = this.getFilterUrl('labeling/issue/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getConflictedIssues (dat) {
    let req = this.getFilterUrl('labeling/conflict/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  saveManualIssueTypes (dat) {
    let req = this.getUrl('labeling/issue')
    return axios.post(req, dat, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  resolveIssues (dat) {
    let req = this.getUrl('labeling/conflict')
    return axios.post(req, dat, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getCommitWithLinksRandom (dat) {
    let req = this.getFilterUrl('labeling/links/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  saveIssueLinks (dat) {
    let req = this.getUrl('labeling/links')
    return axios.post(req, dat, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getPerson (id) {
    let req = this.getUrl('people/' + id + '/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getFileActions (dat) {
    let req = this.getFilterUrl('fileaction/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getCodeEntityStates (dat) {
    // dublicate code with getProductFile
    // this is a special case, we may have NaN, -Infinity, +Infinity in the Json as python allows this.
    // JavaScripts parser does not allow this so we simply replace them here with null.
    let req = this.getFilterUrl('codeentitystate/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    },
    responseType: 'text',
    transformResponse: [function (data) { let tmp = data.replace(/\bNaN\b/g, 'null').replace(/\b-Infinity\b/g, 'null').replace(/\b\+Infinity\b/g, 'null'); return JSON.parse(tmp) }]
    })
  },
  getIssues (dat) {
    let req = this.getFilterUrl('issue/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getPeople (dat) {
    let req = this.getFilterUrl('people/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getMessages (dat) {
    let req = this.getFilterUrl('message/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getMessage (id) {
    let req = this.getUrl('message/' + id + '/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getTags (dat) {
    let req = this.getFilterUrl('tag/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getFiles (dat) {
    let req = this.getFilterUrl('file/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getHunks (dat) {
    let req = this.getFilterUrl('hunk/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getJob (id) {
    let req = this.getUrl('system/job/' + id + '/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getJobs (dat) {
    let req = this.getFilterUrl('system/job/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getReleaseApproaches () {
    let req = this.getUrl('analytics/releaseApproach/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getDefectLinkApproaches () {
    let req = this.getUrl('analytics/defectLinkApproach/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getProjectDatas (dat) {
    let req = this.getFilterUrl('analytics/project/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getDefectLinks (dat) {
    let req = this.getFilterUrl('analytics/defectLink/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getProjectReleaseDatas (dat) {
    let req = this.getFilterUrl('analytics/release/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getFileHistory (dat) {
    let req = this.getFilterUrl('analytics/filehistory/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getProjectData (id) {
    let req = this.getFilterUrl('analytics/project/' + id + '/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  addProjectReleaseData (data) {
    let req = this.getUrl('analytics/release/')
    return axios.post(req, data, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  deleteProjectReleaseData (id) {
    let req = this.getUrl('analytics/release/' + id + '/')
    return axios.delete(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getProjectReleaseFile (id) {
    let req = this.getUrl('analytics/release/' + id + '/file/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getFileChanges (dat) {
    let req = this.getFilterUrl('analytics/filechange/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getCommitLabelFields (dat) {
    let req = this.getFilterUrl('analytics/commitlabel/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getFileChange (id) {
    let req = this.getUrl('analytics/filechange/' + id + '/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getCommitGraph (id) {
    let req = this.getUrl('analytics/commitgraph/' + id + '/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getProducts (dat) {
    let req = this.getFilterUrl('product/', dat)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getProductPaths (dat) {
    let qry = '?'
    if (dat.productIds !== null) {
      qry = qry + 'product_ids=' + dat.productIds.join(',')
    }
    let req = this.getUrl('analytics/commitgraph/' + dat.commitGraph + '/product_path/' + qry)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getProductFile (id) {
    // this is a special case, we may have NaN, -Infinity, +Infinity in the Json as python allows this.
    // JavaScripts parser does not allow this so we simply replace them here with null.
    let req = this.getUrl('product/' + id + '/file/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    },
    responseType: 'text',
    transformResponse: [function (data) { let tmp = data.replace(/\bNaN\b/g, 'null').replace(/\b-Infinity\b/g, 'null').replace(/\b\+Infinity\b/g, 'null'); return JSON.parse(tmp) }]
    })
  },
  getProductFileDownload (id) {
    let req = this.getUrl('product/' + id + '/file_download/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    },
    responseType: 'arraybuffer'
    })
  },
  getPossiblePaths (dat) {
    let req = this.getUrl('analytics/commitgraph/' + dat.commitGraph + '/path/?start_commit=' + dat.startCommit + '&end_commit=' + dat.endCommit)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getReleasePaths (dat) {
    let req = this.getUrl('analytics/commitgraph/' + dat.commitGraph + '/ontdekbaan/?commit=' + dat.commit)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getBugFixingNodes (dat) {
    let req = this.getUrl('analytics/commitgraph/' + dat.commitGraph + '/bug_fixing/?approach=' + dat.approach)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getMarkNodes (dat) {
    let qry = '?'
    if (dat.searchMessage !== null) {
      qry = qry + 'searchMessage=' + encodeURIComponent(dat.searchMessage) + '&'
    }
    if (dat.label !== null) {
      qry = qry + 'label=' + encodeURIComponent(dat.label.join(',')) + '&'
    }
    if (dat.travis !== null) {
      qry = qry + 'travis=' + encodeURIComponent(dat.travis.join(',')) + '&'
    }
    let req = this.getUrl('analytics/commitgraph/' + dat.vcsId + '/mark_nodes/' + qry)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  predictEvaluate (dat) {
    let req = this.getUrl('analytics/predictevaluate/?training=' + dat.training.join(',') + '&test=' + dat.test.join(',') + '&model=' + dat.model)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  predict (dat) {
    let req = this.getUrl('analytics/predict/?training=' + dat.training.join(',') + '&test=' + dat.test.join(',') + '&model=' + dat.model)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getArticulationPoints (dat) {
    let req = this.getUrl('analytics/commitgraph/' + dat.commitGraph + '/articulation_points/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getCommitAnalytics (revisionHash) {
    let req = this.getUrl('analytics/commit/' + revisionHash + '/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getStats () {
    let req = this.getUrl('stats/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getIssueLinkCandidates (commitId) {
    let req = this.getUrl('analytics/issuelinkcandidates/?commit_id=' + commitId)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getAffectedEntities (commitId, faId) {
    let req = this.getUrl('analytics/affectedentities/?commit_id=' + commitId + '&file_action_id=' + faId)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getChangedLines (projectName) {
    let req = this.getUrl('labeling/lines/?project_name=' + projectName)
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  saveChangedLines (dat) {
    let req = this.getUrl('labeling/lines/')
    return axios.post(req, dat, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getStatsHistory () {
    let req = this.getUrl('statshistory/')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  getLeaderboard () {
    let req = this.getUrl('labeling/leaderboard')
    return axios.get(req, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  createRevisionJob (dat) {
    let req = this.getUrl('system/job/collect_revision/')
    return axios.post(req, dat, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  createOtherJob (dat) {
    let req = this.getUrl('system/job/collect_other/')
    return axios.post(req, dat, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  requeueJob (id) {
    let req = this.getUrl('system/job/' + id + '/requeue/')
    return axios.post(req, {}, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  testConnectionWorkerJob (dat) {
    let req = this.getUrl('system/job/test_connection_worker/')
    return axios.post(req, dat, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  },
  testConnectionServersharkJob (dat) {
    let req = this.getUrl('system/job/test_connection_servershark/')
    return axios.post(req, dat, {headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token ' + this.token
    }})
  }
}
