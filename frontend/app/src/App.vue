<template>
  <div id="app">
    <template v-if="error">
      <alert v-for="err in errors" :key="err.id" placement="top-right" duration="0" type="danger" width="400px" dismissable @input="dismiss(err.id)">
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>Error</strong>
        <p>{{err.message}}</p>
        <p v-if="err.full_error.config">{{err.full_error.config.url}}</p>
      </alert>
    </template>
    <vue-progress-bar :autoFinish="false"></vue-progress-bar>
    <router-view></router-view>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import { alert } from 'vue-strap'

export default {
  name: 'app',
  components: {
    alert
  },
  computed: mapGetters({
    loading: 'loading',
    error: 'error',
    errors: 'errors'
  }),
  watch: {
    loading (value) {
      if (value === true) {
        this.$Progress.start()
      }
      if (value === false) {
        this.$Progress.finish()
      }
    },
    error (value) {
      if (value === true) {
        this.$Progress.fail()
      }
    }
  },
  methods: {
    dismiss (id) {
      this.$store.dispatch('popError', id)
    }
  }
}
</script>

<style>
  /* Import Font Awesome Icons Set */
  $fa-font-path: '~font-awesome/fonts/';
  @import '~font-awesome/css/font-awesome.min.css';
  /* Import Simple Line Icons Set */
  $simple-line-font-path: '~simple-line-icons/fonts/';
  @import '~simple-line-icons/css/simple-line-icons.css';

  /*multiselect css*/
  $fa-font-path: '~@fortawesome/fontawesome-free/fonts';
  @import '~@fortawesome/fontawesome-free/css/all.min.css';
</style>

<style lang="scss">
@import './scss/style';
</style>
