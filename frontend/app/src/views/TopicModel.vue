<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-pie-chart"></i> Topic Models
        </div>
<div class="card-body">
<grid :gridColumns="grid.columns" :data="topicModels.data" :count="topicModels.count" :defaultPerPage="15" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
                    <template slot="name" slot-scope="props">
                      <td><router-link :to="{ name: 'TopicModel', params: { id: props.row.id }}">{{ props.row.name }}</router-link></td>
                    </template>
                  </grid>
        </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header"><i class="fa fa-pie-chart"></i> Topic Model Visualization
        </div>
          <div class="card-body">
              <div id="lda"></div>
         </div>
        </div>

      <div class="card">
        <div class="card-header"><i class="fa fa-pie-chart"></i> Topic Model Details
        </div>
          <div class="card-body">
             	<div class="table-responsive">
                 <table class="table">
                    <thead>
                      <tr>
                       <th scope="col">#</th>
                       <th scope="col">Topic Description</th>
                     </tr>
                    </thead>
                    <tbody>
                       <tr v-for="topic in topics">
                         <th scope="row">{{ topic.id }}</th>
                         <td>{{ topic.description }}</td>
                       </tr>
                     </tbody>
                  </table>
                </div>
         </div>
        </div>
    </div>
  </div>
</template>
<script>

import { mapGetters } from 'vuex'
import { dropdown } from 'vue-strap'

import rest from '../api/rest'
import LDAvis from '../vue-ldavis/LDAvis.js'
import Grid from '@/components/Grid.vue'

export default {
  name: 'TopicModelOverview',
  props: {id: false},
  data () {
    return {
      grid: {
        columns: [
          {ident: 'name', name: 'Name'},
          {ident: 'passes', name: 'Passes'},
          {ident: 'K', name: 'K'},
          {ident: 'issues', name: 'Issues'},
          {ident: 'issue_comments', name: 'Issue-Comments'},
          {ident: 'messages', name: 'Messages'},
          {ident: 'filter', name: 'Filter'},
          {ident: 'project_filter', name: 'Project-Filter'},
          {ident: 'language_filter', name: 'Language-Filter'}
        ]
      },
      triggerRefresh: false,
      triggerRefreshTags: false,
      topicModelBody: '',
      topics: []
    }
  },
  components: {
    Grid, dropdown
  },
  mounted () {
    this.loadTopicModelsForProject()
    if (this.id !== false && typeof this.id !== 'undefined') {
      this.loadTopicModel(this.id)
    }
  },
  computed: mapGetters({
    topicModels: 'topicModels',
    currentProject: 'currentProject',
    isSuperuser: 'isSuperuser'
  }),
  watch: {
    currentProject (value) {
      if (typeof value.id !== 'undefined') {
        this.triggerRefresh = true
        this.triggerRefreshTags = true
      }
    },
    id (value) {
      if (value !== false && typeof value !== 'undefined') {
        this.loadTopicModel(value)
      }
    }
  },
  methods: {
    loadTopicModel (id) {
      this.active_id = id
      let dat = {'id': id}
      rest.getTopicModel(dat)
        .then(response => {
          console.log(response.data)
          LDAvis.getLDAvis('#lda', JSON.parse(response.data.data))
          this.topics = response.data.table
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    loadTopicModelsForProject () {
      this.$store.dispatch('getAllTopicModels', this.currentProject.id)
    },
    refreshGrid (dat) {
      this.triggerRefresh = false
      this.loadTopicModelsForProject()
    },
    refreshGridTags (dat) {
      this.triggerRefreshTags = false
      this.loadTopicModelsForProject()
    }
  }
}
</script>

<style>
</style>
