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
                <td>{{key}}</td>
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
                <th>Project</th>
                <th>Issues needed</th>
                <th>Issues partially completed</th>
                <th>Issues completed</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, key, index) in projects">
                <td>{{key}}</td>
                <td>{{item.need_issues}}</td>
                <td>{{item.partial}}</td>
                <td>{{item.finished}}</td>
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
      this.$store.dispatch('popLoading')
      this.last_updated = response.data['last_updated']
      this.board = response.data['board']
      this.projects = response.data['projects']
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
</style>
