<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="id && currentCommit.revision_hash">
      <div class="card">
        <div class="card-header">
          Commit {{ currentCommit.revision_hash }}, parents: 
          <template v-for="p in currentCommit.parents">
            <router-link :key="p" :to="{ name: 'Commit', params: { id: p }}">{{ p }}</router-link>&nbsp;
          </template>
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-group"></i> Persons
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Committer</th>
                      <th>Author</th>
                    </tr>
                    <tr>
                      <td v-if="currentCommit.committer"><router-link :to="{ name: 'Person', params: { id: currentCommit.committer.id }}">{{ currentCommit.committer.name }} ({{ currentCommit.committer.email }})</router-link></td>
                      <td v-else>Unknown</td>
                      <td v-if="currentCommit.author"><router-link :to="{ name: 'Person', params: { id: currentCommit.author.id }}">{{ currentCommit.author.name }} ({{ currentCommit.author.email }})</router-link></td>
                      <td v-else>Unknown</td>
                    </tr>
                  </table>
                </div>
              </div>
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-calendar"></i> Dates
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Committer Date</th>
                      <th>Author Date</th>
                    </tr>
                    <tr>
                      <td>{{ currentCommit.committer_date|momentgerman }}</td>
                      <td>{{ currentCommit.author_date|momentgerman }}</td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
            <div class="col-sm-8">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-comment"></i> Message
                </div>
                <div class="card-block" v-html="$options.filters.nl2br(currentCommit.message)"></div>
              </div>
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-bar-chart"></i> Analytics
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Manual Validations</th>
                      <th>Labels</th>
                      <th>Issue links</th>
                      <th>Validated Links</th>
                    </tr>
                    <tr>
                      <td>
                        <ul class="commit-label-list">
                          <li :key="validation" v-for="validation in currentCommit.validations">{{ validation }}</li>
                        </ul>
                      </td>
                      <td>
                        <ul class="commit-label-list">
                          <li :key="label.name" v-for="label in currentCommit.labels">{{ label.name }} : {{ label.value }}</li>
                        </ul>
                      </td>
                      <td>
                        <ul class="commit-link-list">
                          <li :key="il.id" v-for="il in currentCommit.issue_links"><router-link :to="{ name: 'Issue', params: { id: il.id }}">{{ il.name }}</router-link></li>
                        </ul>
                      </td>
                      <td>
                        <ul class="commit-link-list">
                          <li :key="il.id" v-for="il in currentCommit.validated_issue_links"><router-link :to="{ name: 'Issue', params: { id: il.id }}">{{ il.name }}</router-link></li>
                        </ul>
                      </td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="row" v-if="showFA">
            <div class="col-sm-12">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-file"></i> File Actions
                </div>
                <div class="card-block">
                  <grid :gridColumns="gridFA.columns" :data="gridFileActions.data" :count="gridFileActions.count" :defaultPerPage="5" defaultFilterField="" :triggerRefresh="triggerRefreshFA" @refresh="refreshGridFA">
                    <template slot="file" slot-scope="props">
                      <td>{{ props.object.path }}</td>
                    </template>
                  </grid>
                </div>
              </div>
            </div>
          </div>
          <div class="row" v-if="showCES">
            <div class="col-sm-12">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-code"></i> Code Entity States for this Commit
                </div>
                <div class="card-block">
                  <grid :gridColumns="gridCES.columns" :data="gridCodeEntityStates.data" :count="gridCodeEntityStates.count" :defaultPerPage="5" defaultFilterField="long_name" :triggerRefresh="triggerRefreshCES" @refresh="refreshGridCES">
                  </grid>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import Grid from '@/components/Grid.vue'

export default {
  name: 'singlecommit',
  props: {id: false, showFA: true, showCES: true},  // eslint-disable-line vue/require-prop-type-constructor
  data () {
    return {
      gridFA: {
        columns: [
          {ident: 'file', name: 'File'},
          {ident: 'mode', sortIdent: 'mode', name: 'Mode'},
          {ident: 'induced_by', name: 'Induced by'},
          {ident: 'size_at_commit', name: 'Size'},
          {ident: 'lines_added', sortIdent: 'lines_added', name: 'Added'},
          {ident: 'lines_deleted', sortIdent: 'lines_deleted', name: 'Deleted'}
        ]
      },
      gridCES: {
        columns: [
          {ident: 'long_name', filterIdent: 'long_name', name: 'Long Name'},
          {ident: 'ce_type', sortIdent: 'ce_type', name: 'Type'},
          {ident: 'start_line', name: 'Start Line'},
          {ident: 'end_line', name: 'End Line'},
          {ident: 'metrics', name: 'Metrics'}
        ]
      },
      triggerRefreshFA: false,
      triggerRefreshCES: false,
      runPlugin: null,
      commitPlugins: [{'id': 1, 'name': 'coastSHARK'}, {'id': 12, 'name': 'mecoSHARK'}]
    }
  },
  components: {
    Grid
  },
  mounted () {
    if (this.id !== false && typeof this.id !== 'undefined') {
      this.getCommit(this.id)
    }
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    currentVcs: 'currentVcs',
    currentCommit: 'currentCommit',
    gridFileActions: 'gridFileActions',
    gridCodeEntityStates: 'gridCodeEntityStates',
    currentCommitAnalytics: 'currentCommitAnalytics',
    gridDefectLinks: 'gridDefectLinks',
    isSuperuser: 'isSuperuser'
  }),
  watch: {
    gridDefectLinks (value) {
      console.log('getting defects')
      console.log(value)
    },
    currentProject () {
      this.id = false  // eslint-disable-line vue/no-mutating-props
    },
    id (value) {
      if (value !== false && typeof value !== 'undefined') {
        this.getCommit(value)
      }
    },
    currentCommit (value) {
      if (value !== null && typeof value !== 'undefined') {
        if (this.showFA) {
          this.triggerRefreshFA = true
        }

        if (this.showCES) {
          this.triggerRefreshCES = true
        }
      }
    }
  },
  methods: {
    getCommit (id) {  // eslint-disable-line no-unused-vars
      this.$store.dispatch('getCommit', {vcsSystemId: this.currentVcs.id, revisionHash: this.id})
    },
    refreshGridFA (dat) {
      this.triggerRefreshFA = false
      dat.filter = dat.filter + '&commit_id=' + this.currentCommit.commit_id
      this.$store.dispatch('updateGridFileActions', dat)
    },
    refreshGridCES (dat) {
      this.triggerRefreshCES = false
      dat.filter = dat.filter + '&commit_id=' + this.currentCommit.commit_id
      this.$store.dispatch('updateGridCodeEntityStates', dat)
    }
  }
}
</script>

<style>
.commit-label-list, .commit-link-list {
    list-style-type: none;
    margin: 0px;
    padding: 0px;
}

.btn-override {
  width: auto !important;
  padding: 0.5rem 1rem !important;
  border: 1px solid transparent !important;
  border-color: #20a8d8 !important;
  background-color: #20a8d8 !important;
  color: white !important;
}

.btn-override:hover {
  background-color: #2192ba !important;
}
</style>
