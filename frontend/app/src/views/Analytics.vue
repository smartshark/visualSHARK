<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="currentProject && currentVcs">
      <router-view></router-view>
    </div>
    <div class="animated fadeIn" v-if="currentProject && !currentVcs">
      <b-alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No VCS</strong>
        <p>
          No VCS set for Project {{ currentProject.name }}
        </p>
      </b-alert>
    </div>
    <div class="animated fadeIn" v-if="!currentProject">
      <b-alert variant="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No Project Selected</strong>
        <p>
          Select a Project first
        </p>
      </b-alert>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'analytics',
  data () {
    return {
    }
  },
  components: {
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    currentVcs: 'currentVcs'
  })
}
</script>

<style>
</style>
