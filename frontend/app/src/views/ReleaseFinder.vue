<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-tags"></i> Release finder
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-12 col-md-6">
              <div class="card">
                <div class="card-header">Filtered Releases</div>
                <div class="card-block">
                  Discard qualifiers: <input type="checkbox" v-model="discardQualifiers"/><br/>
                  Discard patch: <input type="checkbox" v-model="discardPatch"/><br/>
                  Discard fliers: <input type="checkbox" v-model="discardFliers"/><br/>
                  <grid :gridColumns="grid.columns" :data="gridReleases.data" :count="gridReleases.count" :defaultPerPage="15" :triggerRefresh="triggerRefresh" @refresh="refreshGrid" :loading="loading">
                    <template slot="revision" slot-scope="props">
                      <td><router-link :to="{ name: 'Commit', params: { id: props.object }}">{{ props.object }}</router-link></td>
                    </template>
                  </grid>
                </div>
              </div>
            </div>
            <div class="col-sm-12 col-md-6">
              <div class="card">
                <div class="card-header">All Tags</div>
                <div class="card-block">
                  <grid :gridColumns="gridT.columns" :data="gridTags.data" :count="gridTags.count" :defaultPerPage="15" defaultFilterField="name" :triggerRefresh="triggerRefreshTags" @refresh="refreshGridTags" :loading="loading">
                    <template slot="commit" slot-scope="props">
                      <td><router-link :to="{ name: 'Commit', params: { id: props.object.revision_hash }}">{{ props.object.revision_hash }}</router-link></td>
                    </template>
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
  name: '',
  data () {
    return {
      grid: {
        columns: [
          {ident: 'revision', name: 'Sha'},
          {ident: 'version', name: 'Filtered Version'},
          {ident: 'qualifier', name: 'Filtered Qualifier'},
          {ident: 'original', name: 'Original Name'}
        ]
      },
      gridT: {
        columns: [
          {ident: 'commit', name: 'Commit'},
          {ident: 'name', sortIdent: 'name', filterIdent: 'name', name: 'Name'},
          {ident: 'date', sortIdent: 'date', name: 'Date'}
        ]
      },
      triggerRefresh: false,
      triggerRefreshTags: false,
      discardPatch: true,
      discardQualifiers: true,
      discardFliers: true
    }
  },
  components: {
    Grid
  },
  mounted () {
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    currentVcs: 'currentVcs',
    gridReleases: 'gridReleases',
    gridTags: 'gridTags',
    loading: 'loading'
  }),
  watch: {
    currentVcs (value) {
      if (typeof value.id !== 'undefined') {
        this.triggerRefresh = true
        this.triggerRefreshTags = true
      }
    },
    discardQualifiers () {
      this.triggerRefresh = true
    },
    discardPatch () {
      this.triggerRefresh = true
    },
    discardFliers () {
      this.triggerRefresh = true
    }
  },
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      dat.filter = dat.filter + '&vcs_system_id=' + this.currentVcs.id + '&discard_qualifiers=' + this.discardQualifiers + '&discard_patch=' + this.discardPatch + '&discard_fliers=' + this.discardFliers
      this.$store.dispatch('updateGridReleases', dat)
    },
    refreshGridTags (dat) {
      this.triggerRefreshTags = false
      dat.filter = dat.filter + '&vcs_system_id=' + this.currentVcs.id
      this.$store.dispatch('updateGridTags', dat)
    }
  }
}
</script>

<style>
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
