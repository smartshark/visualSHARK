<template>
  <navbar>
    <button class="navbar-toggler mobile-sidebar-toggler hidden-lg-up" type="button" @click="mobileSidebarToggle">&#9776;</button>
    <a class="navbar-brand" href="/">visualSHARK {{ version }}</a>
    <ul class="nav navbar-nav hidden-md-down">
      <li class="nav-item">
        <a class="nav-link navbar-toggler sidebar-toggler" href="#" @click="sidebarToggle">&#9776;</a>
      </li>
    </ul>
    <ul class="nav navbar-nav ml-auto">
      <dropdown size="nav" class="nav-item">
        <span slot="button">
          <i class="icon-bell"></i><span :class="{'badge': true, 'badge-pill': true, 'badge-danger': userMessages.length > 0, 'badge-success': userMessages.length == 0}">{{ userMessages.length }}</span>
        </span>
        <div slot="dropdown-menu" class="dropdown-menu dropdown-menu-right">
          <div class="dropdown-header text-center"><strong>Messages</strong></div>
          <ul v-if="userMessages.length > 0" class="msgList">
            <li v-for="msg in userMessages">
              <a href="javascript:void(0)" @click="ack(msg)" title="acknowledge message"><i class="fa fa-check"></i></a>{{ msg.msg }} <template v-if="msg.success">Success!</template>
            </li>
          </ul>
          <span v-else><div style="padding: 0.5rem; text-align: center;">No Messages</div></span>
        </div>
      </dropdown>
      <dropdown size="nav" class="nav-item">
        <span slot="button">
          <span class="hidden-md-down">{{ user }}</span>
        </span>
        <div slot="dropdown-menu"class="dropdown-menu dropdown-menu-right">
          <div class="dropdown-header text-center"><strong>Account</strong></div>
          <router-link :to="'/logout'" class="dropdown-item"><i class="fa fa-lock"></i> Logout</router-link>
        </div>
      </dropdown>
      <li class="nav-item hidden-md-down">
        <a class="nav-link navbar-toggler aside-menu-toggler" href="#" @click="asideToggle">&#9776;</a>
      </li>
    </ul>
  </navbar>
</template>
<script>
import { mapGetters } from 'vuex'

import navbar from './Navbar'
import { dropdown } from 'vue-strap'

import { version } from '../../package.json'

export default {
  name: 'header',
  components: {
    navbar,
    dropdown
  },
  methods: {
    click () {
      // do nothing
    },
    ack (msg) {
      // console.log('acking', msg)
      this.$store.dispatch('popUserMessage', msg)
    },
    sidebarToggle (e) {
      e.preventDefault()
      document.body.classList.toggle('sidebar-hidden')
    },
    mobileSidebarToggle (e) {
      e.preventDefault()
      document.body.classList.toggle('sidebar-mobile-show')
    },
    asideToggle (e) {
      e.preventDefault()
      document.body.classList.toggle('aside-menu-hidden')
    }
  },
  computed: {
    ...mapGetters({
      user: 'user',
      userMessages: 'userMessages'
    }),
    version () {
      return version
    }
  }
}
</script>

<style lang="css">

.dropdown-toggle::after {
  /*display: none !important;*/
}

header.navbar .navbar-brand {
  background-image: none !important;
  font-size: 1rem;
  /*padding-top: 0.9rem !important;*/
}

.navbar-brand {
  font-size: 1rem;
  line-height: 2.3rem;
}

ul.msgList {
  list-style-type: none;
  margin: 0px;
  padding: 0.5rem;
}
</style>
