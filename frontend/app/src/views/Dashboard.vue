<template>
  <div class="animated fadeIn">
    <div class="row">
        <div class="col-sm-6 col-md-4 col-lg-2">
            <div class="card card-inverse card-info">
                <div class="card-block">
                    <div class="h1 text-muted text-right mb-2">
                        <i class="fa fa-tasks"></i>
                    </div>
                    <div class="h4 mb-0">
                      <template v-if="dashboard.projects > 0">{{ dashboard.projects }}</template>
                      <template v-else>...loading</template>
                    </div>
                    <div class="text-muted text-uppercase font-weight-bold">Projects</div>
                </div>
            </div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
            <div class="card card-inverse card-success">
                <div class="card-block">
                    <div class="h1 text-muted text-right mb-2">
                        <i class="fa fa-code"></i>
                    </div>
                    <div class="h4 mb-0">
                      <template v-if="dashboard.commits > 0">{{ dashboard.commits }}</template>
                      <template v-else>...loading</template>
                    </div>
                    <div class="text-muted text-uppercase font-weight-bold">Commits</div>
                </div>
            </div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
            <div class="card card-inverse card-warning">
                <div class="card-block">
                    <div class="h1 text-muted text-right mb-2">
                        <i class="fa fa-bug"></i>
                    </div>
                    <div class="h4 mb-0">
                      <template v-if="dashboard.issues > 0">{{ dashboard.issues }}</template>
                      <template v-else>...loading</template>
                    </div>
                    <div class="text-muted text-uppercase font-weight-bold">Issues</div>
                </div>
            </div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
            <div class="card card-inverse card-light-orange">
                <div class="card-block">
                    <div class="h1 text-muted text-right mb-2">
                        <i class="fa fa-files-o"></i>
                    </div>
                    <div class="h4 mb-0">
                      <template v-if="dashboard.files > 0">{{ dashboard.files }}</template>
                      <template v-else>...loading</template>
                    </div>
                    <div class="text-muted text-uppercase font-weight-bold">Files</div>
                </div>
            </div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2"> 
            <div class="card card-inverse card-primary">
                <div class="card-block">
                    <div class="h1 text-muted text-right mb-2">
                        <i class="fa fa-envelope"></i>
                    </div>
                    <div class="h4 mb-0">
                      <template v-if="dashboard.emails > 0">{{ dashboard.emails }}</template>
                      <template v-else>...loading</template>
                    </div>
                    <div class="text-muted text-uppercase font-weight-bold">E-Mails</div>
                </div>
            </div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
            <div class="card card-inverse card-danger">
                <div class="card-block">
                    <div class="h1 text-muted text-right mb-2">
                        <i class="fa fa-group"></i>
                    </div>
                    <div class="h4 mb-0">
                      <template v-if="dashboard.people > 0">{{ dashboard.people }}</template>
                      <template v-else>...loading</template>
                    </div>
                    <div class="text-muted text-uppercase font-weight-bold">People</div>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-md-6 col-lg-4">
            <div class="card">
                <div class="card-header">
                    <i class="fa fa-code"></i> Commit distribution
                </div>
                <div class="card-block">
                  <canvas id="chartCommits" height="300">
                  </canvas>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card">
                <div class="card-header">
                    <i class="fa fa-bug"></i> Issue distribution
                </div>
                <div class="card-block">
                  <canvas id="chartIssues" height="300">
                  </canvas>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card">
                <div class="card-header">
                    <i class="fa fa-copy"></i> File distribution
                </div>
                <div class="card-block">
                  <canvas id="chartFiles" height="300">
                  </canvas>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-md-6 col-lg-4">
            <div class="card">
                <div class="card-header">
                    <i class="fa fa-envelope"></i> E-Mails distribution
                </div>
                <div class="card-block">
                  <canvas id="chartEmails" height="300">
                  </canvas>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card">
                <div class="card-header">
                    <i class="fa fa-group"></i> People distribution
                </div>
                <div class="card-block">
                  <canvas id="chartPeople" height="300">
                  </canvas>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card">
                <div class="card-header">
                    <i class="fa fa-calendar"></i> History
                </div>
                <div class="card-block">
                  <canvas id="chartHistory" height="300">
                  </canvas>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-12">
            <div class="card">
                <div class="card-header">
                    <i class="fa fa-tasks"></i> Projects
                </div>
                <div class="card-block">
                    <table class="table table-striped table-bordered table-condensed">
                        <thead>
                        <tr>
                            <th>Name</th>
                            <th>VCS</th>
                            <th>Issue</th>
                            <th>Mailinglist</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="project in projects">
                            <td>{{ project.name }}</td>
                            <td>
                                <template v-if="project.vcs">
                                <i class="fa fa-github"></i> <a :href="project.vcs.url" target="_blank">{{ project.vcs.repository_type }}</a><br/>
                                <span class="updated">{{ project.vcs.last_updated | momentfromnow }}</span>
                                </template>
                                <template v-else>
                                    no VCS
                                </template>
                            </td>
                            <td>
                                <template v-if="project.iss">
                                    <div v-for="is in project.iss">
                                    <a :href="is.url" target="_blank">{{ is.url }}</a><br/>
                                    <span class="updated">{{ is.last_updated | momentfromnow }}</span>
                                    <br/>
                                    </div>
                                </template>
                                <template v-else>
                                    no Issue System
                                </template>
                            </td>
                            <td>
                                <template v-if="project.ml.length > 0">
                                    <div v-for="ml in project.ml">
                                    <a :href="ml.name" target="_blank">{{ ml.name }}</a><br/>
                                    <span class="updated">{{ ml.last_updated | momentfromnow }}</span>
                                    <br/>
                                    </div>
                                </template>
                                <template v-else>
                                    no Mailing List
                                </template>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import moment from 'moment'

