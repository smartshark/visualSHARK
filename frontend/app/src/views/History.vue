<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-line-chart"></i> History of {{currentProject.name}}
          <div v-if="isSuperuser" class="card-actions">
            <dropdown class="inline">
              <span slot="button">
                <i class="fa fa-gear"></i>
              </span>
              <div slot="dropdown-menu" class="dropdown-menu dropdown-menu-right">
              <div class="input-group" style="width: 600px">
                <select v-model="currentBranch" class="form-control">
                  <option v-for="item in currentVcsBranches" :value="item.commit_id">{{ item.name }}</option>
                </select>
              </div>
              </div>
            </dropdown>
          </div>
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-12 col-md-8">
              <div class="card">
                <div class="card-header">Size and Complexity</div>
                <div class="card-block">
                </div>
              </div>
            </div>
            <div class="col-sm-12 col-md-8">
              <div class="card">
                <div class="card-header">Issues</div>
                <div class="card-block">
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

export default {
  name: 'history',
  data () {
    return {
      currentBranch: null
    }
  },
  components: {
  },
  mounted () {
    // this.$store.dispatch('getProducts', {filter: '&vcs_system_id=' + this.currentVcs.id, order: 'name'})
  },
  computed: mapGetters({
    currentVcs: 'currentVcs',
    currentProject: 'currentProject',
    currentVcsBranches: 'currentVcsBranches',
    isSuperuser: 'isSuperuser'
  }),
  watch: {
    currentVcs (value) {
    }
  },
  methods: {
  }
}
</script>

<style>
</style>
