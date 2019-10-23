<template>
<div class="wrapper">
   <div class="animated fadeIn" v-if="currentProject && currentProject.id">
      {{ commits.length }} from {{ max }} entries <br>
      <div class="card">
         <table class="table table-striped">
            <thead>
               <tr>
                  <th>Links</th>
                  <th>Commit Message</th>
               </tr>
            </thead>
            <tbody>
               <tr v-for="commit in commits">
                  <td style="width: 30%">
                      <multiselect v-model="commit.selected_links" :options="commit.links" :multiple="true"></multiselect>
                  </td>
                  <td>
                     <pre>{{ commit.message }}</pre>
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
import rest from '../api/rest'

import Multiselect from 'vue-multiselect'

export default {
  name: 'commitIssueLinks',
  props: {id: false},
  data () {
    return {
      commits: [],
      linked: true,
      issueType: 'all',
      max: 0
    }
  },
  components: {
    Multiselect
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    currentIssue: 'currentIssue',
    currentVcs: 'currentVcs'
  }),
  mounted () {
    this.loadRandomIssueLinks()
  },
  watch: {
    currentProject (value) {
      this.loadRandomIssueLinks()
    },
    currentVcs (value) {
      this.loadRandomIssueLinks()
    },
    linked (value) {
      this.loadRandomIssueLinks()
    },
    issueType (value) {
      this.loadRandomIssueLinks()
    }
  },
  methods: {
    submitLabels () {
      this.$store.dispatch('pushLoading')
      rest.saveIssueLinks(this.commits)
        .then(response => {
          window.scrollTo(0, 0)
          this.$store.dispatch('popLoading')
          if (response.data != null) {
            this.loadRandomIssueLinks()
          }
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    loadRandomIssueLinks () {
      this.$store.dispatch('pushLoading')
      var dat = {}
      if (this.currentProject !== null && this.currentProject.id !== null) {
        dat.filter = '&project_id=' + this.currentProject.id
        if (this.currentVcs !== null) {
          dat.filter = dat.filter + '&vcs_system_id=' + this.currentVcs.id
        }
        dat.filter = dat.filter + '&limit=10'
        rest.getCommitWithLinksRandom(dat)
          .then(response => {
            this.$store.dispatch('popLoading')
            if (response.data != null) {
              this.commits = response.data.commits
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
