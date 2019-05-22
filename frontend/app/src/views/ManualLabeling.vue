<template>
<div class="wrapper">
   <div class="animated fadeIn" v-if="currentIts && currentIts.id">
     Linked issues: <input v-model="linked" type="checkbox">

      Issue Type:
       <select v-model="issueType">
                        <option value="all">No Filter</option>
                        <option v-for="item in options" :value="item">{{ item }}</option>
       </select>
      Labeled by other users: <input v-model="labeledByOtherUser" type="checkbox">

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
      linked: true,
      issueType: 'all',
      labeledByOtherUser: false
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
      this.loadRandomIssue()
    },
    currentProject (value) {
      this.loadRandomIssue()
    },
    linked (value) {
      this.loadRandomIssue()
    },
    issueType (value) {
      this.loadRandomIssue()
    },
    labeledByOtherUser (value) {
      this.loadRandomIssue()
    }
  },
  methods: {
    submitLabels () {
      this.$store.dispatch('pushLoading')
      rest.saveManualIssueTypes(this.issues)
        .then(response => {
          this.$store.dispatch('popLoading')
          if (response.data != null) {
            window.scrollTo(0, 0)
            this.loadRandomIssue()
          }
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    loadRandomIssue () {
      this.$store.dispatch('pushLoading')
      var dat = {}
      if (this.currentProject !== null && this.currentProject.id !== null) {
        dat.filter = '&project_id=' + this.currentProject.id
        dat.filter = dat.filter + '&issue_system_id=' + this.currentIts.id
        dat.filter = dat.filter + '&linked=' + this.linked
        dat.filter = dat.filter + '&issue_type=' + this.issueType
        dat.filter = dat.filter + '&labeled_by_other_user=' + this.labeledByOtherUser
        dat.filter = dat.filter + '&limit=10'
        rest.getIssueRandom(dat)
          .then(response => {
            this.$store.dispatch('popLoading')
            if (response.data != null) {
              this.issues = response.data.issues
              this.options = response.data.options
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