<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-link"></i> Current Project {{ currentProject.name }}</div>
        <div class="card-block">
          <div class="row" v-if="currentCommit.commit_id">
            <div class="col-sm-12">
              <DefectLink :commit="currentCommit"></DefectLink>
            </div>
          </div>
          <div class="row">
            <div class="col-sm-12">
              <grid :gridColumns="grid.columns" :data="gridCommits.data" :count="gridCommits.count" :defaultPerPage="15" defaultFilterField="revision_hash" :defaultOrder="grid.defaultOrder" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
                <template slot="revision_hash" slot-scope="props">
                  <td><a href="javascript:void(0)" @click="getCommit(props.object)">{{ props.object }}</a></td>
                </template>
              </grid>
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
import DefectLink from '@/views/DefectLink'

export default {
  name: 'issuelinklist',
  data () {
    return {
      grid: {
        columns: [
          {ident: 'revision_hash', sortIdent: 'revision_hash', filterIdent: 'revision_hash', name: 'Sha'},
          {ident: 'first_message_line', name: 'First Message Line'},
          {ident: 'committer_date', sortIdent: 'committer_date', name: 'Committer Date'}
        ],
        defaultOrder: {
          field: 'committer_date',
          type: -1
        }
      },
      triggerRefresh: false
    }
  },
  components: {
    Grid, DefectLink
  },
  computed: mapGetters({
    currentVcs: 'currentVcs',
    currentCommit: 'currentCommit',
    gridCommits: 'gridCommits',
    currentProject: 'currentProject',
    isSuperuser: 'isSuperuser'
  }),
  watch: {
    currentVcs (value) {
      this.$store.dispatch('clearCurrentCommit')
      this.triggerRefresh = true
    }
  },
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      dat.filter = dat.filter + '&vcs_system_id=' + this.currentVcs.id
      this.$store.dispatch('updateGridCommits', dat)
    },
    getCommit (id) {
      this.$store.dispatch('getCommit', this.currentVcs.id, id)
    }
  }
}
</script>

<style>
</style>
