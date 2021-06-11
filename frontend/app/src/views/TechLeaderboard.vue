<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header">
          <i class="fa fa-crown"></i> Leaderboard <span class="updated">{{last_updated}}</span>
        </div>
        <div class="card-block">
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Commits</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, key, index) in board" :key="key + index">
                <td>{{item.user}}</td>
                <td>{{item.commits}}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <i class="fa fa-tasks"></i> Projects <span class="updated">{{last_updated}}</span>
        </div>
        <div class="card-block">
          <table>
            <thead>
              <tr>
                <th>Project</th>
                <th>Commits completed</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, key, index) in projects" :key="key + index">
                <template>
                  <td>{{key}}</td>
                  <td class="td-number">{{item.commits}}</td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import rest from '../api/rest'

export default {
  name: 'techleaderboard',
  data () {
    return {
      board: {},
      projects: {},
      onlyProjects: [],
      last_updated: ''
    }
  },
  components: {
  },
  mounted() {
    this.$store.dispatch('pushLoading')
    rest.getTechLeaderboard()
    .then(response => {
      this.last_updated = response.data['last_updated']
      // change structure of leaderboard for sorting
      let leaderboard = []
      for(let user in response.data['users']) {
        leaderboard.push({user: user, commits: response.data['users'][user].commits})
      }

      this.board = leaderboard.sort((a, b) => (a.commits < b.commits) ? 1 : -1)
      this.projects = response.data['projects']
      this.$store.dispatch('popLoading')
    })
    .catch(e => {
      this.$store.dispatch('pushError', e)
    });
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    projectsVcs: 'projectsVcs',
    projectsIts: 'projectsIts'
  })
}
</script>

<style>
.updated {
    font-size: 0.7rem;
    opacity: 0.6;
}
.updated:before {
    content: "last update ";
}
td.td-number {
    text-align: right;
}
</style>
