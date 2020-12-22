<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-code"></i> Labeled commits </div>
        <div class="card-block">
          <grid :gridColumns="grid.columns" :data="gridData.data" :count="gridData.count" :defaultOrder="grid.defaultOrder" :defaultPerPage="15" defaultFilterField="external_id" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
            <template slot="revision_hash" slot-scope="props">
              <td>{{ props.row.revision_hash }}
                </td>
            </template>
            <template slot="is_labeled" slot-scope="props">
              <td>
                <i v-if="props.row.is_labeled" class="fa fa-check"></i>
                <i v-if="!props.row.is_labeled" class="fa fa-times"></i>
              </td>
            </template>
            <template slot="has_technology" slot-scope="props">
              <td>
                <i v-if="props.row.has_technology" class="fa fa-check"></i>
                <i v-if="!props.row.has_technology" class="fa fa-times"></i>
              </td>
            </template>
            <template slot="actions" slot-scope="props">
              <td>
                <router-link :to="{ name: 'Technology Label', params: { loadId: '' + props.row.id}}" class="btn" tag="button" style="cursor: pointer;"> control labels</router-link>
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
import rest from '../api/rest'

import Grid from '@/components/Grid.vue'

export default {
  name: 'TechnologyLabelOverview',
  props: {id: false},
  data () {
    return {
      grid: {
        columns: [
          {ident: 'project_name', sortIdent: 'project_name',  name: 'Project'},
          {ident: 'revision_hash', sortIdent: 'revision_hash',  name: 'Commit'},
          {ident: 'is_labeled', sortIdent: 'is_labeled', filterIdent: 'is_labeled', name: 'IsLabeled'},
          {ident: 'has_technology', sortIdent: 'has_technology', filterIdent: 'has_technology', name: 'HasTechnology'},
          {ident: 'changed_at', sortIdent: 'changed_at', filterIdent: 'changed_at', name: 'Last changed'},
          {ident: 'actions', name: 'Actions'}
        ],
        defaultOrder: {
          field: 'is_labeled',
          type: 1
        }
      },
      triggerRefresh: false
    }
  },
  components: {
    Grid
  },
  computed: {
    ...mapGetters({
      gridData: 'gridTechnologyLabels'
    })
  },
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      this.$store.dispatch('updateGridTechnologyLabels', dat)
    },
    unskip (id) {
      this.$store.dispatch('pushLoading')
      rest.unskipIssue(id)
        .then(response => {
            this.$store.dispatch('popLoading')
            this.triggerRefresh = true
        })
        .catch(e => {
          this.$store.dispatch('popLoading')
          this.$store.dispatch('pushError', e)
        });
    }
  }
}
</script>

<style>
</style>
