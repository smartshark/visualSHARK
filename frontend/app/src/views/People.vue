<template>
  <div class="wrapper">
    <div class="animated fadeIn" v-if="id && currentPerson.email">
      <div class="card">
        <div class="card-header">
          <i class="fa fa-user"></i> Person
        </div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-4">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-info"></i> Information
                </div>
                <div class="card-block">
                  <table class="table">
                    <tr>
                      <th>ID</th>
                      <td>{{ currentPerson.id }}</td>
                    </tr>
                    <tr>
                      <th>E-Mail</th>
                      <td>{{ currentPerson.email }}</td>
                    </tr>
                    <tr>
                      <th>Name</th>
                      <td>{{ currentPerson.name }}</td>
                    </tr>
                    <tr>
                      <th>Username</th>
                      <td>{{ currentPerson.username }}</td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
            <div class="col-sm-8">
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-bug"></i> Issues
                </div>
                <div class="card-block">
                  <grid :gridColumns="gridIS.columns" :data="gridIssues.data" :count="gridIssues.count" :defaultPerPage="5" defaultFilterField="subject" :defaultOrder="gridIS.defaultOrder" :triggerRefresh="triggerRefreshIS" @refresh="refreshGridIS">
                    <template slot="external_id" slot-scope="props">
                      <td><router-link :to="{ name: 'Issue', params: { id: props.row.id }}">{{ props.object }}</router-link></td>
                    </template>
                  </grid>
                </div>
              </div>
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-code"></i> Commits
                </div>
                <div class="card-block">
                  <grid :gridColumns="gridC.columns" :data="gridCommits.data" :count="gridCommits.count" :defaultPerPage="5" defaultFilterField="revision_hash" :defaultOrder="gridC.defaultOrder" :triggerRefresh="triggerRefreshC" @refresh="refreshGridC">
                    <template slot="revision_hash" slot-scope="props">
                      <td><router-link :to="{ name: 'Commit', params: { id: props.object }}">{{ props.object }}</router-link></td>
                    </template>
                  </grid>
                </div>
              </div>
              <div class="card">
                <div class="card-header">
                  <i class="fa fa-envelope"></i> Sent messages
                </div>
                <div class="card-block">
                  <grid :gridColumns="gridM.columns" :data="gridMessages.data" :count="gridMessages.count" :defaultPerPage="5" defaultFilterField="revision_hash" :defaultOrder="gridM.defaultOrder" :triggerRefresh="triggerRefreshM" @refresh="refreshGridM">
                    <template slot="subject" slot-scope="props">
                      <td><router-link :to="{ name: 'Message', params: { id: props.row.id }}">{{ props.object }}</router-link></td>
                    </template>
                  </grid>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="animated fadeIn">
      <div class="row">
        <div class="col-sm-12">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-group"></i> People
            </div>
            <div class="card-block">
              <grid :gridColumns="grid.columns" :data="gridPeople.data" :count="gridPeople.count" :defaultPerPage="15" defaultFilterField="name" :defaultOrder="grid.defaultOrder" :triggerRefresh="triggerRefresh" @refresh="refreshGrid">
                <template slot="name" slot-scope="props">
                  <td><router-link :to="{ name: 'Person', params: { id: props.row.id }}">{{ props.object }}</router-link></td>
                </template>
              </grid>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { alert } from 'vue-strap'

import Grid from '@/components/Grid.vue'
import modal from '@/components/Modal'

export default {
  name: 'people',
  props: {id: false},
  data () {
    return {
      grid: {
        columns: [
          {ident: 'name', sortIdent: 'name', filterIdent: 'name', name: 'Name'},
          {ident: 'email', sortIdent: 'email', filterIdent: 'email', name: 'E-Mail'},
          {ident: 'username', sortIdent: 'username', filterIdent: 'username', name: 'Username'}
        ],
        defaultOrder: {
          field: 'name',
          type: -1
        }
      },
      gridIS: {
        columns: [
          {ident: 'external_id', sortIdent: 'external_id', filterIdent: 'external_id', name: 'ID'},
          {ident: 'title', sortIdent: 'title', filterIdent: 'title', name: 'title'},
          {ident: 'created_at', sortIdent: 'created_at', name: 'Created'},
          {ident: 'updated_at', sortIdent: 'updated_at', name: 'Updated'},
          {ident: 'status', sortIdent: 'status', filterIdent: 'status', name: 'State'}
        ],
        defaultOrder: {
          field: 'updated_at',
          type: -1
        }
      },
      gridC: {
        columns: [
          {ident: 'revision_hash', sortIdent: 'revision_hash', filterIdent: 'revision_hash', name: 'Sha'},
          {ident: 'committer_date', sortIdent: 'committer_date', filterIdent: 'committer_date', name: 'Committer Date'}
        ],
        defaultOrder: {
          field: 'committer_date',
          type: -1
        }
      },
      gridM: {
        columns: [
          {ident: 'subject', sortIdent: 'subject', filterIdent: 'subject', name: 'Subject'},
          {ident: 'date', sortIdent: 'date', filterIdent: 'date', name: 'Date'}
        ],
        defaultOrder: {
          field: 'date',
          type: -1
        }
      },
      triggerRefresh: false,
      triggerRefreshIS: false,
      triggerRefreshC: false,
      triggerRefreshM: false
    }
  },
  components: {
    Grid, modal, alert
  },
  mounted () {
    if (this.id !== false && typeof this.id !== 'undefined') {
      this.$store.dispatch('getPerson', this.id)
    }
  },
  computed: mapGetters({
    gridPeople: 'gridPeople',
    gridIssues: 'gridIssues',
    gridCommits: 'gridCommits',
    gridMessages: 'gridMessages',
    currentPerson: 'currentPerson'
  }),
  watch: {
    id (value) {
      console.log('id', value)
      if (value !== false && typeof value !== 'undefined') {
        this.$store.dispatch('getPerson', value)
      }
    },
    currentPerson (value) {
      if (value !== null && typeof value !== 'undefined') {
        this.triggerRefreshIS = true
        this.triggerRefreshC = true
      }
    }
  },
  methods: {
    refreshGrid (dat) {
      this.triggerRefresh = false
      this.$store.dispatch('updateGridPeople', dat)
    },
    refreshGridIS (dat) {
      this.triggerRefreshIS = false
      dat.filter = dat.filter + '&person_id=' + this.currentPerson.id
      this.$store.dispatch('updateGridIssues', dat)
    },
    refreshGridC (dat) {
      this.triggerRefreshC = false
      dat.filter = dat.filter + '&person_id=' + this.currentPerson.id
      this.$store.dispatch('updateGridCommits', dat)
    },
    refreshGridM (dat) {
      this.triggerRefreshM = false
      dat.filter = dat.filter + '&person_id=' + this.currentPerson.id
      this.$store.dispatch('updateGridMessages', dat)
    }
  }
}
</script>
