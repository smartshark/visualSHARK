<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="id != false">
      <Job :id="id"></Job>
    </div>
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-tasks"></i> Jobs</div>
        <div class="card-block">
          <grid :gridColumns="grid.columns" :data="gridJobs.data" :count="gridJobs.count" :defaultOrder="grid.defaultOrder" :defaultPerPage="15" defaultFilterField="" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
            <template slot="job_type" slot-scope="props">
              <td><router-link :to="{ name: 'Job', params: { id: props.row.id }}">{{ props.object.name }}</router-link></td>
            </template>
            <template slot="created_at" slot-scope="props">
              <td>{{ props.object|momentgerman }}</td>
            </template>
            <template slot="executed_at" slot-scope="props">
              <td v-if="props.object">{{ props.object|momentgerman }}</td>
              <td v-else></td>
            </template>
          </grid>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import Job from '@/views/Job.vue'
import Grid from '@/components/Grid.vue'

export default {
  name: 'jobs',
  props: {id: false},
  data () {
    return {
      grid: {
        columns: [
          {ident: 'job_type', sortIdent: 'job_type', filterIdent: 'job_type', name: 'Type'},
          {ident: 'created_at', sortIdent: 'created_at', name: 'Created'},
          {ident: 'executed_at', sortIdent: 'executed_at', name: 'Executed'},
          {ident: 'error_count', sortIdent: 'error_count', name: 'Errors'}
        ],
        defaultOrder: {
          field: 'executed_at',
          type: -1
        }
      },
      triggerRefresh: false
    }
  },
  components: {
    Grid, Job
  },
  computed: mapGetters({
    gridJobs: 'gridJobs'
  }),
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      this.$store.dispatch('updateGridJobs', dat)
    }
  }
}
</script>

<style>
</style>
