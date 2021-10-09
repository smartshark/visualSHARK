<template>
<div class="wrapper">
  <template v-if="flashes">
    <b-alert v-for="flash in flashes" :key="flash.id" placement="top-center" duration="5" variant="success" dismissable>
      <span class="icon-info-circled alert-icon-float-left"></span>
      <p>{{flash.message}}</p>
    </b-alert>
  </template>
  <div class="card" v-bind:class="{'isLoading': isLoading}">
    <div class="card-header">
      <i class="fa fa-info"></i> Control
    </div>
    <div class="card-block">
      <!--<div v-if="isSuperuser">
        <input type="text" v-model="external_id"/> <button v-on:click="loadIssue" class="btn btn-primary">Load issue</button>
      </div>-->
      <div class="submitLine">
        <button v-if="result.length == 0" v-on:click="submit" class="btn btn-primary">Submit Labels</button>
        <button v-else v-on:click="load" class="btn btn-primary">Load next issue</button>
      </div>
      <div v-if="result.length > 0">
        Submitted and validated changes:
        <div v-for="change in result">
          <div v-for="(item, key, index) in change" :key="index">
            <strong>FileChange: {{key}}</strong><br/>
            <div v-for="(item2, key2, index2) in item" :key="index2">
              <strong>Hunk: {{key2}}</strong><br/>
              <div v-for="l in item2">
                {{l}}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="animated fadeIn" v-if="issue.id">
    <div class="card">
      <div class="card-header">
        <i class="fa fa-bug"></i> <a :href="issue_url + issue.external_id" target="_blank">{{issue.external_id}}</a> - {{issue.title}}
      </div>
      <div class="card-block">
        <pre class="force-wrap">{{issue.desc}}</pre>
      </div>
    </div>
    <template v-if="commit.changes.length > 0">
      <div class="card" v-for="commit in commits">
        <div class="card-header">
          <i class="fa fa-code"></i> <a :href="vcs_url + commit.revision_hash" target="_blank">{{commit.revision_hash}}</a> ({{commit.changes.length}} files)
        </div>
        <div class="card-block">
          <pre>{{commit.message}}</pre>
        </div>
        <template v-for="c in commit.changes">
          <DiffView :commit="commit.revision_hash" :parent="c.parent_revision_hash" :filename="c.filename" :lines="c.lines" ref="diffView" :key="commit.revision_hash + c.parent_revision_hash + c.filename"/>
        </template>
      </div>
    </template>
  </div>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import rest from '../api/rest'

import DiffView from '@/components/DiffView.vue'

export default {
  name: 'linelabels',
  data () {
    return {
      commits: [],
      issue: {},
      result: [],
      vcs_url: '',
      issue_url: '',
      has_trained: false,
      load_last: false,
      isLoading: true,
      flashes: []
    }
  },
  components: {
    DiffView
  },
  computed: mapGetters({
    isSuperuser: 'isSuperuser',
    currentProject: 'currentProject',
    projectsVcs: 'projectsVcs',
    projectsIts: 'projectsIts'
  }),
  watch: {
    currentProject () {
      this.loadSample()
    }
  },
  mounted() {
    this.loadSample()
  },
  methods: {
    load() {
      this.loadSample()
    },
    loadSample() {
      this.$store.dispatch('pushLoading')
      this.result = []
      this.commits = []
      this.flashes = []
      this.vcs_url = ''
      this.issue_url = ''
      this.issue = {}
      this.isLoading = true
      rest.getChangedLines(this.currentProject.name)
        .then(response => {
          this.$store.dispatch('popLoading')
          this.isLoading = false
          // maybe we are finished for this project
          if(response.data['warning'] == 'no_more_issues') {
            this.flashes.push({id: 'no_more_issues', message: 'No more issues for this project available, select next project.'})
            return
          }

          this.commits = response.data['commits']
          this.issue = response.data['issue']
          this.vcs_url = response.data['vcs_url']
          this.issue_url = response.data['issue_url']

          this.has_trained = response.data['has_trained']
          this.load_last = response.data['load_last']

          if(this.has_trained !== true) {
            this.flashes.push({id: 'train', message: 'You have not finished the training! Loading training issues first!'})
          }
          if(this.load_last === true) {
            this.flashes.push({id: 'last', message: 'You have not finished labeling the last issue, loading last issue first.'})
          }
        })
        .catch(e => {
          this.isLoading = false
          this.$store.dispatch('pushError', e)
        });
    },
    submit() {
      let isComplete = true
      let result = {}
      this.isLoading = true
      for(let o in this.$refs.diffView) {
        
        let dv = this.$refs.diffView[o]
        if(!dv.isComplete) {
          this.$store.dispatch('pushError', {message: 'Change ' + dv.commit + ' is incomplete!'})
          isComplete = false
        }else {
          let c = dv.commit
          let p = dv.parent
          let f = dv.filename
          let m = dv.models
          result[c + '_' + p + '_' + f] = m
        }
      }

      if(isComplete === true) {
        this.$store.dispatch('pushLoading')
        rest.saveChangedLines({data: {labels: result, issue_id: this.issue.id}, type: 'combined'})
          .then(response => {
            this.isLoading = false
            this.$store.dispatch('popLoading')
            this.result = response.data['changes']
          })
          .catch(e => {
            this.isLoading = false
            this.$store.dispatch('pushError', e)
          });
      }
    }
  }
}
</script>

<style>
pre.force-wrap {
  white-space: pre-wrap;       /* Since CSS 2.1 */
  white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
  white-space: -pre-wrap;      /* Opera 4-6 */
  white-space: -o-pre-wrap;    /* Opera 7 */
  word-wrap: break-word;       /* Internet Explorer 5.5+ */
}
.isLoading {
  opacity: 0.2;
}
</style>
