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
      <b-dropdown size="md" variant="link" toggle-class="text-decoration-none" no-caret dropleft>
        <template #button-content>
          <i class="icon-bell"></i><span :class="{'badge': true, 'badge-pill': true, 'badge-danger': userMessages.length > 0, 'badge-success': userMessages.length == 0}">{{ userMessages.length }}</span>
        </template>
        <b-dropdown-header>Messages</b-dropdown-header>
          <template v-if="userMessages.length > 0" class="msgList">
            <b-dropdown-item v-for="msg in userMessages" :key="msg.msg">
              <a href="javascript:void(0)" @click="ack(msg)" title="acknowledge message"><i class="fa fa-check"></i></a>{{ msg.msg }} <template v-if="msg.success">Success!</template>
            </b-dropdown-item>
          </template>
          <template v-else><b-dropdown-text style="padding: 0.5rem; text-align: center;">No Messages</b-dropdown-text></template>
        </div>
      </b-dropdown>
      <b-dropdown size="md" variant="link" class="nav-item" :text="user" dropleft>
          <b-dropdown-header>Account</b-dropdown-header>
          <b-dropdown-item><router-link :to="'/logout'" class="dropdown-item"><i class="fa fa-lock"></i> Logout</router-link></b-dropdown-item>
        </div>
      </b-dropdown>
      <li class="nav-item hidden-md-down">
        <a class="nav-link navbar-toggler aside-menu-toggler" href="#" @click="asideToggle">&#9776;</a>
      </li>
    </ul>
  </navbar>
</template>
<script>
import { mapGetters } from 'vuex'

import navbar from './Navbar'

import { version } from '../../package.json'

export default {
  name: 'header',
  components: {
    navbar
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
