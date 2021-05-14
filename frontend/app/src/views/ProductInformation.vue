<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-tags"></i> Product Information for {{currentProject.name}}</div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-12 col-md-6">
              <div class="card">
                <div class="card-header">Collected Products</div>
                <div class="card-block">
                  <ul v-if="products">
                    <li v-for="v in products.data"><a href="javascript:void(0)" @click="getProduct(v)" title="show information">{{ v.name }} ({{ v.last_updated|momentgerman }})</a> <a href="javascript:void(0)" @click="downloadProduct(v)" title="download json file"><i class="fa fa-download"></i></a></li>
                  </ul>
                </div>
              </div>
              <div class="card">
                <div class="card-header">Metrics</div>
                <div class="card-block">
                  <grid :gridColumns="gridProd.columns" :data="gridData" :count="gridDataCount" :defaultPerPage="15" defaultFilterField="metric" :triggerRefresh="triggerRefreshProd" @refresh="refreshGridProd"></grid>
                </div>
              </div>
            </div>
            <div class="col-sm-12 col-md-6">
              <div class="card">
                <div class="card-header">Information
                  <template v-if="currentProduct"> about {{ currentProduct.name }}
                    <div v-if="isSuperuser" class="card-actions">
                      <dropdown class="inline">
                        <span slot="button">
                          <i class="fa fa-gear"></i>
                        </span>
                        <div slot="dropdown-menu" class="dropdown-menu dropdown-menu-right">
                          <div class="dropdown-header text-center"><strong>Re-Mine dataset</strong></div>
                          <div class="input-group" style="width: 600px">
                            <select v-model="runPlugin" class="form-control">
                              <option v-for="item in datasetPlugins" :value="item.name">{{ item.name }}</option>
                            </select>
                            <div class="input-group-btn"><button type="button" class="btn btn-primary btn-override" @click="schedulePlugin()"><i class="fa fa-clock-o"></i> schedule plugin
                            </button></div>
                          </div>
                        </div>
                      </dropdown>
                    </div>
                  </template>
                </div>
                <div class="card-block" id="canvascontainer">
                  <canvas id="versionchart" height="300">
                  </canvas>
                  <FilePathInformation :release="currentProductData"></FilePathInformation>
                </div>
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

import rest from '../api/rest'

import Grid from '@/components/Grid.vue'
import FilePathInformation from '@/components/FilePathInformation'

import Chart from 'chart.js'

