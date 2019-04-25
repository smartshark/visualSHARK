<template>
<div class="wrapper">
   <div class="animated fadeIn" v-if="currentIts && currentIts.id">
      Linked issues: <input v-model="linked" type="checkbox">

      Issue Type:
       <select v-model="issueType">
                        <option value="all">No Filter</option>
                        <option v-for="item in options" :value="item">{{ item }}</option>
       </select>
      <div class="card">
         <table class="table table-striped">
            <thead>
               <tr>
                  <th>Label from Source</th>
                  <th>Labels from Users</th>
                  <th>Label in SmartSHARK</th>
                  <th>Verification</th>
                  <th>Details</th>
               </tr>
            </thead>
            <tbody>
               <tr v-for="issue in issues">
                  <th>
                     {{ issue.issue_type }}</th>
                  <th>
                    <div v-for="manual_issue in issue.issue_type_manual">{{ manual_issue }}</div></th>
                  <td>
                     <select v-model="issue.resolution" class="form-control" size="10">
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
  name: 'resolutionview',
  props: {id: false},
  data () {
    return {
      options: [],
      issues: [],
      triggerRefresh: false,
      triggerRefreshEvents: false,
      linked: true,
      issueType: 'all'
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
    this.loadConflicted()
  },
  watch: {
    currentIts (value) {
      this.triggerRefresh = true
      this.triggerRefreshEvents = true
    },
    linked (value) {
      this.loadConflicted()
    },
    issueType (value) {
      this.loadConflicted()
    }
  },
  methods: {
    submitLabels () {
      rest.resolveIssues(this.issues)
        .then(response => {
          console.log(response.data)
          if (response.data != null) {
            this.loadConflicted()
          }
        })
    },
    loadConflicted () {
      var dat = {}
      if (this.currentProject !== null && this.currentProject.id !== null) {
        dat.filter = '&project_id=' + this.currentProject.id
        dat.filter = dat.filter + '&issue_system_id=' + this.currentIts.id
        dat.filter = dat.filter + '&linked=' + this.linked
        dat.filter = dat.filter + '&issue_type=' + this.issueType
        dat.filter = dat.filter + '&limit=10'
        rest.getConflictedIssues(dat)
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
