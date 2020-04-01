<template>
<div class="wrapper">
  <div class="animated fadeIn" v-if="issue.id">
    <div class="card">
      <div class="card-header">
        <i class="fa fa-bug"></i> {{issue.external_id}} - {{issue.title}}
      </div>
      <div class="card-block">
        <pre class="force-wrap">{{issue.desc}}</pre>
        <div class="submitLine">
          <button v-on:click="submit">Submit Labels</button>
        </div>
        <div v-if="result.length > 0">
          Submitted and validated changes:
          <div v-for="change in result">{{change}}</div>
        </div>
      </div>
    </div>
    <div class="card" v-for="commit in commits" v-if="commit.changes.length > 0">
      <div class="card-header">
        <i class="fa fa-code"></i> {{commit.revision_hash}}
      </div>
      <div class="card-block">
        <pre>{{commit.message}}</pre>
      </div>
      <template v-for="c in commit.changes">
        <DiffView :commit="commit.revision_hash" :filename="c.filename" :lines="c.lines" ref="diffView"/>
      </template>
    </div>
  </div>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'
import rest from '../api/rest'

import DiffView from '@/components/DiffView.vue'

export default {
  name: 'linelabels',
  data () {
    return {
      commits: [],
      issue: {},
      result: []
    }
  },
  components: {
    alert,
    DiffView
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    projectsVcs: 'projectsVcs',
    projectsIts: 'projectsIts'
  }),
  watch: {
    currentProject (value) {
      this.loadSample()
    }
  },
  mounted() {
    this.loadSample()
  },
  methods: {
    loadSample() {
      this.$store.dispatch('pushLoading')
      rest.getChangedLines(this.currentProject.name)
        .then(response => {
          this.$store.dispatch('popLoading')
          this.commits = response.data['commits']
          this.issue = response.data['issue']
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        });
    },
    submit() {
      let isComplete = true;
      let result = {}
      for(let o in this.$refs.diffView) {
        let dv = this.$refs.diffView[o]
        if(!dv.isComplete) {
          this.$store.dispatch('pushError', {message: 'Change ' + dv.commit + ' is incomplete!'})
          isComplete = false
        }else {
          let c = dv.commit
          let f = dv.filename
          let m = dv.models
          result[c + '_' + f] = m
        }
      }

      if(isComplete === true) {
        this.$store.dispatch('pushLoading')
        rest.saveChangedLines({data: {labels: result, issue_id: this.issue.id}})
          .then(response => {
            this.$store.dispatch('popLoading')
            this.result = response.data['changes']
          })
          .catch(e => {
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
</style>