export default {
  name: 'versionfilter',
  data () {
    return {
      chart: null,
      currentProduct: null,
      currentProductData: null,
      currentProductComplete: null,
      currentProductMetrics: [],
      runPlugin: null,
      datasetPlugins: [{'name': 'mynbouSHARK'}],
      gridDataCount: 0,
      gridData: [],
      gridProd: {
        columns: [
          {ident: 'metric', sortIdent: 'metric', filterIdent: 'metric', name: 'Metric'}
        ]
      },
      triggerRefreshProd: false
    }
  },
  components: {
    FilePathInformation, Grid
  },
  mounted () {
    this.$store.dispatch('getProducts', {filter: '&vcs_system_id=' + this.currentVcs.id, order: 'name'})
  },
  computed: mapGetters({
    currentVcs: 'currentVcs',
    currentProject: 'currentProject',
    products: 'products',
    isSuperuser: 'isSuperuser'
  }),
  watch: {
    currentVcs (value) {
      if (typeof value.id !== 'undefined') {
        this.clearChart()
        this.$store.dispatch('getProducts', {filter: '&vcs_system_id=' + this.currentVcs.id, order: 'name'})
      }
    }
  },
  methods: {
    schedulePlugin () {
      let dat = {plugin_ids: [this.runPlugin], url: this.currentVcs.url, project_mongo_ids: [this.currentProject.id], start_commit: this.currentProductComplete.start_commit, end_commit: this.currentProductComplete.end_commit, path_approach: this.currentProductComplete.label_path_approach, defect_label_name: this.currentProductComplete.defect_link_approach + '_bugfix', metric_approach: this.currentProductComplete.metrics_approach, dataset: this.currentProduct.name, file_ending: this.currentProductComplete.file_ending}
      rest.createOtherJob(dat)
        .then(response => {
          this.$store.dispatch('popLoading')
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    sortMetric (a, b) {
      if (a.metric > b.metric) {
        return -1
      }
      if (a.metric < b.metric) {
        return 1
      }
      return 0
    },
    sort (field, order) {
      if (field === 'metric') {
        this.gridData = this.gridData.sort(this.sortMetric)
      }
      if (order === 'asc') {
        this.gridData = this.gridData.reverse()
      }
    },
    // todo: doublicated code in Prediction.vue
    refreshGridProd (dat) {
      if (this.currentProductMetrics === null) {
        return
      }
      if (dat.search.length > 0) {
        this.gridData = this.currentProductMetrics.filter(item => item.metric.includes(dat.search))
      }

      if (dat.filter.length > 0) {
        let f = dat.filter.split('=')[1]
        this.gridData = this.currentProductMetrics.filter(item => item.metric === f)
      }

      if (dat.filter.length === 0 && dat.search.length === 0) {
        this.gridData = this.currentProductMetrics
      }

      if (dat.order.length > 0) {
        for (let field of dat.order.split(',')) {
          let order = 'desc'
          if (field[0] === '-') {
            field = field.split('-')[1]
            order = 'desc'
          } else {
            order = 'asc'
          }
          this.sort(field, order)
        }
      }
      this.gridData = this.gridData.slice(dat.offset, dat.offset + dat.limit)
    },
    downloadProduct (version) {
      this.$store.dispatch('pushLoading')
      rest.getProductFileDownload(version.id)
        .then(response => {
          this.$store.dispatch('popLoading')

          // this is kind of stupid, but it seems to be the only way
          // save response in blob, create blob url, create A element, link it and click it.
          let blob = new Blob([response.data], { type: 'application/json' })
          let url = window.URL.createObjectURL(blob)
          let link = document.createElementNS('http://www.w3.org/1999/xhtml', 'a')
          link.href = url
          link.download = this.currentProject.name + '-' + version.name + '.json'
          document.body.appendChild(link)
          link.click()
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    getProduct (version) {
      this.clearChart()
      this.currentProduct = version
      this.$store.dispatch('pushLoading')
      rest.getProductFile(version.id)
        .then(response => {
          let data = response.data.instances
          this.currentProductData = data
          this.currentProductComplete = response.data

          this.currentProductMetrics = []
          for (let col of Object.keys(data[1])) {
            this.currentProductMetrics.push({'metric': col})
          }
          this.gridDataCount = this.currentProductMetrics.length
          this.triggerRefreshProd = true

          const types = ['all', 'file_gui', 'file_test', 'file_db', 'file_network', 'file_multithreading', 'file_webservice', 'file_fileio', 'none']

          let datasets = [
            {
              label: 'clean',
              data: [0, 0, 0, 0, 0, 0, 0, 0, 0],
              borderColor: 'rgba(51, 204, 51, 0.7)',
              backgroundColor: 'rgba(51, 204, 51, 0.7)'
            },
            {
              label: 'buggy',
              data: [0, 0, 0, 0, 0, 0, 0, 0, 0],
              borderColor: 'rgba(225, 58, 55, 0.7)',
              backgroundColor: 'rgba(225, 58, 55, 0.7)'
            }
          ]
          for (let row of data) {
            let t = 'none'
            for (let tp of types) {
              // console.log('gui: ', row['gui'])
              if (row[tp] === true) {
                t = types.indexOf(tp)
                //if (row.label === true) {
                if (row.BUGFIX_count > 0) {
                  datasets[1].data[t] += 1
                } else {
                  datasets[0].data[t] += 1
                }
              }
            }
            //if (row.label === true) {
            if (row.BUGFIX_count > 0) {
              datasets[1].data[0] += 1
            } else {
              datasets[0].data[0] += 1
            }
          }
          this.drawChart(datasets, types)
        })
        this.$store.dispatch('popLoading')
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    clearChart () {
      // clear the canvas first
      if (this.chart !== null) {
        this.chart.destroy()
      }
      this.currentProduct = null
      this.currentProductData = null
    },
    drawChart (datasets, types) {
      try {
        let ctx = document.getElementById('versionchart').getContext('2d')
        // eslint-disable-next-line
        this.chart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: types,
            datasets: datasets
          },
          options: {
            scales: {
              yAxes: [{
                stacked: true,
                ticks: {
                  beginAtZero: true
                }
              }],
              xAxes: [{
                stacked: true,
                ticks: {
                  beginAtZero: true
                }
              }]
            }
          }
        })
      } catch (e) {
        console.log(e)
      }
    }
  }
}
</script>

<style>
div.select-label {
  width: 250px;
  line-height: 2rem;
}

.btn-override {
  width: auto !important;
  padding: 0.5rem 1rem !important;
  border: 1px solid transparent !important;
  border-color: #20a8d8 !important;
  background-color: #20a8d8 !important;
  color: white !important;
}

.btn-override:hover {
  background-color: #2192ba !important;
}
</style>
