<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="id != false">
      <Commit :id="id" :showFA="true" :showCES="true"></Commit>
    </div>

    <div class="animated fadeIn" v-if="currentVcs && currentVcs.id">
      <div class="row">
        <div class="col-sm-6">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-code"></i> Commits
            </div>
            <div class="card-block">
              <grid :gridColumns="grid.columns" :data="gridCommits.data" :count="gridCommits.count" :defaultPerPage="15" defaultFilterField="revision_hash" :defaultOrder="grid.defaultOrder" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
                <template slot="revision_hash" slot-scope="props">
                  <td><router-link :to="{ name: 'Commit', params: { id: props.object }}">{{ props.object }}</router-link></td>
                </template>
              </grid>
            </div>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-tags"></i> Tags
            </div>
            <div class="card-block">
              <grid :gridColumns="gridT.columns" :data="gridTags.data" :count="gridTags.count" :defaultPerPage="15" defaultFilterField="name" :triggerRefresh="triggerRefreshTags" @refresh="refreshGridTags">
                <template slot="commit" slot-scope="props">
                  <td><router-link :to="{ name: 'Commit', params: { id: props.object.revision_hash }}">{{ props.object.revision_hash }}</router-link></td>
                </template>
              </grid>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="animated fadeIn" v-if="!currentVcs">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No VCS Selected</strong>
        <p>
          Select a VCS first
        </p>
      </alert>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'

import Grid from '@/components/Grid.vue'
import Commit from '@/views/Commit.vue'
import modal from '@/components/Modal'

export default {
  name: 'commits',
  props: {id: false},
  data () {
    return {
      grid: {
        columns: [
          {ident: 'revision_hash', sortIdent: 'revision_hash', filterIdent: 'revision_hash', name: 'Sha'},
          {ident: 'committer_date', sortIdent: 'committer_date', name: 'Committer Date'}
        ],
        defaultOrder: {
          field: 'committer_date',
          type: -1
        }
      },
      gridT: {
        columns: [
          {ident: 'commit', name: 'Commit'},
          {ident: 'name', sortIdent: 'name', filterIdent: 'name', name: 'Name'},
          {ident: 'date', sortIdent: 'date', name: 'Date'}
        ]
      },
      triggerRefresh: false,
      triggerRefreshTags: false
    }
  },
  components: {
    Grid, modal, alert, Commit
  },
  mounted () {
    if (this.id !== false && typeof this.id !== 'undefined') {
      // this.getCommit(this.id)
    }
  },
  computed: mapGetters({
    gridCommits: 'gridCommits',
    gridTags: 'gridTags',
    currentProject: 'currentProject',
    currentCommit: 'currentCommit',
    currentVcs: 'currentVcs'
  }),
  watch: {
    currentProject (value) {
      this.triggerRefresh = true
      this.triggerRefreshTags = true
      this.id = false
    },
    currentVcs (value) {
      this.triggerRefresh = true
      this.triggerRefreshTags = true
      this.id = false
    },
    id (value) {
      if (value !== false && typeof value !== 'undefined') {
        // this.getCommit(value)
      }
    }
  },
  methods: {
    getCommit (id) {
      this.$store.dispatch('getCommit', this.id)
      this.$store.dispatch('getCommitAnalytics', this.id)
    },
    refreshGrid (dat) {
      this.triggerRefresh = false
      dat.filter = dat.filter + '&vcs_system_id=' + this.currentVcs.id
      this.$store.dispatch('updateGridCommits', dat)
    },
    refreshGridTags (dat) {
      this.triggerRefreshTags = false
      dat.filter = dat.filter + '&vcs_system_id=' + this.currentVcs.id
      this.$store.dispatch('updateGridTags', dat)
    }
  }
}
</script>
