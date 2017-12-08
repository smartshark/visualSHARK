<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="id && currentJob && currentJob.job_type">
      <div class="card">
        <div class="card-header">
          Job {{ currentJob.job_type.name }} ({{ id }})
          <div v-if="isSuperuser" class="card-actions">
            <dropdown class="inline">
              <span slot="button">
                <i class="fa fa-gear"></i>
              </span>
              <div slot="dropdown-menu" class="dropdown-menu dropdown-menu-right">
                <div class="dropdown-header text-center"><strong>Re-queue Job</strong></div>
                <div class="input-group" style="width: 600px">
                  <div class="input-group-btn"><button type="button" class="btn btn-primary btn-override" @click="requeueJob()"><i class="fa fa-clock-o"></i> re-queue
                  </button></div>
                </div>
              </div>
            </dropdown>
          </div>
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-6">
              <div class="card">
                <div class="card-header">
                  Data
                </div>
                <div class="card-block">
                  {{ currentJob.data }}
                </div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="card">
                <div class="card-header">
                  Result
                </div>
                <div class="card-block">
                  {{ currentJob.result }}
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
  name: 'singlejob',
  props: {id: false},
  data () {
    return {
    }
  },
  components: {
    Grid, dropdown
  },
  mounted () {
    if (this.id !== false && typeof this.id !== 'undefined') {
      this.getJob(this.id)
    }
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    currentVcs: 'currentVcs',
    currentJob: 'currentJob',
    isSuperuser: 'isSuperuser'
  }),
  watch: {
    currentProject (value) {
      this.id = false
    },
    id (value) {
      if (value !== false && typeof value !== 'undefined') {
        this.getJob(value)
      }
    }
  },
  methods: {
    requeueJob () {
      rest.requeueJob(this.id)
        .then(response => {
          this.$store.dispatch('popLoading')
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    getJob (id) {
      this.$store.dispatch('getJob', this.id)
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