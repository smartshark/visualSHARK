<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="id != false">
      <Message :id="id"></Message>
    </div>
    <div class="animated fadeIn" v-if="currentMl">
      <div class="card">
        <div class="card-header"><i class="fa fa-envelope"></i> E-Mails from {{ currentMl.name }}</div>
        <div class="card-block">
          <grid :gridColumns="grid.columns" :data="gridMessages.data" :count="gridMessages.count" :defaultPerPage="15" defaultFilterField="" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
            <template slot="subject" slot-scope="props">
              <td>
                <router-link :to="{ name: 'Message', params: { id: props.row.id }}">
                  <template v-if="props.object">
                    {{ props.object }}
                  </template>
                  <template v-else>
                    [no subject]
                  </template>
                </router-link>
              </td>
            </template>
          </grid>
        </div>
      </div>
    </div>
    <div class="animated fadeIn" v-if="!currentMl">
      <alert type="danger" dismissable>
        <span class="icon-info-circled alert-icon-float-left"></span>
        <strong>No Mailinglist selected</strong>
        <p>
          Select a Mailinglist first
        </p>
      </alert>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'

import Grid from '@/components/Grid.vue'
import Message from '@/views/Message.vue'
// import rest from '../api/rest'

export default {
  name: 'messages',
  props: {id: false},
  data () {
    return {
      grid: {
        columns: [
          {ident: 'subject', sortIdent: 'subject', filterIdent: 'subject', name: 'Subject'},
          {ident: 'date', sortIdent: 'date', name: 'Date'}
        ]
      },
      triggerRefresh: false
    }
  },
  components: {
    Grid, alert, Message
  },
  mounted () {
  },
  computed: mapGetters({
    currentMl: 'currentMl',
    gridMessages: 'gridMessages'
  }),
  watch: {
    currentMl (value) {
      if (typeof value.id !== 'undefined') {
        this.triggerRefresh = true
      }
    }
  },
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      dat.filter = dat.filter + '&mailing_list_id=' + this.currentMl.id
      this.$store.dispatch('updateGridMessages', dat)
    }
  }
}
</script>

<style>
</style>
