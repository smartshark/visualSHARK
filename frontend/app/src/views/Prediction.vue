<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header"><i class="fa fa-line-chart"></i> Prediction for {{currentProject.name}}</div>
        <div class="card-block">
          <div class="row">
            <div class="col-sm-12 col-md-4">
              <div class="card">
                <div class="card-header">Training Data</div>
                <div class="card-block">
                  <ul v-if="products">
                    <li v-for="v in products.data" :class="{selected: trainingProducts.indexOf(v.id) !== -1}"><a href="javascript:void(0)" @click="setTraining(v)">{{ v.name }} ({{ v.last_updated|momentgerman }})</a></li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="col-sm-12 col-md-4">
              <div class="card">
                <div class="card-header">Test Data</div>
                <div class="card-block">
                  <ul v-if="products">
                    <li v-for="v in products.data" :class="{selected: testProducts.indexOf(v.id) !== -1}"><a href="javascript:void(0)" @click="setTest(v)">{{ v.name }} ({{ v.last_updated|momentgerman }})</a></li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="col-sm-12 col-md-4">
              <div class="card">
                <div class="card-header">Prediction</div>
                <div class="card-block">
                  <select v-model="predictionModel" class="form-control">
                    <option v-for="item in predictionModels" :value="item">{{ item }}</option>
                  </select>
                  <button @click="predictEvaluate()">predict &amp; evaluate</button>
                  <button @click="predict()">predict</button>
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-sm-12 col-md-12">
              <div class="card">
                <div class="card-header">Prediction &amp; Evaluation Results</div>
                <div class="card-block" id="canvascontainer" style="height: 400px;">
                  <canvas id="predictionResults">
                  </canvas>
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-sm-12 col-md-12">
              <div class="card">
                <div class="card-header">Prediction Results</div>
                <div class="card-block">
                  <grid :gridColumns="gridPred.columns" :data="gridData" :count="gridDataCount" :defaultPerPage="15" defaultFilterField="" :triggerRefresh="triggerRefreshPred" @refresh="refreshGridPred">
                  </grid>
                  <FilePathInformation :release="currentProductData" :options="currentProductDataOptions"></FilePathInformation>
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
  name: 'prediction',
  data () {
    return {
      chart: null,
      trainingProducts: [],
      testProducts: [],
      results: [],
      predictionModel: 'NB',
      predictionModels: ['NB', 'LR'],
      currentProductData: null,
      currentProductDataOptions: {prediction: true},
      gridDataCount: 0,
      gridData: [],
      gridPred: {
        columns: [
          {ident: 'long_name', filterIdent: 'long_name', name: 'File'},
          {ident: 'bugs', sortIdent: 'bugs', name: '#Bugs'},
          {ident: 'label', sortIdent: 'label', name: 'Label'}
        ]
      },
      triggerRefreshPred: false
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
    products: 'products',
    currentProject: 'currentProject'
  }),
  watch: {
    currentVcs (value) {
      if (typeof value.id !== 'undefined') {
        this.$store.dispatch('getProducts', {filter: '&vcs_system_id=' + this.currentVcs.id, order: 'name'})
        this.trainingProducts = []
        this.testProducts = []
      }
    }
  },
  methods: {
    sortBugs (a, b) {
      if (a.bugs > b.bugs) {
        return -1
      }
      if (a.bugs < b.bugs) {
        return 1
      }
      return 0
    },
    sortLabel (a, b) {
      if (a.label === true && b.label === false) {
        return -1
      }
      if (a.label === false && b.label === true) {
        return 1
      }
      return 0
    },
    sort (field, order) {
      if (field === 'bugs') {
        this.gridData = this.gridData.sort(this.sortBugs)
      }
      if (field === 'label') {
        this.gridData = this.gridData.sort(this.sortLabel)
      }
      if (order === 'asc') {
        this.gridData = this.gridData.reverse()
      }
    },
    refreshGridPred (dat) {
      if (this.currentProductData === null) {
        return
      }
      if (dat.search.length > 0) {
        this.gridData = this.currentProductData.filter(item => item.long_name.includes(dat.search))
      } else {
        this.gridData = this.currentProductData
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
    getNumbers (text) {
      let s = ''
      for (let i = 0; i < text.length; i++) {
        s = s + text.charCodeAt(i)
      }
      return s
    },
    color (seed) {
      let col = '#' + Math.floor((Math.abs(Math.sin(seed) * 16777215)) % 16777215).toString(16)
      if (col.length < 7) {
        col = col + '0'
      }
      return col
    },
    getColor (text) {
      return this.color(this.getNumbers(text))
    },
    setTraining (product) {
      if (this.trainingProducts.filter(el => el === product.id).length === 0) {
        this.trainingProducts.push(product.id)
      } else {
        this.trainingProducts = this.trainingProducts.filter(el => el !== product.id)
      }
    },
    setTest (product) {
      if (this.testProducts.filter(el => el === product.id).length === 0) {
        this.testProducts.push(product.id)
      } else {
        this.testProducts = this.testProducts.filter(el => el !== product.id)
      }
    },
    clearChart () {
      if (this.chart !== null) {
        this.chart.destroy()
      }
    },
    drawChart (data) {
      try {
        let ctx = document.getElementById('predictionResults').getContext('2d')
        ctx.canvas.height = 400

        let auc = []
        let prec = []
        let rec = []
        let labels = []
        for (let i = 0; i < this.results.length; i++) {
          auc.push(this.results[i]['auc'])
          prec.push(this.results[i]['precision'])
          rec.push(this.results[i]['recall'])

          labels.push('experiment: ' + this.results[i]['title'])
        }

        let datasets = [
          {
            label: 'AUC',
            data: auc,
            backgroundColor: this.getColor('AUC')
          },
          {
            label: 'Precision',
            data: prec,
            backgroundColor: this.getColor('Precision')
          },
          {
            label: 'Recall',
            data: rec,
            backgroundColor: this.getColor('Recall')
          }
        ]

        // eslint-disable-next-line
        this.chart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: datasets
          },
          options: {
            maintainAspectRatio: false,
            scales: {
              yAxes: [
                {
                  display: true,
                  ticks: {
                    beginAtZero: true,
                    steps: 100,
                    stepValue: 1,
                    max: 1
                  }
                }
              ]
            }
          }
        })
      } catch (e) {
        console.log(e)
      }
    },
    predict () {
      if (this.trainingProducts.length === 0) {
        this.$store.dispatch('pushError', {message: 'Please select at least one training product'})
        return
      }
      if (this.testProducts.length === 0) {
        this.$store.dispatch('pushError', {message: 'Please select at least one test product'})
        return
      }

      this.$store.dispatch('pushLoading')
      rest.predict({ training: this.trainingProducts, test: this.testProducts, model: this.predictionModel })
        .then(response => {
          let data = response.data.product
          this.currentProductData = data
          this.gridData = data.slice(0, 15)
          this.gridDataCount = data.length
          this.$store.dispatch('popLoading')
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    },
    getNames (productIds) {
      let names = []
      for (let i of productIds) {
        for (let p of this.products.data) {
          if (p.id === i) {
            names.push(p.name)
          }
        }
      }
      return names
    },
    predictEvaluate () {
      if (this.trainingProducts.length === 0) {
        this.$store.dispatch('pushError', {message: 'Please select at least one training product'})
        return
      }
      if (this.testProducts.length === 0) {
        this.$store.dispatch('pushError', {message: 'Please select at least one test product'})
        return
      }

      this.$store.dispatch('pushLoading')
      rest.predictEvaluate({ training: this.trainingProducts, test: this.testProducts, model: this.predictionModel })
        .then(response => {
          this.$store.dispatch('popLoading')
          let dat = response.data
          dat.title = this.predictionModel + ', train: ' + this.getNames(this.trainingProducts).join(',') + ', test: ' + this.getNames(this.testProducts).join(',')
          this.results.push(dat)
          this.clearChart()
          this.drawChart(response.data)
        })
        .catch(e => {
          this.$store.dispatch('pushError', e)
        })
    }
  }
}
</script>

<style>
li.selected {
    font-weight: 700;
}
</style>
