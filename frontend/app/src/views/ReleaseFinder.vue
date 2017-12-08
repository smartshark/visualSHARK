<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-tags"></i> Release finder
        <div v-if="isSuperuser" class="card-actions">
          <dropdown class="inline">
            <span slot="button">
              <i class="fa fa-gear"></i>
            </span>
            <div slot="dropdown-menu" class="dropdown-menu dropdown-menu-right">
              <div class="dropdown-header text-center"><strong>Mine dataset</strong></div>
              <div class="input-group" style="width: 600px;">
                <span class="input-group-addon">start commit</span>
                <input type="text" class="form-control" v-model="startCommit">
              </div>
              <div class="input-group" style="width: 600px;">
                <span class="input-group-addon">end commit</span>
                <input type="text" class="form-control" v-model="endCommit">
              </div>
              <div class="input-group" style="width: 600px;">
                <span class="input-group-addon">dataset name</span>
                <input type="text" class="form-control" v-model="dataset">
              </div>
              <div class="input-group" style="width: 600px;">
                <span class="input-group-addon">file ending</span>
                <input type="text" class="form-control" v-model="fileEnding">
              </div>
              <div class="input-group" style="width: 600px;">
                <span class="input-group-addon">defect label name</span>
                <input type="text" class="form-control" v-model="defectLabelName" value="">
              </div>
              <div class="input-group" style="width: 600px;">
                <span class="input-group-addon">label path approach</span>
                <input type="text" class="form-control" v-model="labelPathApproach" value=""><br/>
              </div>
              <div class="input-group" style="width: 600px;">
                <span class="input-group-addon">metric approach</span>
                <input type="text" class="form-control" v-model="metricApproach"><br/>
              </div>
              <div class="input-group" style="width: 600px">
                <select v-model="runPlugin" class="form-control">
                  <option v-for="item in datasetPlugins" :value="item.name">{{ item.name }}</option>
                </select>
                <div class="input-group-btn"><button type="button" class="btn btn-primary btn-override" @click="schedulePlugin()"><i class="fa fa-clock-o"></i> schedule plugin
                </button></div>
              </div>
            </div>
          </dropdown>
        </div>
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-12 col-md-6">
              <div class="card">
                <div class="card-header">Filtered Releases</div>
                <div class="card-block">
                  Discard qualifiers: <input type="checkbox" v-model="discardQualifiers"/><br/>
                  Discard patch: <input type="checkbox" v-model="discardPatch"/><br/>
                  <grid :gridColumns="grid.columns" :data="gridReleases.data" :count="gridReleases.count" :defaultPerPage="15" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
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
  name: '',
  data () {
    return {
      grid: {
        columns: [
          {ident: 'revision', name: 'Sha'},
          {ident: 'version', name: 'Filtered Version'},
          {ident: 'qualifier', name: 'Filtere Qualifier'},
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

      startCommit: null,
      endCommit: null,
      defectLabelName: 'adjustedszz_bugfix',
      labelPathApproach: 'commit_to_commit',
      metricApproach: 'sum_only',
      dataset: null,
      fileEnding: 'java',
      runPlugin: null,
      datasetPlugins: [{'name': 'mynbouSHARK'}]
    }
  },
  components: {
    Grid, dropdown
  },
  mounted () {
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    currentVcs: 'currentVcs',
    gridReleases: 'gridReleases',
    gridTags: 'gridTags',
    isSuperuser: 'isSuperuser'
  }),
  watch: {
    currentVcs (value) {
      if (typeof value.id !== 'undefined') {
        this.triggerRefresh = true
        this.triggerRefreshTags = true
      }
    },
    discardQualifiers (value) {
      this.triggerRefresh = true
    },
    discardPatch (value) {
      this.triggerRefresh = true
    }
  },
  methods: {
    schedulePlugin () {
      let dat = {plugin_ids: [this.runPlugin], url: this.currentVcs.url, project_mongo_ids: [this.currentProject.id], start_commit: this.startCommit, end_commit: this.endCommit, path_approach: this.labelPathApproach, defect_label_name: this.defectLabelName, metric_approach: this.metricApproach, dataset: this.dataset, file_ending: this.fileEnding}
      rest.createOtherJob(dat)
      .then(response => {
        this.$store.dispatch('popLoading')
      })
      .catch(e => {
        this.$store.dispatch('pushError', e)
      })
    },
    refreshGrid (dat) {
      this.triggerRefresh = false
      dat.filter = dat.filter + '&vcs_system_id=' + this.currentVcs.id + '&discard_qualifiers=' + this.discardQualifiers + '&discard_patch=' + this.discardPatch
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
