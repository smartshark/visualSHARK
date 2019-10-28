<template>
  <div id="loginScreen" class="app flex-row align-items-center">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-4">
          <div class="card-group mb-0">
            <div class="card p-2">
              <div class="card-block">
                <h4>visualSHARK {{ version }}</h4>
                <template v-if="loginMessage !== ''">
                  <p class="text-muted" v-if="loginMessage !== ''">{{loginMessage}}</p>
                </template>
                <template v-else>
                  <p class="text-muted" v-if="logout">Logout Successful</p>
                  <p class="text-muted" v-else>Sign In to your account</p>
                </template>
                <div class="input-group mb-1" :class="{'has-danger': loginMessage !== ''}">
                  <span class="input-group-addon"><i class="icon-user"></i></span>
                  <input type="text" class="form-control" placeholder="Username" v-model="user" :class="{'form-control-danger': loginMessage !== ''}" @keypress.enter="login">
                </div>
                <div class="input-group mb-2" :class="{'has-danger': loginMessage !== ''}">
                  <span class="input-group-addon"><i class="icon-lock"></i></span>
                  <input type="password" class="form-control" placeholder="Password" v-model="pass" :class="{'form-control-danger': loginMessage !== ''}" @keypress.enter="login">
                </div>
                <div class="row">
                  <div class="col-6">
                    <button type="button" class="btn btn-primary px-2" @click="login">Login</button>
                  </div>
                  <div class="col-6 text-right">
                    <!--<button type="button" class="btn btn-link px-0">Forgot password?</button>-->
                  </div>
                </div>
              </div>
            </div><!--
            <div class="card card-inverse card-primary py-3 hidden-md-down" style="width:44%">
              <div class="card-block text-center">
                <div>
                  <h2>Sign up</h2>
                  <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                  <button type="button" class="btn btn-primary active mt-1">Register Now!</button>
                </div>
              </div>
            </div>-->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import { version } from '../../package.json'

export default {
  name: 'Login',
  props: {logout: false},
  data () {
    return {user: '', pass: '', version: ''}
  },
  methods: {
    login () {
      this.$store.dispatch('login', {user: this.user, pass: this.pass})
      // we can not do this here because router will replace the route before we can return the token
      // this.$router.replace('/')
    },
    loginImage () {
      let maximum = 2
      let minimum = 1
      let i = Math.floor(Math.random() * (maximum - minimum + 1)) + minimum
      return 'llogin-llama' + i
    }
  },
  mounted () {
    document.getElementById('loginScreen').className += ' ' + this.loginImage()
  },
  created () {
    this.version = version
    if (this.logout === true) {
      this.$store.dispatch('logout')
    }
  },
  computed: mapGetters({
    loginSuccess: 'loginSuccess',
    loginMessage: 'loginMessage'
  }),
  watch: {
    loginSuccess (value) {
      if (value === true) {
        this.$router.replace('/')
      }
    },
    loginMessage (value) {
      console.log('login error', value)
    }
  }
}
</script>

<style>
.llogin-llama1 {
  background-image: url('../assets/llogin_llama1.jpg');
  background-size: cover;
}
.llogin-llama2 {
  background-image: url('../assets/llogin_llama2.jpg');
  background-size: cover;
}
</style>
