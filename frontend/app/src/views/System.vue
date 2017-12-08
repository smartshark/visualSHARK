<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="isSuperuser">
      <router-view></router-view>
    </div>
    <div class="animated fadeIn" v-if="!isSuperuser">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>Access denied</strong>
        <p>
          no access to system
        </p>
      </alert>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'

export default {
  name: 'system',
  data () {
    return {
    }
  },
  components: {
    alert
  },
  computed: mapGetters({
    isSuperuser: 'isSuperuser'
  })
}
</script>

<style>
</style>
