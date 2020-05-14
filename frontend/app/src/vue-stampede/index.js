import store from '../store'

import Stomp from 'webstomp-client'

export default {
  install (Vue, options) {
    let id = null
    Vue.prototype.$stomp = Stomp.client(options.uri)
    Vue.prototype.$stomp.debug = () => {}
    Vue.prototype.$stomp.connect(options.user, options.pw, con => {
      const channel = store.getters.channel
      if (channel === '') {
        return
      }
      console.log('subscribe to channel ' + channel)
      id = Vue.prototype.$stomp.subscribe('/topic/' + channel, message => {
        const data = JSON.parse(message.body)
        store.dispatch('pushUserMessage', data)
      }, f => {
        // store.dispatch('pushError', {message: 'websocket connection error', detail: f})
        console.log('connection failed', f)
      })
    }, fail => {
      const channel = store.getters.channel
      if (channel === '') {
        return
      }
      // store.dispatch('pushError', {message: 'websocket connection error', detail: fail})
      console.log('connection failed', fail)
    }, '/')

    Vue.discoChannel = function () {
      Vue.prototype.$stomp.unsubscribe(id)
      Vue.prototype.$stomp.disconnect(f => { console.log('disconnected') })
    }

    Vue.connectChannel = function () {
      const channel = store.getters.channel
      Vue.prototype.$stomp.subscribe('/topic/' + channel, message => {
        const data = JSON.parse(message.body)
        store.dispatch('pushUserMessage', data)
      }, f => {
        // store.dispatch('pushError', {message: 'websocket connection error', detail: f})
        console.log('connection failed', f)
      })
    }
  }
}
