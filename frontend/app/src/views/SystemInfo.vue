<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-info"></i> System Information</div>
        <div class="card-block">
          Worker connection: {{ conWorker }}<br/>
          serverSHARK connection: {{ conRemote }} <br/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'systeminfo',
  props: {id: false},
  computed: mapGetters({
    conWorker: 'conWorker',
    conRemote: 'conRemote'
  }),
  mounted () {
    this.$store.dispatch('testConnectionWorker', {ping: '1'})
    this.$store.dispatch('testConnectionServershark', {ping: '1'})
  }
}
</script>

<style>
</style>
