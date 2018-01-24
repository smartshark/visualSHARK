import rest from '../../api/rest'
import * as types from '../mutation-types'

// initial
const state = {
  topicModels: [],
  topicEvaluation: null
}

const getters = {
  topicModels: state => state.topicModels,
  topicEvaluation: state => state.topicEvaluation
}

const actions = {
  getAllTopicModels ({commit}, id) {
    rest.getTopicModelsForProject(id)
      .then(response => {
        commit(types.GRID_TOPICS, { response })
      })
      .catch(e => {
        commit(types.PUSH_ERROR, { e })
      })
  },
  evaluateTopicModelwithIssue ({commit}, dat) {
    console.log(dat)
    rest.evaluateTopicModelForCommit(dat)
      .then(response => {
        console.log(response.data)
        commit(types.TOPIC_EVAL, { response })
      })
      .catch(e => {
        commit(types.PUSH_ERROR, { e })
      })
  }
}

const mutations = {
  [types.GRID_TOPICS] (state, { response }) {
    if (typeof response.data.models === 'undefined') {
      state.topicModels = {data: response.data, count: response.data.length}
    } else {
      state.topicModels = {data: response.data.models, count: response.data.models.count}
    }
  },
  [types.TOPIC_EVAL] (state, { response }) {
    if (typeof response.data.evaluation === 'undefined') {
      state.topicEvaluation = {data: response.data, count: response.data.length}
    } else {
      state.topicEvaluation = {data: response.data.evaluation, count: response.data.evaluation.count}
    }
  }
}

export default {
  state,
  getters,
  actions,
  mutations
}