import Chart from 'chart.js'

export default {
  name: 'dashboard',
  computed: mapGetters({
    dashboard: 'dashboard',
    dashboardStats: 'dashboardStats',
    dashboardStatsHistory: 'dashboardStatsHistory',
    projects: 'allProjectData'
  }),
  mounted () {
    this.$store.dispatch('updateDashboard')
    this.$store.dispatch('updateDashboardStats')
    this.$store.dispatch('updateDashboardStatsHistory')
    // this.drawChart()
  },
  watch: {
    dashboardStats () {
      this.drawChart()
    },
    dashboardStatsHistory () {
      this.drawHistoryChart()
    }
  },
  methods: {
    color (seed) {
      return '#' + Math.floor((Math.abs(Math.sin(seed) * 16777215)) % 16777215).toString(16)
    },
    drawHistoryChart () {
      let commits = []
      let issues = []
      let files = []
      let emails = []
      let people = []

      this.dashboardStatsHistory.forEach(item => {
        let date = item['date']
        commits.push({y: item.commits, x: moment(date).toDate()})
        issues.push({y: item.issues, x: moment(date).toDate()})
        files.push({y: item.files, x: moment(date).toDate()})
        emails.push({y: item.messages, x: moment(date).toDate()})
        people.push({y: item.people, x: moment(date).toDate()})
      })
      try {
        let ctx = document.getElementById('chartHistory').getContext('2d')
        let c = new Chart(ctx, { // eslint-disable-line
          type: 'line',
          data: {
            datasets: [{
              label: 'commits',
              data: commits,
              borderColor: 'rgb(77, 189, 116)',
              backgroundColor: 'rgba(77, 189, 116, 0)'
            },
            {
              label: 'issues',
              data: issues,
              borderColor: 'rgb(248, 203, 0)',
              backgroundColor: 'rgba(248, 203, 0, 0)'
            },
            {
              label: 'files',
              data: files,
              borderColor: 'rgb(255, 153, 102)',
              backgroundColor: 'rgba(255, 153, 102, 0)'
            },
            {
              label: 'emails',
              data: emails,
              borderColor: 'rgb(32, 168, 216)',
              backgroundColor: 'rgba(32, 168, 216, 0)'
            },
            {
              label: 'people',
              data: people,
              borderColor: 'rgb(248, 108, 107)',
              backgroundColor: 'rgba(248, 108, 107, 0)'
            }]
          },
          options: {
            scales: {
              xAxes: [{
                display: true,
                position: 'bottom',
                type: 'time',
                time: {
                  unit: 'day'
                }
              }],
              yAxes: [{
                type: 'logarithmic',
                display: true,
                ticks: {
                  min: 0
                }
              }]
            }
          }
        })
      } catch (e) {
        console.log(e)
      }
    },
    drawChart () {
      let backgroundColor = []
      let labels = []
      let commits = []
      let issues = []
      let files = []
      let emails = []
      let people = []
      let i = 1
      Object.keys(this.dashboardStats).forEach(key => {
        labels.push(key)
        commits.push(this.dashboardStats[key].commits)
        issues.push(this.dashboardStats[key].issues)
        files.push(this.dashboardStats[key].files)
        emails.push(this.dashboardStats[key].messages)
        people.push(this.dashboardStats[key].people)
        backgroundColor.push(this.color(i))
        i += 1
      })

      let ctx1 = document.getElementById('chartCommits').getContext('2d')
      let c1 = new Chart(ctx1, { // eslint-disable-line
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [
            {
              data: commits,
              backgroundColor: backgroundColor
            }
          ]
        }
      })
      let ctx2 = document.getElementById('chartIssues').getContext('2d')
      let c2 = new Chart(ctx2, { // eslint-disable-line
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [
            {
              data: issues,
              backgroundColor: backgroundColor
            }
          ]
        }
      })
      let ctx3 = document.getElementById('chartFiles').getContext('2d')
      let c3 = new Chart(ctx3, { // eslint-disable-line
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [
            {
              data: files,
              backgroundColor: backgroundColor
            }
          ]
        }
      })
      let ctx4 = document.getElementById('chartEmails').getContext('2d')
      let c4 = new Chart(ctx4, { // eslint-disable-line
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [
            {
              data: emails,
              backgroundColor: backgroundColor
            }
          ]
        }
      })
      let ctx5 = document.getElementById('chartPeople').getContext('2d')
      let c5 = new Chart(ctx5, { // eslint-disable-line
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [
            {
              data: people,
              backgroundColor: backgroundColor
            }
          ]
        }
      })
    }
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
.card-light-orange {
    background-color: #ff9966 !important;
}
</style>
