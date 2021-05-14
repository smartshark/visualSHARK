<template>
  <div class="wrapper">
    <template v-if="flashes">
      <b-alert v-for="flash in flashes" :key="flash.id" placement="top-center" duration="5" variant="success" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <p>{{flash.message}}</p>
      </b-alert>
    </template>
    <div class="animated fadeIn">

      <div class="row">
        <div class="col-md-6">
          <div v-if="commit.revision_hash" class="form-group">
            <div class="input-group">
              <div class="input-group-addon">
                <span class="input-group-text">{{finished}}/{{todo + finished}}</span>
              </div>
              <progress :max="todo + finished" :value="finished" style="vertical-align: none;"></progress>
            </div>
          </div>
        </div>
        <div class="col-md-6" style="text-align: right;">
          <button v-if="commit.revision_hash" v-on:click="submit" class="btn btn-primary">Submit Labels</button>
          <button v-else v-on:click="load" class="btn btn-primary">Load next issue</button>
          <button v-on:click="generate" class="btn btn-primary">sync disagreements</button>
        </div>
      </div>

      <div class="card" v-if="commit.revision_hash">
        <div class="card-header"><i class="fa fa-code"></i> Commit <a :href="'https://github.com/apache/' + commit.project_name + '/commit/' + commit.revision_hash">{{commit.revision_hash}}</a>
        </div>
        <div class="card-block">
<pre>{{commit.message}}</pre>
        </div>
      </div>

      <div class="card" v-if="commit.revision_hash">
        <div class="card-header"><i class="fa fa-tags"></i> Label
        </div>
        <div class="card-block">
          <table>
            <tr>
              <th>Resolution</th>
              <th>Label1</th>
              <th>Label2</th>
            </tr>
            <tr>
              <td>
                <input type="checkbox" v-model="commit.is_perfective" name="is_perfective"/> increases quality<br/>
                <input type="checkbox" v-model="commit.is_corrective" name="is_corrective"/> fixes a bug
              </td>
              <td>
                <input type="checkbox" v-model="label1.is_perfective" disabled/> increases quality<br/>
                <input type="checkbox" v-model="label1.is_corrective" disabled/> fixes a bug
              </td>
              <td>
                <input type="checkbox" v-model="label2.is_perfective" disabled/> increases quality<br/>
                <input type="checkbox" v-model="label2.is_corrective" disabled/> fixes a bug
              </td>
            </tr>
          </table>
        </div>
      </div>

      <div class="card" v-if="commit.revision_hash && commit.issues.length > 0">
        <div class="card-header"><i class="fa fa-bug"></i> Linked issues
        </div>
        <div class="card-block">
          <div v-for="i in commit.issues">
            <a :href="'https://issues.apache.org/jira/browse/' + i.external_id">{{i.external_id}}</a> [{{i.type}}]
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import rest from '../api/rest'

export default {
  name: 'ChangeTypeDisagreement',
  data () {
    return {
      commit: {},
      label1: {},
      label2: {},
      todo: null,
      finished: null,
      flashes: []
    }
  },
  components: {
  },
  computed: mapGetters({
    loading: 'loading'
  }),
  methods: {
    load() {
      this.loadSample()
    },
    loadSample() {
      this.$store.dispatch('pushLoading')
      this.commit = {}
      rest.getChangeTypeDisagreement()
        .then(response => {
          this.flashes = []
          this.$store.dispatch('popLoading')
          if(response.data['warning'] == 'no_more_issues') {
            this.flashes.push({id: 'no_more_data', message: 'No more labeling necessary. Thank you!'})
            return
          }
          this.commit = response.data
          this.label1 = response.data['label1']
          this.label2 = response.data['label2']
          this.todo = response.data['todo']
          this.finished = response.data['finished']
        })
        .catch(e => {
          this.$store.dispatch('popLoading')
          this.$store.dispatch('pushError', e)
        });
    },
    generate() {
      this.$store.dispatch('pushLoading')
      rest.setChangeTypeDisagreement({action: 'sync'})
        .then(response => {
          this.$store.dispatch('popLoading')
          this.commit = {}
          this.loadSample()
        })
        .catch(e => {
          this.$store.dispatch('popLoading')
          this.$store.dispatch('pushError', e)
        });
    },
    submit() {
      this.$store.dispatch('pushLoading')
      rest.setChangeTypeDisagreement({data: this.commit, action: 'resolve'})
        .then(response => {
          this.$store.dispatch('popLoading')
          this.commit = {}
          this.loadSample()
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
