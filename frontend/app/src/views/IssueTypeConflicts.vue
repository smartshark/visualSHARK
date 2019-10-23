<template>
<div class="wrapper">
   <div class="animated fadeIn" v-if="currentProject && currentProject.id">
      {{ issues.length }} from {{ max }} entries <br>

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
                     <a :href="issue.url" target="_blank">
                        <h5>{{ issue.title }}</h5>
                     </a>
                     <pre>{{ issue.desc }}</pre><br/>
                    <template v-for="link in issue.links">
                        <a :href="link.link" target="_blank">{{ link.name }}</a>&nbsp;
                     </template>
                  </td>
               </tr>
            </tbody>
         </table>
      </div>
      <button v-on:click="submitLabels" type="button" class="btn btn-success">Absenden</button>
   </div>
    <div class="animated fadeIn" v-if="!currentProject">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No project Selected</strong>
        <p>
          Select a project first
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
  name: 'issueTypeConflicts',
  props: {id: false},
  data () {
    return {
      options: [],
      issues: [],
      linked: true,
      issueType: 'all',
      max: 0
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
    currentProject (value) {
      this.loadConflicted()
    },
    currentIts (value) {
      this.loadConflicted()
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
      this.$store.dispatch('pushLoading')
      rest.resolveIssues(this.issues)
        .then(response => {
          this.$store.dispatch('popLoading')
          if (response.data != null) {
            window.scrollTo(0, 0)
            this.loadConflicted()
          }
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    loadConflicted () {
      this.$store.dispatch('pushLoading')
      var dat = {}
      if (this.currentProject !== null && this.currentProject.id !== null) {
        dat.filter = '&project_id=' + this.currentProject.id
        if (this.currentIts !== null) {
          dat.filter = dat.filter + '&issue_system_id=' + this.currentIts.id
        }
        dat.filter = dat.filter + '&linked=' + this.linked
        dat.filter = dat.filter + '&issue_type=' + this.issueType
        dat.filter = dat.filter + '&limit=10'
        rest.getConflictedIssues(dat)
          .then(response => {
            this.$store.dispatch('popLoading')
            if (response.data != null) {
              this.issues = response.data.issues
              this.options = response.data.options
              this.max = response.data.max
            }
          })
          .catch(e => {
            this.$store.dispatch('pushError', e)
          })
      }
    }
  }
}
</script>
<style>
pre {
    white-space: pre-wrap; 
}
</style>