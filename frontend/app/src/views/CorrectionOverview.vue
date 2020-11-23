<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-bug"></i> Issues</div>
        <div class="card-block">
          <grid :gridColumns="grid.columns" :data="gridCorrections.data" :count="gridCorrections.count" :defaultOrder="grid.defaultOrder" :defaultPerPage="15" defaultFilterField="external_id" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
            <template slot="external_id" slot-scope="props">
              <td>{{ props.row.external_id }}
                </td>
            </template>
            <template slot="is_skipped" slot-scope="props">
              <td>
                <i v-if="props.row.is_skipped" class="fa fa-check"></i>
                <i v-if="!props.row.is_skipped" class="fa fa-times"></i>
              </td>
            </template>
            <template slot="is_corrected" slot-scope="props">
              <td>
                <i v-if="props.row.is_corrected" class="fa fa-check"></i>
                <i v-if="!props.row.is_corrected" class="fa fa-times"></i>
              </td>
            </template>
            <template slot="actions" slot-scope="props">
              <td>
                <router-link :to="{ name: 'Change lines control', params: { loadExternalId: props.row.external_id }}"><button class="btn">control labels</button></router-link>
                <router-link :to="{ name: 'Change lines correction', params: { loadExternalId: props.row.external_id }}" v-if="!props.row.is_corrected"><button class="btn btn-primary" style="margin-left: 10px">correct issue</button></router-link>
              </td>
            </template>
          </grid>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import Grid from '@/components/Grid.vue'

export default {
  name: 'CorrectionOverview',
  props: {id: false},
  data () {
    return {
      grid: {
        columns: [
          {ident: 'project_name', sortIdent: 'project_name',  name: 'Project'},
          {ident: 'external_id', sortIdent: 'external_id',  name: 'Issue'},
          {ident: 'is_skipped', sortIdent: 'is_skipped', filterIdent: 'is_skipped', name: 'IsSkipped'},
          {ident: 'is_corrected', sortIdent: 'is_corrected', filterIdent: 'is_corrected', name: 'IsCorrected'},
          {ident: 'actions', name: 'Actions'}
        ],
        defaultOrder: {
          field: 'is_corrected',
          type: 1
        }
      },
      triggerRefresh: false
    }
  },
  components: {
    Grid
  },
  computed: mapGetters({
    gridCorrections: 'gridCorrections'
  }),
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      this.$store.dispatch('updateGridCorrections', dat)
    }
  }
}
</script>

<style>
</style>
