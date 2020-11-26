<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header">
          <i class="fa fa-crown"></i> Correction Board
        </div>
        <div class="card-block">
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Issues</th>
                <th>Skipped</th>
                <th>Corrected</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, key, index) in board.users">
                <td>{{key}}</td>
                <td>{{item.all_issues}}</td>
                <td>{{item.skipped_issues}}</td>
                <td>{{item.corrected_issues}}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td>Sums</td>
                <td>{{board.all_issues}}</td>
                <td>{{board.skipped_issues}}</td>
                <td>{{board.corrected_issues}}</td>
              </tr>
              </tr>
            </tfoot>
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
  name: 'correctionboard',
  data () {
    return {
      board: {}
    }
  },
  components: {
    alert
  },
  mounted() {
    this.$store.dispatch('pushLoading')
    rest.getCorrectionBoard()
    .then(response => {
      this.board = response.data
      this.$store.dispatch('popLoading')
    })
    .catch(e => {
      this.$store.dispatch('popLoading')
      this.$store.dispatch('pushError', e)
    });
  }
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
