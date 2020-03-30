<template>
<div class="wrapper">
  <div class="animated fadeIn" v-if="issue.id">
    <div class="card">
      <div class="card-header">
        <i class="fa fa-bug"></i> {{issue.external_id}} - {{issue.title}}
      </div>
      <div class="card-block">
        <pre>{{issue.desc}}</pre>
        <div class="submitLine">
          <button v-on:click="submit">Submit Labels</button>
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
        <DiffView :commit="commit.revision_hash" :filename="c.filename" :code="c.code" :lines="c.lines" :onlyDeleted="c.deleted" :onlyAdded="c.added" ref="diffView"/>
      </template>
    </div>
  </div>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'
import rest from '../api/rest'
import hljs from 'highlight.js/lib/highlight';
import java from 'highlight.js/lib/languages/java';

import DiffView from '@/components/DiffView.vue'

export default {
  name: 'linelabels',
  data () {
    return {
      commits: [],
      issue: {}
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
  mounted() {
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
  methods: {
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
</style>
