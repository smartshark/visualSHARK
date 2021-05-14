<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="isSuperuser">
      <router-view></router-view>
    </div>
    <div class="animated fadeIn" v-if="!isSuperuser">
      <b-alert variant="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>Access denied</strong>
        <p>
          no access to system
        </p>
      </b-alert>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'system',
  data () {
    return {
    }
  },
  components: {
  },
  computed: mapGetters({
    isSuperuser: 'isSuperuser'
  })
}
</script>

<style>
</style>
