<template>
  <div class="wrapper">
    <template v-if="flashes">
      <alert v-for="flash in flashes" :key="flash.id" placement="top-center" duration="5" type="success" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <p>{{flash.message}}</p>
      </alert>
    </template>
    <div class="animated fadeIn">

      <div class="submitLine">
        <button v-if="commit.revision_hash" v-on:click="submit" class="btn btn-primary">Submit Labels</button>
        <button v-else v-on:click="load" class="btn btn-primary">Load next issue</button>
      </div>

      <div class="card" v-if="commit.revision_hash">
        <div class="card-header"><i class="fa fa-code"></i> Commit <a :href="'https://github.com/apache/' + commit.project_name + '/commits/' + commit.revision_hash">{{commit.revision_hash}}</a>
        </div>
        <div class="card-block">
<pre>{{commit.message}}</pre>
          <input type="checkbox" v-model="commit.is_perfective" name="is_perfective"/> increases quality<br/>
          <input type="checkbox" v-model="commit.is_corrective" name="is_corrective"/> fixes a bug
        </div>
      </div>

      <div class="card" v-if="commit.revision_hash && commit.issues.length > 0">
        <div class="card-header"><i class="fa fa-bug"></i> Linked issues
        </div>
        <div class="card-block">
          <div v-for="i in commit.issues">
            <a :href="'https://issues.apache.org/jira/browse/' + i.external_id">{{i.external_id}}</a> Bug is validated: {{i.verified_bug}}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert, checkbox } from 'vue-strap'
import rest from '../api/rest'

export default {
  name: '',
  data () {
    return {
      commit: {},
      flashes: []
    }
  },
  components: {
    alert,
    checkbox
  },
  mounted () {
  },
  computed: mapGetters({
    loading: 'loading'
  }),
  watch: {
  },
  methods: {
    load() {
      this.loadSample()
    },
    loadSample() {
      this.$store.dispatch('pushLoading')
      this.commit = {}
      rest.getChangeType()
        .then(response => {
          this.flashes = []
          this.$store.dispatch('popLoading')
          if(response.data['warning'] == 'no_more_issues') {
            this.flashes.push({id: 'no_more_data', message: 'No more labeling necessary. Thank you!'})
            return
          }
          this.commit = response.data
        })
        .catch(e => {
          this.$store.dispatch('popLoading')
          this.$store.dispatch('pushError', e)
        });
    },
    submit() {
      this.$store.dispatch('pushLoading')
      rest.setChangeType({data: this.commit})
        .then(response => {
          this.$store.dispatch('popLoading')
          this.commit = {}
        })
        .catch(e => {
          this.$store.dispatch('popLoading')
          this.$store.dispatch('pushError', e)
        });
    }
  }
}
</script>

<style>

</style>
