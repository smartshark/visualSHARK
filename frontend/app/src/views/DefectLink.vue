<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header">
          <i class="fa fa-link"></i> Current Commit {{ commit.revision_hash }}, parents: 
          <template v-for="p in currentCommit.parents">
            {{ p }}&nbsp;
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
                      <td><router-link :to="{ name: 'Person', params: { id: commit.committer.id }}">{{ commit.committer.name }} ({{ commit.committer.email }})</router-link></td>
                      <td><router-link :to="{ name: 'Person', params: { id: commit.author.id }}">{{ commit.author.name }} ({{ commit.author.email }})</router-link></td>
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
                      <td>{{ commit.committer_date|momentgerman }}</td>
                      <td>{{ commit.author_date|momentgerman }}</td>
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
                <div class="card-block" v-html="$options.filters.nl2br(commit.message)"></div>
              </div>
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-bar-chart"></i> Issue Link Candidates
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Issue</th>
                      <th>Type</th>
                      <th>Status</th>
                      <th>Resolution</th>
                      <th>Created</th>
                      <th>Last update</th>
                      <th>Confidence</th>
                    </tr>
                    <tr v-for="c in links">
                      <td v-if="c.issue_id"><router-link :to="{ name: 'Issue', params: { id: c.issue_id }}">{{ c.issue }}</router-link></td>
                      <td v-else>{{c.issue}}</td>
                      <td>{{c.type}}</td>
                      <td>{{c.status}}</td>
                      <td>{{c.resolution}}</td>
                      <td>{{c.created_at|momentgerman}}</td>
                      <td>{{c.updated_at|momentgerman}}</td>
                      <td>{{c.confidence}}<br/>
                        <ul>
                          <li v-for="reason in c.confidence_reasons">{{reason.score}}: {{reason.reason}}</li>
                        </ul>
                      </td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-sm-12 col-md-6">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-file"></i> File Actions
                </div>
                <div class="card-block">
                  <grid :gridColumns="gridFA.columns" :data="gridFileActions.data" :count="gridFileActions.count" :defaultPerPage="5" defaultFilterField="" :triggerRefresh="triggerRefreshFA" @refresh="refreshGridFA">
                    <template slot="file" slot-scope="props">
                      <td><a href="javascript:void(0)" @click="getHunks(props.row.id)">{{ props.object.path }}</a></td>
                    </template>
                  </grid>
                </div>
              </div>
            </div>
            <div class="col-sm-12 col-md-6">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-code"></i> Hunks
                </div>
                <div class="card-block">
                  <grid :gridColumns="gridH.columns" :data="gridHunks.data" :count="gridHunks.count" :defaultPerPage="5" defaultFilterField="" :triggerRefresh="triggerRefreshH" @refresh="refreshGridH">
                    <template slot="content" slot-scope="props">
                      <td><pre>{{props.object}}</pre></td>
                    </template>
                  </grid>
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-sm-12">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-bar-chart"></i> Affected Entities 
                </div>
                <div class="card-block">
                  <table class="table" v-if="entitiesLoaded">
                    <tr>
                      <th>Path</th>
                      <th>Long name</th>
                      <th>Type</th>
                      <th>Content</th>
                    </tr>
                    <tr v-for="e in entities">
                      <td>{{e.path}}</td>
                      <td>{{e.long_name}}</td>
                      <td>{{e.type}}</td>
                      <td v-if="e.type != 'file'">entitiy: {{e.start_line}} - {{e.end_line}}<br/>
                        <template v-for="h in e.hunks">
                          hunk:{{h.hunk_start}} - {{h.hunk_end}}<br/>
                          <pre>{{h.hunk_content}}</pre>
                        </template>
                      </td>
                      <td v-if="e.type == 'file'">
                        <strong>Distance: {{e.pmd_linter_distance}}</strong><br/>
                        <template v-for="l in e.pmd_linter_current">
                          Type: {{l.l_ty}} (Line: {{l.ln}})<br/>
                          {{l.msg}}<br/>
                        </template>
                        --<br/>
                        <template v-for="l in e.pmd_linter_previous">
                          Type: {{l.l_ty}} (Line: {{l.ln}})<br/>
                          {{l.msg}}<br/>
                        </template>
                      </td>
                    </tr>
                  </table>
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
import { dropdown } from 'vue-strap'

import rest from '../api/rest'

import Grid from '@/components/Grid.vue'

export default {
  name: 'defectlinks',
  props: {commit: false},
  data () {
    return {
      fa: null,
      showAffectedEntities: false,
      entitiesLoaded: false,
      links: [],
      entities: [],
      gridFA: {
        columns: [
          {ident: 'file', name: 'File', filterIdent: 'file'},
          {ident: 'mode', sortIdent: 'mode', name: 'Mode'},
          {ident: 'size_at_commit', name: 'Size'},
          {ident: 'lines_added', sortIdent: 'lines_added', name: 'Added'},
          {ident: 'lines_deleted', sortIdent: 'lines_deleted', name: 'Deleted'}
        ]
      },
      triggerRefreshFA: false,
      gridH: {
        columns: [
          {ident: 'content', name: 'Content'},
          {ident: 'new_start', name: 'New Start'},
          {ident: 'new_lines', name: 'New Lines'},
          {ident: 'old_start', name: 'Old Start'},
          {ident: 'old_lines', name: 'Old Lines'}
        ]
      },
      triggerRefreshH: false
    }
  },
  components: {
    Grid, dropdown
  },
  computed: mapGetters({
    currentVcs: 'currentVcs',
    currentCommit: 'currentCommit',
    gridFileActions: 'gridFileActions',
    gridHunks: 'gridHunks',
    currentProject: 'currentProject',
    isSuperuser: 'isSuperuser'
  }),
  watch: {
    currentVcs (value) {
      if (typeof value.id !== 'undefined') {
      }
    }
  },
  mounted () {
    this.getLinks()
    this.clearGrids()
  },
  methods: {
    clearGrids () {
      this.$store.dispatch('clearGridHunks')
      this.$store.dispatch('clearGridFileActions')
    },
    getHunks (fa) {
      this.fa = fa
      this.$store.dispatch('updateGridHunks', {filter: '&file_action_id=' + fa})
      this.getAffectedEntities(fa)
      this.gridH.loading = false
    },
    getAffectedEntities (fa) {
      this.$store.dispatch('pushLoading')
      this.entitiesLoaded = false
      rest.getAffectedEntities(this.commit.commit_id, fa)
        .then(response => {
          this.entities = response.data
          this.$store.dispatch('popLoading')
          this.entitiesLoaded = true
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    getLinks () {
      this.$store.dispatch('pushLoading')
      rest.getIssueLinkCandidates(this.commit.commit_id)
        .then(response => {
          this.links = response.data
          this.$store.dispatch('popLoading')
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    refreshGridFA (dat) {
      this.triggerRefreshFA = false
      // this is undefined on mount
      if (typeof this.commit.commit_id === 'undefined') {
        return
      }
      dat.filter = dat.filter + '&commit_id=' + this.commit.commit_id
      this.$store.dispatch('updateGridFileActions', dat)
    },
    refreshGridH (dat) {
      this.triggerRefreshH = false

      // this is null on mount
      if (this.fa === null) {
        return
      }
      dat.filter = dat.filter + '&file_action_id=' + this.fa
      this.$store.dispatch('updateGridHunks', dat)
    }
  }
}
</script>

<style>
</style>
