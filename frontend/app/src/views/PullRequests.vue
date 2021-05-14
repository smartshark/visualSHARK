<template>
  <div class="wrapper">
<div class="animated fadeIn" v-if="id && currentPullRequest.external_id">
      <div class="card">
        <div class="card-header">
          <i class="fa fa-code-fork"></i> PULL-{{ currentPullRequest.external_id }}
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-12">
              <div class="card">
                <div class="card-header">
                  {{ currentPullRequest.title }}
                </div>
                <div class="card-block">
                  <pre>{{ currentPullRequest.description }}</pre>
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-info"></i> Pull Request Information
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>State</th>
                      <td>{{ currentPullRequest.state }}</td>
                    </tr>
                    <tr>
                      <th>Updated</th>
                      <td>{{ currentPullRequest.updated_at }}</td>
                    </tr>
                    <tr>
                      <th>Merged</th>
                      <td>{{ currentPullRequest.merged_at }}</td>
                    </tr>
                    <tr>
                      <th>Labels</th>
                      <td>{{ currentPullRequest.labels }}</td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-comments"></i> Comments
                </div>
                <div class="card-block">
                  <div v-for="comment in currentPullRequest.comments" :key="comment.external_id">
                    <div>{{comment.author.name}} - {{comment.created_at}}</div>
                    <div>{{comment.comment}}</div>
                    <br/>
                  </div>
                </div>
              </div>
            </div>
              <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-bullhorn"></i> Events
                </div>
                <div class="card-block">
                  <div v-for="event in currentPullRequest.events" :key="event.external_id">
                    <div>{{event.author.name}} - {{event.created_at}}</div>
                    <div>{{event.event_type}}</div>
                    <div>{{event.additional_data}}</div>
                    <br/>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-code"></i> Commits
                </div>
                <div class="card-block">
                  <div v-for="commit in currentPullRequest.commits" :key="commit.commit_sha">
                    <div>{{commit.author.name}}</div>
                    <div>{{commit.commit_sha}}</div>
                    <div>{{commit.message}}</div>
                    <br/>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-copy"></i> Files
                </div>
                <div class="card-block">
                  <div v-for="file in currentPullRequest.files" :key="file.path">
                    <div>{{file.path}}</div>
                    <div>{{file.status}}</div>
                    <div>additions: {{file.additions}}, deletions: {{file.deletions}}</div>
                    <br/>
                  </div>
                </div>
              </div>
            </div>
              <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-search"></i> Reviews
                </div>
                <div class="card-block">
                  <div v-for="review in currentPullRequest.reviews" :key="review.external_id">
                    <div>{{review.external_id}} - {{review.state}} - {{review.submitted_at}} - {{review.creator.name}}</div>
                    <div>{{review.description}}</div>
                    <div v-if="review.pull_request_commit">{{review.pull_request_commit.commit_sha}}</div>
                    <div v-else>pull request not linked to commit</div>
                    <br/>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="animated fadeIn" v-if="currentPrs && currentPrs.id">
      <div class="row">
        <div class="col-sm-12">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-code-fork"></i> Pull Requests
            </div>
            <div class="card-block">
              <grid :gridColumns="grid.columns" :data="gridPullRequests.data" :count="gridPullRequests.count" :defaultPerPage="15" defaultFilterField="external_id" :defaultOrder="grid.defaultOrder" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
                <template slot="external_id" slot-scope="props">
                  <td><router-link :to="{ name: 'Pull Requests', params: { id: props.row.id }}">{{ props.object }}</router-link></td>
                </template>
              </grid>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="animated fadeIn" v-if="currentPrs && !currentPrs.id">
      <b-alert show variant="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No Pull Request System</strong>
        <p>
          No Pull Request System set for Project {{ currentProject.name }}
        </p>
      </b-alert>
    </div>
    <div class="animated fadeIn" v-if="!currentPrs">
      <b-alert show variant="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No Pull Request System Selected</strong>
        <p>
          Select a Pull Request System first
        </p>
      </b-alert>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import Grid from '@/components/Grid.vue'

export default {
  name: 'pulls',
  /* eslint-disable vue/require-prop-type-constructor */
  props: {id: false},
  data () {
    return {
      grid: {
        columns: [
          {ident: 'external_id', sortIdent: 'external_id', filterIdent: 'external_id', name: 'ID'},
          {ident: 'title', sortIdent: 'title', filterIdent: 'title', name: 'Title'},
          {ident: 'created_at', sortIdent: 'created_at', name: 'Created'},
          {ident: 'updated_at', sortIdent: 'updated_at', name: 'Updated'},
          {ident: 'merged_at', sortIdent: 'merged_at', name: 'Merged'},
          {ident: 'state', sortIdent: 'state', filterIdent: 'state', name: 'State'}
        ],
        defaultOrder: {
          field: 'updated_at',
          type: -1
        }
      },
      triggerRefresh: false
    }
  },
  components: {
    Grid
  },
  computed: mapGetters({
    gridPullRequests: 'gridPullRequests',
    currentProject: 'currentProject',
    currentPrs: 'currentPrs',
    currentPullRequest: 'currentPullRequest'
  }),
  mounted () {
    if (this.id !== false && typeof this.id !== 'undefined') {
      this.$store.dispatch('getPullRequest', this.id)
    }
  },
  watch: {
    /* eslint-disable no-unused-vars */
    currentProject (value) {
      this.id = false
      this.triggerRefresh = true
    },
    /* eslint-disable no-unused-vars */
    currentPrs (value) {
      this.id = false
      this.triggerRefresh = true
    },
    id (value) {
      if (value !== false && typeof value !== 'undefined') {
        this.$store.dispatch('getPullRequest', value)
      }
    },
    currentPullRequest (value) {
      if (value !== null && typeof value !== 'undefined') {
        //this.gridEventData = value.events
      }
    }
  },
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      if (this.currentPrs !== null && this.currentPrs.id !== null) {
        dat.filter = dat.filter + '&pull_request_system_id=' + this.currentPrs.id
        this.$store.dispatch('updateGridPullRequests', dat)
      }
    }
  }
}
</script>
<style>
</style>
