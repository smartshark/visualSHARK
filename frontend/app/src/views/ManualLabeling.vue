<template>
<div class="wrapper">
   <div class="animated fadeIn" v-if="currentIts && currentIts.id">
      <div class="card">
         <table class="table table-striped">
            <thead>
               <tr>
                  <th>Label from Source</th>
                  <th>Label in SmartSHARK</th>
                  <th>Verification</th>
                  <th>Details</th>
               </tr>
            </thead>
            <tbody>
               <tr v-for="issue in issues">
                  <th>
                     {{ issue.issue_type }}</th>
                  <td>
                     <select v-model="issue.resolution" class="form-control">
                        <option v-for="item in options" :value="item">{{ item }}</option>
                     </select>
                  </td>
                  <td> <input v-model="issue.checked" type="checkbox"> </td>
                  <td>
                     <a href="http://google.de" target="_blank">
                        <h5>{{ issue.title }}</h5>
                     </a>
                     <pre>
                     {{ issue.desc }}
                     </pre>
                  </td>
               </tr>
            </tbody>
         </table>
      </div>
      <button v-on:click="submitLabels" type="button" class="btn btn-success">Absenden</button>
   </div>
   <div class="animated fadeIn" v-if="currentIts && !currentIts.id">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No Issue System</strong>
        <p>
          No Issue System set for Project {{ currentProject.name }}
        </p>
      </alert>
    </div>
    <div class="animated fadeIn" v-if="!currentIts">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No ITS Selected</strong>
        <p>
          Select a ITS first
        </p>
      </alert>
    </div>
</div>
</template>

<script>

import { mapGetters } from 'vuex'
import Grid from '@/components/Grid.vue'
import rest from '../api/rest'

export default {
  name: 'manuallabeling',
  props: {id: false},
  data () {
    return {
      options: [],
      issues: [],
      triggerRefresh: false,
      triggerRefreshEvents: false
    }
  },
  components: {
    Grid
  },
  computed: mapGetters({
    gridIssues: 'gridIssues',
    currentProject: 'currentProject',
    currentIssue: 'currentIssue',
    currentIts: 'currentIts'
  }),
  mounted () {
    this.loadRandomIssue()
  },
  watch: {
    currentIts (value) {
      this.triggerRefresh = true
      this.triggerRefreshEvents = true
    },
    id (value) {
      if (value !== false && typeof value !== 'undefined') {
        this.$store.dispatch('getIssue', value)
      }
    }
  },
  methods: {
    submitLabels () {
      rest.saveManualIssueTypes(this.issues)
        .then(response => {
          console.log(response.data)
          if (response.data != null) {
            this.loadRandomIssue()
          }
        })
    },
    loadRandomIssue () {
      var dat = {}
      if (this.currentProject !== null && this.currentProject.id !== null) {
        dat.filter = '&project_id=' + this.currentProject.id
        dat.filter = dat.filter + '&limit=10'
        rest.getIssueRandom(dat)
          .then(response => {
            console.log(response.data)
            if (response.data != null) {
              this.issues = response.data.issues
              this.options = response.data.options
            }
          })
      }
    }
  }
}
</script>
