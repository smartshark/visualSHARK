<template>
<div class="wrapper">
  <template v-if="flashes">
    <alert v-for="flash in flashes" :key="flash.id" placement="top-center" duration="5" type="success" dismissable>
      <span class="icon-info-circled alert-icon-float-left"></span>
      <p>{{flash.message}}</p>
    </alert>
  </template>
  <div class="card" v-bind:class="{'isLoading': isLoading}">
    <div class="card-header">
      <i class="fa fa-info"></i> Control
    </div>
    <div class="card-block">
      <div v-if="isSuperuser">
        <input type="text" v-model="external_id"/> <button v-on:click="loadBugfix">Load</button>
      </div>
<!--       <div class="submitLine">
        <button v-if="result.length == 0" v-on:click="submit" class="btn btn-primary">Submit Labels</button>
        <button v-else v-on:click="load" class="btn btn-primary">Load next issue</button>
      </div> -->
<!--       <div v-if="result.length > 0">
        Submitted and validated changes:
        <div v-for="change in result">
          <div v-for="(item, key, index) in change">
            <strong>FileChange: {{key}}</strong><br/>
            <div v-for="(item2, key2, index2) in item">
              <strong>Hunk: {{key2}}</strong><br/>
              <div v-for="l in item2">
                {{l}}
              </div>
            </div>
          </div>
        </div>
      </div> -->
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
    <div class="card" v-for="commit in commits" v-if="commit.changes.length > 0">
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
  </div>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'
import rest from '../api/rest'

import DiffView from '@/components/DiffView2.vue'
import modal from '@/components/Modal'

export default {
  name: 'InspectBugfix',
  data () {
    return {
      commits: [],
      issue: {},
      result: [],
      vcs_url: '',
      issue_url: '',
      isLoading: false,
      external_id: 'SCXML-285',
      flashes: []
    }
  },
  components: {
    alert,
    DiffView,
    modal
  },
  computed: mapGetters({
    isSuperuser: 'isSuperuser',
    currentProject: 'currentProject',
    projectsVcs: 'projectsVcs',
    projectsIts: 'projectsIts'
  }),
  watch: {
    currentProject (value) {
    }
  },
  mounted() {
  },
  methods: {
    loadBugfix: function(event) {
      console.log(this.external_id, 'loading bugfix')
      this.$store.dispatch('pushLoading')
      this.result = []
      this.commits = []
      this.flashes = []
      this.vcs_url = ''
      this.issue_url = ''
      this.issue = {}
      this.isLoading = true
      rest.getBugfix(this.currentProject.name, this.external_id)
        .then(response => {
          this.$store.dispatch('popLoading')
          this.isLoading = false
          this.commits = response.data['commits']
          this.issue = response.data['issue']
          this.vcs_url = response.data['vcs_url']
          this.issue_url = response.data['issue_url']
          console.log(this.commits)
        })
        .catch(e => {
          this.isLoading = false
          this.$store.dispatch('pushError', e)
        });
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
