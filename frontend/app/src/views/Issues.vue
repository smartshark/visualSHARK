<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="id && currentIssue.external_id">
      <div class="card">
        <div class="card-header">
          {{ currentIssue.external_id }}
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-12">
              <div class="card">
                <div class="card-header">
                  {{ currentIssue.title }}
                </div>
                <div class="card-block">
                  {{ currentIssue.desc }}
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-info"></i> Issue Information
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Type</th>
                      <td>{{ currentIssue.issue_type }}</td>
                    </tr>
                    <tr>
                      <th>Priority</th>
                      <td>{{ currentIssue.priority }}</td>
                    </tr>
                    <tr>
                      <th>State</th>
                      <td>{{ currentIssue.status }}</td>
                    </tr>
                    <tr>
                      <th>Resolution</th>
                      <td>{{ currentIssue.resolution }}</td>
                    </tr>
                    <tr>
                      <th>Components</th>
                      <td>{{ currentIssue.components }}</td>
                    </tr>
                    <tr>
                      <th>Labels</th>
                      <td>{{ currentIssue.labels }}</td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-group"></i> People
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Reporter</th>
                      <td v-if="currentIssue.reporter"><router-link :to="{ name: 'Person', params: { id: currentIssue.reporter.id }}">{{ currentIssue.reporter.name }} ({{ currentIssue.reporter.email }})</router-link></td>
                      <td v-else>Not set</td>
                    </tr>
                    <tr>
                      <th>Creator</th>
                      <td v-if="currentIssue.creator"><router-link :to="{ name: 'Person', params: { id: currentIssue.creator.id }}">{{ currentIssue.creator.name }} ({{ currentIssue.creator.email }})</router-link></td>
                      <td v-else>Not set</td>
                    </tr>
                    <tr>
                      <th>Assignee</th>
                      <td v-if="currentIssue.assignee"><router-link :to="{ name: 'Person', params: { id: currentIssue.assignee.id }}">{{ currentIssue.assignee.name }} ({{ currentIssue.assignee.email }})</router-link></td>
                      <td v-else>Not set</td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-tags"></i> Versions
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Affects Versions</th>
                      <td>{{ currentIssue.affects_versions }}</td>
                    </tr>
                    <tr>
                      <th>Fix Versions</th>
                      <td>{{ currentIssue.fix_versions }}</td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="animated fadeIn" v-if="currentIts && currentIts.id">
      <div class="row">
        <div class="col-sm-12">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-bug"></i> Issues
            </div>
            <div class="card-block">
              <grid :gridColumns="grid.columns" :data="gridIssues.data" :count="gridIssues.count" :defaultPerPage="15" defaultFilterField="external_id" :defaultOrder="grid.defaultOrder" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
                <template slot="external_id" slot-scope="props">
                  <td><router-link :to="{ name: 'Issue', params: { id: props.row.id }}">{{ props.object }}</router-link></td>
                </template>
              </grid>
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-sm-6">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-tags"></i> Versions
            </div>
            <div class="card-block">
            </div>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-cubes"></i> Components
            </div>
            <div class="card-block">
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="animated fadeIn" v-if="currentIts && !currentIts.id">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No Issue System</strong>
        <p>
          No Issue System set for Project {{ currentProject.name }}
        </p>
      </alert>
    </div>
    <div class="animated fadeIn" v-if="!currentIts">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No ITS Selected</strong>
        <p>
          Select a ITS first
        </p>
      </alert>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'

import Grid from '@/components/Grid.vue'
import modal from '@/components/Modal'

export default {
  name: 'commits',
  props: {id: false},
  data () {
    return {
      grid: {
        columns: [
          {ident: 'external_id', sortIdent: 'external_id', filterIdent: 'external_id', name: 'ID'},
          {ident: 'title', sortIdent: 'title', filterIdent: 'title', name: 'Title'},
          {ident: 'created_at', sortIdent: 'created_at', name: 'Created'},
          {ident: 'updated_at', sortIdent: 'updated_at', name: 'Updated'},
          {ident: 'status', sortIdent: 'status', filterIdent: 'status', name: 'State'}
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
    Grid, modal, alert
  },
  computed: mapGetters({
    gridIssues: 'gridIssues',
    currentProject: 'currentProject',
    currentIssue: 'currentIssue',
    currentIts: 'currentIts'
  }),
  mounted () {
    if (this.id !== false && typeof this.id !== 'undefined') {
      this.$store.dispatch('getIssue', this.id)
    }
  },
  watch: {
    currentProject (value) {
      this.triggerRefresh = true
    },
    currentIts (value) {
      this.triggerRefresh = true
    },
    id (value) {
      if (value !== false && typeof value !== 'undefined') {
        this.$store.dispatch('getIssue', value)
      }
    },
    currentIssue (value) {
      if (value !== null && typeof value !== 'undefined') {
      }
    }
  },
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      if (this.currentIts !== null && this.currentIts.id !== null) {
        dat.filter = dat.filter + '&issue_system_id=' + this.currentIts.id
        this.$store.dispatch('updateGridIssues', dat)
      }
    }
  }
}
</script>
