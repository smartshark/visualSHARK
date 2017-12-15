<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="currentProject && currentVcs">
      <div class="card">
        <div class="card-header"><i class="fa fa-files-o"></i> Files</div>
        <div class="card-block">
          <grid :gridColumns="grid.columns" :data="gridFiles.data" :count="gridFiles.count" :defaultPerPage="15" defaultFilterField="" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
            <template slot="file" slot-scope="props">
              <td>{{ props.object.path }}</router-link></td>
            </template>
          </grid>
        </div>
      </div>
    </div>
    <div class="animated fadeIn" v-if="currentProject && !currentVcs">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No VCS</strong>
        <p>
          No Issue System set for Project {{ currentProject.name }}
        </p>
      </alert>
    </div>
    <div class="animated fadeIn" v-if="!currentProject">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No Project Selected</strong>
        <p>
          Select a Project first
        </p>
      </alert>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'

import Grid from '@/components/Grid.vue'
// import rest from '../api/rest'

export default {
  name: 'files',
  data () {
    return {
      grid: {
        columns: [
          {ident: 'path', sortIdent: 'path', filterIdent: 'path', name: 'File'}
        ]
      },
      triggerRefresh: false
    }
  },
  components: {
    Grid, alert
  },
  mounted () {
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    currentVcs: 'currentVcs',
    gridFiles: 'gridFiles'
  }),
  watch: {
    currentVcs (value) {
      if (typeof value.id !== 'undefined') {
        this.triggerRefresh = true
      }
    }
  },
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      dat.filter = dat.filter + '&vcs_system_id=' + this.currentVcs.id
      this.$store.dispatch('updateGridFiles', dat)
    }
  }
}
</script>

<style>
</style>
