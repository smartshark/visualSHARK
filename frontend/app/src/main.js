// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import Vuex from 'vuex'
import moment from 'moment'

import App from './App'
import router from './router'
import store from './store'

import VueProgressBar from 'vue-progressbar'
import VueStomp from './vue-stampede'

Vue.use(VueProgressBar, {
  color: 'rgb(143, 255, 199)',
  failedColor: 'red',
  height: '2px',
  autoFinish: false
})

Vue.filter('nl2br', function (value) {
  const breakTag = '<br/>'
  return (value + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + breakTag + '$2')
})

Vue.filter('momentfromnow', function (date) {
  return moment(date).fromNow()
})
Vue.filter('momentgerman', function (date) {
  return moment(date).format('DD. MMMM YYYY HH:mm:ss')
})

Vue.config.productionTip = false

Vue.use(Vuex)

if (process.env.NODE_ENV === 'development') {
  Vue.use(VueStomp, { uri: process.env.VUE_APP_WS_URL, user: process.env.VUE_APP_WS_USER, pw: process.env.VUE_APP_WS_PW })
}
if (process.env.NODE_ENV === 'production') {
  Vue.use(VueStomp, { uri: process.env.VUE_APP_WS_URL, user: process.env.VUE_APP_WS_USER, pw: process.env.VUE_APP_WS_PW })
}

// register custom fields
// import select2 from '@/components/Select2'
// Vue.component('field-fieldSelect', select2)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  template: '<App/>',
  components: { App }
})
