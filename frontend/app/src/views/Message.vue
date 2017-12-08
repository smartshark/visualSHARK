<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="id">
      <div class="card">
        <div class="card-header">
          <template v-if="currentMessage.subject">{{ currentMessage.subject }}</template>
          <template v-else>[no subject]</template>
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-group"></i> Persons
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Sender</th>
                      <th>Recipients</th>
                      <th v-if="currentMessage.cc_ids && currentMessage.cc_ids.length > 0">CCs</th>
                    </tr>
                    <tr>
                      <td><router-link v-if="currentMessage.sender" :to="{ name: 'Person', params: { id: currentMessage.sender.id }}">{{ currentMessage.sender.name }} ({{ currentMessage.sender.email }})</router-link></td>
                      <td>
                        <ul>
                            <li v-for="recipient in currentMessage.recipients"><router-link :to="{ name: 'Person', params: { id: recipient.id }}">{{ recipient.name }} ({{ recipient.email }})</router-link></li>
                        </ul>
                      </td>
                      <td v-if="currentMessage.cc_ids && currentMessage.cc_ids.length > 0">
                        <ul>
                            <li v-for="recipient in currentMessage.cc_ids"><router-link :to="{ name: 'Person', params: { id: recipient.id }}">{{ recipient.name }} ({{ recipient.email }})</router-link></li>
                        </ul>
                      </td>
                    </tr>
                  </table>
                </div>
              </div>
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-calendar"></i> Dates
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Date</th>
                    </tr>
                    <tr>
                      <td><template v-if="currentMessage.date">{{ currentMessage.date|momentgerman }}</template></td>
                    </tr>
                  </table>
                </div>
              </div>
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-envelope-o"></i> Thread Information
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>In reply</th>
                    </tr>
                    <tr>
                      <td>
                        <router-link v-if="currentMessage.in_reply_to_id" :to="{ name: 'Message', params: { id: currentMessage.in_reply_to_id.id }}">{{ currentMessage.in_reply_to_id.subject }}</router-link>
                      </td>
                    </tr>
                  </table>
                  <table class="table">
                    <tr>
                      <th>References</th>
                    </tr>
                    <tr>
                      <td>
                        <ul>
                          <li v-for="ref in currentMessage.reference_ids">
                            <router-link :to="{ name: 'Message', params: { id: ref.id }}">{{ ref.subject }}</router-link>
                          </li>
                        </ul>
                      </td>
                    </tr>
                  </table>
                </div>
              </div>
              <div class="card" v-if="currentMessage.patches.length > 0">
                <div class="card-header">
                  <i class="fa fa-code"></i> Patches
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>Patches</th>
                    </tr>
                    <tr>
                      <td>
                        <ul>
                          <li v-for="patch in currentMessage.patches">
                            {{patch.patch}}
                          </li>
                        </ul>
                      </td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
            <div class="col-sm-8">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-comment"></i> Message
                </div>
                <div class="card-block" v-html="$options.filters.nl2br(currentMessage.body)"></div>
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
  name: 'singlemessage',
  props: {id: false},
  data () {
    return {
    }
  },
  mounted () {
    if (this.id !== false && typeof this.id !== 'undefined') {
      this.getMessage(this.id)
    }
  },
  computed: mapGetters({
    currentMessage: 'currentMessage'
  }),
  watch: {
    currentMl (value) {
      this.id = false
    },
    id (value) {
      if (value !== false && typeof value !== 'undefined') {
        this.getMessage(value)
      }
    }
  },
  methods: {
    getMessage (id) {
      this.$store.dispatch('getMessage', this.id)
    }
  }
}
</script>

<style>
</style>