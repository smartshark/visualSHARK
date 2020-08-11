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
                <th>Lines</th>
                <th>Files</th>
                <th>Commits</th>
                <th>Issues</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, key, index) in board">
                <td>{{item.user}}</td>
                <td>{{item.lines}}</td>
                <td>{{item.files}}</td>
                <td>{{item.commits}}</td>
                <td>{{item.issues}}</td>
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
                <th></th>
                <th></th>
                <th colspan="3" style="text-align: center;">Issues partially completed</th>
                <th></th>
              </tr>
              <tr>
                <th>Project</th>
                <th>Issues needed</th>
                <th>1 participant</th>
                <th>2 participants</th>
                <th>3 participants</th>
                <th>Issues completed</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, key, index) in projects">
                <td>{{key}}</td>
                <td class="td-number">{{item.need_issues}}</td>
                <td class="td-number">{{item.partial_1}}</td>
                <td class="td-number">{{item.partial_2}}</td>
                <td class="td-number">{{item.partial_3}}</td>
                <td class="td-number">{{item.finished}}</td>
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
import { alert } from 'vue-strap'
import rest from '../api/rest'

export default {
  name: 'leaderboard',
  data () {
    return {
      board: {},
      projects: {},
      last_updated: ''
    }
  },
  components: {
    alert
  },
  mounted() {
    this.$store.dispatch('pushLoading')
    rest.getLeaderboard()
    .then(response => {
      this.last_updated = response.data['last_updated']
      
      // change structure of leaderboard for sorting
      let leaderboard = []
      for(let user in response.data['board']) {
        leaderboard.push({user: user, lines: response.data['board'][user].lines, commits: response.data['board'][user].commits, issues: response.data['board'][user].issues, files: response.data['board'][user].files})
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
