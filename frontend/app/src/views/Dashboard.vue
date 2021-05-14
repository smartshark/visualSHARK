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
                      <template v-if="dashboardStats.num_projects > 0">{{ dashboardStats.num_projects }}</template>
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
                      <template v-if="dashboardStats.num_commits > 0">{{ dashboardStats.num_commits }}</template>
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
                      <template v-if="dashboardStats.num_issues > 0">{{ dashboardStats.num_issues }}</template>
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
                      <template v-if="dashboardStats.num_files > 0">{{ dashboardStats.num_files }}</template>
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
                      <template v-if="dashboardStats.num_emails > 0">{{ dashboardStats.num_emails }}</template>
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
                      <template v-if="dashboardStats.num_people > 0">{{ dashboardStats.num_people }}</template>
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
                            <th>Project</th>
                            <th>Repository</th>
                            <th>Pull Request System</th>
                            <th>Issue Tracking System</th>
                            <th>Mailing List</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="project in projects" :key="project.name">
                            <td>{{ project.name }}</td>
                            <td>
                                <template v-if="project.vcs">
                                <div v-for="vcs in project.vcs" :key="vcs.url">
                                    <i class="fa fa-github"></i> <a :href="vcs.url" target="_blank">{{ vcs.repository_type }}</a><br/>
                                    <span class="updated">{{ vcs.last_updated | momentfromnow }}</span>
                                </div>
                                </template>
                            </td>
                            <td>
                                <template v-if="project.prs">
                                <div v-for="prs in project.prs" :key="prs.url">
                                    <a :href="prs.url" target="_blank">{{prs.url}}</a><br/>
                                    <span class="updated">{{ prs.last_updated | momentfromnow }}</span>
                                </div>
                                </template>
                            </td>
                            <td>
                                <template v-if="project.its">
                                    <div v-for="is in project.its" :key="is.url">
                                    <a :href="is.url" target="_blank">{{ is.url }}</a><br/>
                                    <span class="updated">{{ is.last_updated | momentfromnow }}</span>
                                    <br/>
                                    </div>
                                </template>
                            </td>
                            <td>
                                <template v-if="project.ml.length > 0">
                                    <div v-for="ml in project.ml" :key="ml.name">
                                    <a :href="ml.name" target="_blank">{{ ml.name }}</a><br/>
                                    <span class="updated">{{ ml.last_updated | momentfromnow }}</span>
                                    <br/>
                                    </div>
                                </template>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <modal :show="welcomeModal && showWelcome" @ok="welcomeModal = false" @close="closeModal">
      <div slot="title">
        Welcome to visualSHARK
      </div>
      <div slot="modal-body" class="modal-body">
        This is an overview over all project which are currently in our database.
        Not all of them are part of the labeling experiment due to no manually confirmed issue types und commit->issue links.<br/>
        <br/>
        Every project that is available for the labeling experiment is shown in the right menus drop-down field.
        After closing this dialog you can select the project that you want to label in the dropdown on the right and then click on Changed Lines in the left menu. That takes you directly to the labeling and the issue/commits are then sampled from your selected project.
      </div>
      <div slot="modal-footer" class="modal-footer">
        <input type="checkbox" v-model="neverAgain"/>Do not show this dialog again
      </div>
    </modal>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import moment from 'moment'

import Chart from 'chart.js'

import modal from '@/components/Modal'

export default {
  name: 'dashboard',
  data () {
    return {
      welcomeModal: true,
      neverAgain: false
    }
  },
  components: {
    modal
  },
  computed: {
    ...mapGetters({
    dashboardStats: 'dashboardStats',
    dashboardStatsHistory: 'dashboardStatsHistory',
    projects: 'allProjectData',
    showWelcome: 'showWelcome'
    })
  },
  mounted () {
    // this.$store.dispatch('updateDashboard')
    this.$store.dispatch('updateDashboardStats')
    this.$store.dispatch('updateDashboardStatsHistory')
    // this.drawChart()
    let sw = this.$store.state.showWelcome
    if(sw !== null && typeof sw !== 'undefined') {
      this.neverAgain = !this.$store.state.showWelcome
    }
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
    closeModal() {
      this.welcomeModal = false
      this.$store.dispatch('setShowWelcome', !this.neverAgain)
    },
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
      Object.keys(this.dashboardStats.projects).forEach(key => {
        labels.push(key)
        commits.push(this.dashboardStats.projects[key].commits)
        issues.push(this.dashboardStats.projects[key].issues)
        files.push(this.dashboardStats.projects[key].files)
        emails.push(this.dashboardStats.projects[key].messages)
        people.push(this.dashboardStats.projects[key].people)
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
